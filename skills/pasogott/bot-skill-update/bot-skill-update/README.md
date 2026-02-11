# Bot Update Skill

Complete **modular** backup, update, and restore workflow for Bot installations.

**Repository**: https://github.com/bot/bot

## Quick Start

```bash
# 0. Dry run (see what would be backed up)
~/.skills/bot-skill-update/backup-bot-dryrun.sh

# 1. Create backup
~/.skills/bot-skill-update/backup-bot-full.sh

# 2. Follow checklist
cat ~/.skills/bot-skill-update/UPDATE_CHECKLIST.md

# 3. Restore if needed
~/.skills/bot-skill-update/restore-bot.sh <backup-dir>
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Complete skill documentation |
| `backup-bot-dryrun.sh` | **Dry run** - preview backup without changes |
| `backup-bot-full.sh` | Full backup script |
| `restore-bot.sh` | Restore from backup |
| `validate-setup.sh` | Validate configuration |
| `check-upstream.sh` | Check for updates |
| `UPDATE_CHECKLIST.md` | Step-by-step update guide |
| `QUICK_REFERENCE.md` | Quick command reference |
| `METADATA.md` | Skill metadata and architecture |

## What Gets Backed Up

- ✅ Configuration (`~/.bot/bot.json`)
- ✅ Sessions state
- ✅ Agent states (multi-agent)
- ✅ Credentials & auth tokens
- ✅ Cron jobs
- ✅ Sandbox states
- ✅ **All agent workspaces (dynamically detected from config!)**
- ✅ Git repository state (commit, branch, remotes)

## Dynamic Workspace Detection

The scripts **automatically discover** all agent workspaces from your config:

```bash
# Reads from config:
.routing.agents.{agentId}.workspace

# Creates backups:
workspace-{agentId}.tar.gz
```

No hardcoded paths! Works with any agent configuration.

## Critical Changes in v2026.1.8

⚠️ **DM Lockdown**: DMs default to `pairing` (was open)  
⚠️ **Groups**: Now allowlists (add `"*"` for allow-all)  
⚠️ **Sandbox**: Default scope is `"agent"` (was `"session"`)  
⚠️ **Timestamps**: UTC format in envelopes  

## Backup Location

```
~/.bot-backups/pre-update-YYYYMMDD-HHMMSS/
├── bot.json
├── sessions.tar.gz
├── agents.tar.gz
├── credentials.tar.gz
├── cron.tar.gz
├── sandboxes.tar.gz
├── workspace-*.tar.gz       # Dynamically detected!
├── git-version.txt
├── git-status.txt
└── BACKUP_INFO.txt
```

## Usage Examples

### Before Major Update

```bash
# Full backup with validation
~/.skills/bot-update/backup-bot-full.sh

# Review what was backed up
ls -lh ~/.bot-backups/pre-update-*/
```

### After Update (if issues)

```bash
# Find latest backup
ls -t ~/.bot-backups/ | head -1

# Restore
~/.skills/bot-update/restore-bot.sh ~/.bot-backups/<dir>
```

### Check Backup Status

```bash
LATEST=$(ls -t ~/.bot-backups/ | head -1)
cat ~/.bot-backups/$LATEST/BACKUP_INFO.txt
```

## Testing After Update

```bash
# New CLI features
pnpm bot agents list
pnpm bot logs --tail 50
pnpm bot providers list --usage

# Web UI
open http://localhost:3001/logs

# Verify routing
# Send messages to your configured providers
```

## Installation

### Via Skills (Recommended)

```bash
# Install from Skills
skills install bot-skill-update

# Make scripts executable (required after Skills install)
chmod +x ~/.skills/bot-skill-update/*.sh
```

### Via Git

```bash
# Clone to your skills directory
git clone https://github.com/pasogott/bot-skill-update.git ~/.skills/bot-skill-update

# Make scripts executable
chmod +x ~/.skills/bot-skill-update/*.sh
```

### Quick Test

```bash
# Test with dry run
~/.skills/bot-skill-update/backup-bot-dryrun.sh
```

## Support

For issues, consult:
1. `UPDATE_CHECKLIST.md` for step-by-step guidance
2. `SKILL.md` for detailed troubleshooting
3. Bot logs: `pnpm bot logs --follow`
4. Run doctor: `pnpm bot doctor`

## License

MIT - see [LICENSE](LICENSE)

## Author

**Pascal Schott** ([@pasogott](https://github.com/pasogott))

Contribution for Bot  
Repository: https://github.com/bot/bot
