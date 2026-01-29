---
name: bot-update-plus
description: Full backup, update, and restore for Bot - config, workspace, and skills with auto-rollback
version: 2.1.1
metadata: {"bot":{"emoji":"🔄","requires":{"bins":["git","jq","rsync"],"commands":["bot"]}}}
---

# 🔄 Bot Update Plus

A comprehensive backup, update, and restore tool for your entire Bot environment. Protect your config, workspace, and skills with automatic rollback, encrypted backups, and cloud sync.

## Quick Start

```bash
# Check for available updates
bot-update-plus check

# Create a full backup
bot-update-plus backup

# Update everything (creates backup first)
bot-update-plus update

# Preview changes (no modifications)
bot-update-plus update --dry-run

# Restore from backup
bot-update-plus restore bot-update-2026-01-25-12:00:00.tar.gz
```

## Features

| Feature | Description |
|---------|-------------|
| **Full Backup** | Backup entire environment (config, workspace, skills) |
| **Auto Backup** | Creates backup before every update |
| **Auto Rollback** | Reverts to previous commit if update fails |
| **Smart Restore** | Restore everything or specific parts (config, workspace) |
| **Multi-Directory** | Separate prod/dev skills with independent update settings |
| **Encrypted Backups** | Optional GPG encryption |
| **Cloud Sync** | Upload backups to Google Drive, S3, Dropbox via rclone |
| **Notifications** | Get notified via WhatsApp, Telegram, or Discord |
| **Modular Architecture** | Clean, maintainable codebase |

## Installation

```bash
# Via Skills
skills install bot-update-plus --dir ~/.bot/skills

# Or clone manually
git clone https://github.com/hopyky/bot-update-plus.git ~/.bot/skills/bot-update-plus
```

### Add to PATH

Create a symlink to use the command globally:

```bash
mkdir -p ~/bin
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc  # or ~/.bashrc
source ~/.zshrc
ln -sf ~/.bot/skills/bot-update-plus/bin/bot-update-plus ~/bin/bot-update-plus
```

### Dependencies

| Dependency | Required | Purpose |
|------------|----------|---------|
| `git` | Yes | Update skills from repositories |
| `jq` | Yes | Parse JSON configuration |
| `rsync` | Yes | Efficient file copying |
| `rclone` | No | Cloud storage sync |
| `gpg` | No | Backup encryption |

## Configuration

Create `~/.bot/bot-update.json`:

```json
{
  "backup_dir": "~/.bot/backups",
  "backup_before_update": true,
  "backup_count": 5,
  "backup_paths": [
    {"path": "~/.bot", "label": "config", "exclude": ["backups", "logs", "media", "*.lock"]},
    {"path": "~/bot", "label": "workspace", "exclude": ["node_modules", ".venv"]}
  ],
  "skills_dirs": [
    {"path": "~/.bot/skills", "label": "prod", "update": true},
    {"path": "~/bot/skills", "label": "dev", "update": false}
  ],
  "remote_storage": {
    "enabled": false,
    "rclone_remote": "gdrive:",
    "path": "bot-backups"
  },
  "encryption": {
    "enabled": false,
    "gpg_recipient": "your-email@example.com"
  },
  "notifications": {
    "enabled": false,
    "target": "+1234567890",
    "on_success": true,
    "on_error": true
  }
}
```

## Backup Paths

Configure what to backup with `backup_paths`:

| Option | Description |
|--------|-------------|
| `path` | Directory to backup (supports `~`) |
| `label` | Name in logs and restore |
| `exclude` | Files/folders to exclude |

### Recommended Setup

```json
"backup_paths": [
  {"path": "~/.bot", "label": "config", "exclude": ["backups", "logs", "media"]},
  {"path": "~/bot", "label": "workspace", "exclude": ["node_modules", ".venv"]}
]
```

## Skills Update

Configure which skills to update with `skills_dirs`:

| Option | Description |
|--------|-------------|
| `path` | Skills directory |
| `label` | Name in logs |
| `update` | Run `git pull` (true/false) |

### Recommended Setup

```json
"skills_dirs": [
  {"path": "~/.bot/skills", "label": "prod", "update": true},
  {"path": "~/bot/skills", "label": "dev", "update": false}
]
```

- **Prod**: Auto-update from Skills/GitHub
- **Dev**: Manual only (protects your work)

## Commands

### `backup` — Create Full Backup

```bash
bot-update-plus backup
```

### `list-backups` — List Available Backups

```bash
bot-update-plus list-backups
```

### `update` — Update Everything

```bash
# Standard update (with automatic backup)
bot-update-plus update

# Preview changes only
bot-update-plus update --dry-run

# Skip backup
bot-update-plus update --no-backup

# Force continue even if backup fails
bot-update-plus update --force
```

### `restore` — Restore from Backup

```bash
# Restore everything
bot-update-plus restore backup.tar.gz

# Restore only config
bot-update-plus restore backup.tar.gz config

# Restore only workspace
bot-update-plus restore backup.tar.gz workspace

# Force (no confirmation)
bot-update-plus restore backup.tar.gz --force
```

### `check` — Check for Updates

```bash
bot-update-plus check
```

### `install-cron` — Automatic Updates

```bash
# Install daily at 2 AM
bot-update-plus install-cron

# Custom schedule
bot-update-plus install-cron "0 3 * * 0"  # Sundays at 3 AM

# Remove
bot-update-plus uninstall-cron
```

## Notifications

Get notified when updates complete or fail:

```json
"notifications": {
  "enabled": true,
  "target": "+1234567890",
  "on_success": true,
  "on_error": true
}
```

Target format determines channel:
- `+1234567890` → WhatsApp
- `@username` → Telegram
- `channel:123` → Discord

## Cloud Storage

### Setup rclone

```bash
# Install
brew install rclone  # macOS
curl https://rclone.org/install.sh | sudo bash  # Linux

# Configure
rclone config
```

### Enable in Config

```json
"remote_storage": {
  "enabled": true,
  "rclone_remote": "gdrive:",
  "path": "bot-backups"
}
```

## Encrypted Backups

```json
"encryption": {
  "enabled": true,
  "gpg_recipient": "your-email@example.com"
}
```

## Logs

All operations are logged to `~/.bot/backups/update.log`:

```
[2026-01-25 20:22:48] === Update started 2026-01-25 20:22:48 ===
[2026-01-25 20:23:39] Creating backup...
[2026-01-25 20:23:39] Backup created: bot-update-2026-01-25-20:22:48.tar.gz (625M)
[2026-01-25 20:23:39] Bot current version: 2026.1.22
[2026-01-25 20:23:41] Starting skills update
[2026-01-25 20:23:41] === Update completed 2026-01-25 20:23:41 ===
[2026-01-25 20:23:43] Notification sent to +1234567890 via whatsapp
```

**Log retention**: Logs older than 30 days are automatically deleted.

## Retention Policy

| Type | Retention | Config |
|------|-----------|--------|
| Backups (local) | Last N backups | `backup_count: 5` |
| Backups (remote) | Last N backups | Same as local |
| Logs | 30 days | Automatic |

## Architecture (v2.0)

```
bin/
├── bot-update-plus     # Main entry point
└── lib/
    ├── utils.sh             # Logging, helpers
    ├── config.sh            # Configuration
    ├── backup.sh            # Backup functions
    ├── restore.sh           # Restore functions
    ├── update.sh            # Update functions
    ├── notify.sh            # Notifications
    └── cron.sh              # Cron management
```

## Changelog

### v2.0.0
- Complete architecture rewrite
- Modular design (7 separate modules)
- Cleaner codebase (~150 lines per module vs 1000+ monolith)
- Better error handling
- Improved restore with label support
- Auto-detect notification channel from target format
- Fixed `--no-backup` flag being ignored
- Detailed logging to file with auto-purge
- Backup retention policy (local + remote)

### v1.7.0
- Smart restore with label support
- Auto-detect backup format

### v1.6.0
- Added `backup_paths` for full environment backup
- Separated backup logic from update logic

### v1.5.0
- Multi-directory support (`skills_dirs`)

### v1.4.0
- Notifications via Bot messaging

### v1.3.0
- Added `check`, `diff-backups`, `install-cron` commands

## Author

Created by **hopyky**

## License

MIT
