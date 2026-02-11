---
name: bot-skill-update
description: Comprehensive backup, update, and restore workflow with dynamic workspace detection
homepage: https://github.com/pasogott/bot-skill-update
metadata: {"bot":{"emoji":"💾","requires":{"bins":["bash","jq","tar","git"]},"tags":["backup","restore","update","multi-agent"]}}
---

# Bot Update Skill

Comprehensive backup, update, and restore workflow for Bot installations.

## Repository

- **GitHub**: https://github.com/bot/bot
- **Upstream**: `origin/main`
- **Local Clone**: `~/code/bot` (default)

## Description

This skill provides a complete, **modular** update workflow for Bot with **dynamic workspace detection**:
- Configuration files
- Agent states and sessions
- Credentials and auth tokens
- **All agent workspaces (auto-detected from config)**
- Cron jobs and sandboxes
- Git repository state

### Key Features

✅ **Dynamic Workspace Detection** - Reads workspace paths from config  
✅ **Multi-Agent Support** - Handles multiple agents automatically  
✅ **Safe Rollback** - Full restore capability  
✅ **Git Integration** - Tracks versions and remotes  
✅ **Validation** - Pre/post checks included  
✅ **Dry Run** - Preview before backup

## Files

- `config.json` - Skill configuration (repo URLs, paths)
- `backup-bot-dryrun.sh` - **Dry run** preview (no changes)
- `backup-bot-full.sh` - **Dynamic** full backup script
- `restore-bot.sh` - **Dynamic** restore script
- `validate-setup.sh` - Pre/post update validation
- `check-upstream.sh` - Check for available updates
- `UPDATE_CHECKLIST.md` - Step-by-step update checklist
- `QUICK_REFERENCE.md` - Quick command reference
- `SKILL.md` - This file
- `README.md` - Quick start guide

### Dynamic Features

Both backup and restore scripts now:
- Read workspace paths from `~/.bot/bot.json`
- Support any number of agents
- Handle missing workspaces gracefully
- Generate safe filenames from agent IDs

## When to Use

Trigger this skill when asked to:
- "update bot"
- "upgrade to latest version"
- "backup bot before update"
- "restore bot from backup"
- "rollback bot update"

## Usage

### 1. Preview Backup (Dry Run)

```bash
~/.skills/bot-update/backup-bot-dryrun.sh
```

**Shows:**
- What files would be backed up
- Estimated backup size
- Workspace detection results
- Disk space availability
- Files that would be skipped

**No files are created or modified!**

### 2. Create Full Backup

```bash
~/.skills/bot-update/backup-bot-full.sh
```

**Backs up:**
- `~/.bot/bot.json` (config)
- `~/.bot/sessions/` (session state)
- `~/.bot/agents/` (multi-agent state)
- `~/.bot/credentials/` (auth tokens)
- `~/.bot/cron/` (scheduled jobs)
- `~/.bot/sandboxes/` (sandbox state)
- All agent workspaces (dynamically detected!)
- Git commit and status

**Output:** `~/.bot-backups/pre-update-YYYYMMDD-HHMMSS/`

### 3. Update Bot

Follow the checklist:

```bash
cat ~/.skills/bot-update/UPDATE_CHECKLIST.md
```

**Key steps:**
1. Create backup
2. Stop gateway
3. Pull latest code
4. Adjust config for breaking changes
5. Run doctor
6. Test functionality
7. Start gateway as daemon

### 4. Restore from Backup

```bash
~/.skills/bot-update/restore-bot.sh ~/.bot-backups/pre-update-YYYYMMDD-HHMMSS
```

**Restores:**
- All configuration
- All state files
- All workspaces
- Optionally: git version

## Important Notes

### Multi-Agent Setup

This skill is designed for multi-agent setups with:
- Multiple agents with separate workspaces
- Sandbox configurations
- Provider routing (WhatsApp/Telegram/Discord/Slack/etc.)

### Breaking Changes in v2026.1.8

**CRITICAL:**
- **DM Lockdown**: DMs now default to `pairing` policy instead of open
- **Groups**: `telegram.groups` and `whatsapp.groups` are now allowlists
- **Sandbox**: Default scope changed to `"agent"` from implicit
- **Timestamps**: Now UTC format in agent envelopes

### Backup Validation

After backup, always verify:
```bash
BACKUP_DIR=~/.bot-backups/pre-update-YYYYMMDD-HHMMSS
cat "$BACKUP_DIR/BACKUP_INFO.txt"
ls -lh "$BACKUP_DIR"
```

Should contain:
- ✅ `bot.json`
- ✅ `credentials.tar.gz`
- ✅ `workspace-*.tar.gz` (one per agent)

### Config Changes Required

**Example: Switch WhatsApp to pairing:**
```bash
jq '.whatsapp.dmPolicy = "pairing"' ~/.bot/bot.json | sponge ~/.bot/bot.json
```

**Example: Set explicit sandbox scope:**
```bash
jq '.agent.sandbox.scope = "agent"' ~/.bot/bot.json | sponge ~/.bot/bot.json
```

## Workflow

### Standard Update Flow

```bash
# 1. Check for updates
~/.skills/bot-update/check-upstream.sh

# 2. Validate current setup
~/.skills/bot-update/validate-setup.sh

# 3. Dry run
~/.skills/bot-update/backup-bot-dryrun.sh

# 4. Backup
~/.skills/bot-update/backup-bot-full.sh

# 5. Stop gateway
cd ~/code/bot
pnpm bot gateway stop

# 6. Update code
git checkout main
git pull --rebase origin main
pnpm install
pnpm build

# 7. Run doctor
pnpm bot doctor --yes

# 8. Test
pnpm bot gateway start  # foreground for testing

# 9. Deploy
pnpm bot gateway stop
pnpm bot gateway start --daemon
```

### Rollback Flow

```bash
# Quick rollback
~/.skills/bot-update/restore-bot.sh <backup-dir>

# Manual rollback
cd ~/code/bot
git checkout <old-commit>
pnpm install && pnpm build
cp <backup-dir>/bot.json ~/.bot/
pnpm bot gateway restart
```

## Testing After Update

### Functionality Tests

- [ ] Provider DMs work (check pairing policy)
- [ ] Group mentions respond
- [ ] Typing indicators work
- [ ] Agent routing works
- [ ] Sandbox isolation works
- [ ] Tool restrictions enforced

### New Features
```bash
pnpm bot agents list
pnpm bot logs --tail 50
pnpm bot providers list --usage
pnpm bot skills list
```

### Monitoring

```bash
# Live logs
pnpm bot logs --follow

# Or Web UI
open http://localhost:3001/logs

# Check status
pnpm bot status
pnpm bot gateway status
```

## Troubleshooting

### Common Issues

**Gateway won't start:**
```bash
pnpm bot logs --grep error
pnpm bot doctor
```

**Auth errors:**
```bash
# OAuth profiles might need re-login
pnpm bot providers login <provider>
```

**Sandbox issues:**
```bash
# Check sandbox config
jq '.agent.sandbox' ~/.bot/bot.json

# Check per-agent sandbox
jq '.routing.agents[] | {name, sandbox}' ~/.bot/bot.json
```

### Emergency Restore

If something goes wrong:

```bash
# 1. Stop gateway
pnpm bot gateway stop

# 2. Full restore
LATEST_BACKUP=$(ls -t ~/.bot-backups/ | head -1)
~/.skills/bot-update/restore-bot.sh ~/.bot-backups/$LATEST_BACKUP

# 3. Restart
pnpm bot gateway start
```

## Installation

### Via Skills

```bash
bot skills install bot-update
```

### Manual

```bash
git clone <repo-url> ~/.skills/bot-update
chmod +x ~/.skills/bot-update/*.sh
```

## License

MIT - see [LICENSE](LICENSE)

## Author

**Pascal Schott** ([@pasogott](https://github.com/pasogott))

Contribution for Bot  
https://github.com/bot/bot
