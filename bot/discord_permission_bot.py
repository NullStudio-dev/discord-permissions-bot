import discord
from discord.ext import commands
from discord.ui import View, Button
from discord.utils import get
import asyncio
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)

PERMISSIONS = {
    "view_channel": "View Channel",
    "send_messages": "Send Messages",
    "manage_messages": "Manage Messages",
    "embed_links": "Embed Links",
    "attach_files": "Attach Files",
    "read_message_history": "Read Message History",
    "add_reactions": "Add Reactions",
    "mention_everyone": "Mention Everyone",
    "use_external_emojis": "Use External Emojis",
    "connect": "Connect",
    "speak": "Speak",
    "mute_members": "Mute Members",
    "deafen_members": "Deafen Members",
    "move_members": "Move Members",
}

DATA_FILE = "permissions_data.json"
LOG_CHANNEL_ID = 123456789012345678  # replace with your log channel

# Load data if exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        permissions_data = json.load(f)
else:
    permissions_data = {}

# --- Helpers ---
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(permissions_data, f, indent=4)

def auto_correct_channel(guild, name):
    channel = get(guild.channels, name=name)
    if channel:
        return channel
    for c in guild.channels:
        if name.lower() in c.name.lower():
            return c
    return None

# --- On ready ---
@bot.event
async def on_ready():
    print(f"[INFO] Logged in as {bot.user} (ID: {bot.user.id})")
    invite_url = discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(administrator=True))
    print(f"[INFO] Invite URL:\n{invite_url}")

# --- Set permissions command ---
@bot.command()
async def set(ctx, roles: str, *, channels: str):
    role_objs = []
    for r in roles.split(","):
        role = get(ctx.guild.roles, name=r.strip()) or ctx.guild.get_role(int(r.strip().strip("<@&>")))
        if role:
            role_objs.append(role)
    if not role_objs:
        return await ctx.send("[ERROR] No valid roles found.")

    channel_objs = []
    for ch in channels.split(","):
        ch = ch.strip()
        if ch.startswith("<#") and ch.endswith(">"):
            ch_id = int(ch.strip("<#>"))
            channel = get(ctx.guild.channels, id=ch_id)
        else:
            channel = auto_correct_channel(ctx.guild, ch)
        if channel:
            channel_objs.append(channel)
    if not channel_objs:
        return await ctx.send("[ERROR] No valid channels found.")

    # Check hierarchy
    for role in role_objs:
        if ctx.guild.me.top_role <= role:
            return await ctx.send(f"[ERROR] Cannot modify role {role.name}, higher than bot.")

    # Interactive Buttons
    view = View(timeout=180)  # 3 minutes
    selected_perms = {}

    for perm_key, perm_name in PERMISSIONS.items():
        button_true = Button(label=f"{perm_name}: True", style=discord.ButtonStyle.green)
        button_false = Button(label=f"{perm_name}: False", style=discord.ButtonStyle.red)

        async def btn_callback(interaction, key=perm_key, value=True):
            selected_perms[key] = value
            await interaction.response.send_message(f"[INFO] Set {PERMISSIONS[key]} = {value}", ephemeral=True)

        button_true.callback = btn_callback
        button_false.callback = lambda i, key=perm_key: btn_callback(i, key, False)

        view.add_item(button_true)
        view.add_item(button_false)

    await ctx.send(f"[INFO] Choose permissions for roles {[r.name for r in role_objs]}", view=view)
    await view.wait()
    if not selected_perms:
        return await ctx.send("[ERROR] No permissions selected.")

    # Apply permissions
    for role in role_objs:
        for channel in channel_objs:
            try:
                # Save default
                if str(ctx.guild.id) not in permissions_data:
                    permissions_data[str(ctx.guild.id)] = {}
                if str(role.id) not in permissions_data[str(ctx.guild.id)]:
                    permissions_data[str(ctx.guild.id)][str(role.id)] = {}
                if str(channel.id) not in permissions_data[str(ctx.guild.id)][str(role.id)]:
                    permissions_data[str(ctx.guild.id)][str(role.id)][str(channel.id)] = {k: getattr(channel.overwrites_for(role), k, False) for k in PERMISSIONS}
                save_data()

                await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(**selected_perms))
                await ctx.send(f"[SUCCESS] Applied permissions for {role.name} in {channel.name}")
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(f"[INFO] Role {role.name} | Channel {channel.name} | Permissions {selected_perms}")
            except Exception as e:
                await ctx.send(f"[ERROR] Failed to apply permissions for {role.name} in {channel.name}")
                try:
                    await ctx.author.send(f"[EXCEPTION] {e}")
                except:
                    print(f"[EXCEPTION] {e}")

# --- Undo / Reset ---
@bot.command()
async def undo(ctx, roles: str, *, channels: str = None):
    role_objs = []
    for r in roles.split(","):
        role = get(ctx.guild.roles, name=r.strip()) or ctx.guild.get_role(int(r.strip().strip("<@&>")))
        if role:
            role_objs.append(role)
    if not role_objs:
        return await ctx.send("[ERROR] No valid roles found.")

    channel_objs = []
    if channels:
        for ch in channels.split(","):
            ch = ch.strip()
            if ch.startswith("<#") and ch.endswith(">"):
                ch_id = int(ch.strip("<#>"))
                channel = get(ctx.guild.channels, id=ch_id)
            else:
                channel = auto_correct_channel(ctx.guild, ch)
            if channel:
                channel_objs.append(channel)
    else:
        channel_objs = ctx.guild.channels

    for role in role_objs:
        for channel in channel_objs:
            try:
                overwrite_data = permissions_data.get(str(ctx.guild.id), {}).get(str(role.id), {}).get(str(channel.id))
                if overwrite_data:
                    await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(**overwrite_data))
                    await ctx.send(f"[SUCCESS] Reverted permissions for {role.name} in {channel.name}")
            except Exception as e:
                print(f"[ERROR] Failed to revert {role.name} in {channel.name}: {e}")

# --- Template save/apply ---
@bot.command()
async def template_save(ctx, role: discord.Role, name: str):
    guild_id = str(ctx.guild.id)
    if guild_id not in permissions_data:
        return await ctx.send("[ERROR] No permissions data to save.")
    role_data = permissions_data[guild_id].get(str(role.id))
    if not role_data:
        return await ctx.send("[ERROR] No permissions to save for this role.")
    if "templates" not in permissions_data[guild_id]:
        permissions_data[guild_id]["templates"] = {}
    permissions_data[guild_id]["templates"][name] = role_data
    save_data()
    await ctx.send(f"[SUCCESS] Template '{name}' saved for {role.name}")

@bot.command()
async def template_apply(ctx, role: discord.Role, name: str):
    guild_id = str(ctx.guild.id)
    templates = permissions_data.get(guild_id, {}).get("templates", {})
    template = templates.get(name)
    if not template:
        return await ctx.send("[ERROR] Template not found.")
    for channel_id, perms in template.items():
        channel = get(ctx.guild.channels, id=int(channel_id))
        if channel:
            try:
                await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(**perms))
                await ctx.send(f"[SUCCESS] Applied template '{name}' to {role.name} in {channel.name}")
            except Exception as e:
                print(f"[ERROR] Failed to apply template in {channel.name}: {e}")

bot.run("YOUR_BOT_TOKEN")
