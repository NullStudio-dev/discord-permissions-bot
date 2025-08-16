# Discord Permissions Management Bot Documentation

## Overview

This Discord bot simplifies and automates channel permissions management for server roles. It offers interactive commands, logging, templates, and backup support to efficiently manage permissions across multiple roles and channels.

---

## Features

* **Set Command (.set):** Assign permissions to one or multiple roles across channels.
* **Undo Command (.undo):** Revert permissions to default or previously saved states.
* **Template Management:** Save and apply permission templates to roles.
* **Interactive Buttons:** Choose permissions with True/False buttons.
* **Auto-Correct Channels:** Suggest similar channel names for typos.
* **Logging:** Track all permission changes in a specified log channel.
* **Multi-Guild Support:** Store settings per server.
* **JSON Backup/Restore:** Export and import permission settings.
* **Role Hierarchy Check:** Prevents modifying roles above bot's top role.
* **Session Timeout:** Automatically cancels permission selection after 3 minutes.

---

## Commands

### 1. `.set`

**Purpose:** Set permissions for one or multiple roles.

**Usage:**

```
.set -roles @Role1,@Role2 -channels #channel1,#channel2
```

**Features:**

* Supports Text, Voice, Stage, and Category channels.
* Interactive True/False button selection.
* Multiple roles and channels supported.
* Auto-corrects channel names.

**Example:**

```
.set -roles @Member,@Staff -channels #general,#announcements
```

### 2. `.undo`

**Purpose:** Revert permissions to default or previously saved state.

**Usage:**

```
.undo -roles @Role1,@Role2 -channels #channel1,#channel2
```

**Features:**

* Reverts specified channels or all channels if none are provided.
* Uses stored default permissions.

**Example:**

```
.undo -roles @Member -channels #general
```

### 3. `.template save`

**Purpose:** Save current permissions as a template.

**Usage:**

```
.template save @Role TemplateName
```

**Example:**

```
.template save @Staff StaffDefault
```

### 4. `.template apply`

**Purpose:** Apply a saved template to a role.

**Usage:**

```
.template apply @Role TemplateName
```

**Example:**

```
.template apply @Staff StaffDefault
```

---

## Permission Interface

* Buttons represent each permission (Green = True, Red = False).
* Session timeout: 3 minutes.
* Permissions apply to all selected channels and roles.

---

## Logging

* Logs changes in a designated channel.
* Format:

```
[INFO] Role <RoleName> | Channel <ChannelName> | Permissions {permission_dict}
```

* Errors are sent to the user via DM or printed in console.

---

## Backup & Restore

* Permissions stored in `permissions_data.json`.
* Supports export/import for backups or server migration.

---

## Additional Features

* Multi-role & multi-channel support.
* Auto-correct for channel names.
* Role hierarchy safety.
* Interactive True/False selection.
* Timeout and undo/reset capabilities.
* Multi-guild configurations.

---

## Setup Instructions

1. Clone or download the Python bot file.
2. Install dependencies:

```bash
pip install discord.py
```

3. Update `YOUR_BOT_TOKEN` and `LOG_CHANNEL_ID` in the code.
4. Run the bot:

```bash
python discord_permission_bot.py
```

5. Use the printed invite URL to add the bot to your server.

---

## Notes

* Ensure the bot has sufficient permissions or Administrator rights.
* Verify role hierarchy before applying changes.
* Keep JSON backup files secure.

---

This bot provides a robust, interactive, and efficient system for managing Discord server permissions.
