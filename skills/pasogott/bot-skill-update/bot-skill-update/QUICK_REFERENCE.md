# Bot Update - Quick Reference Card

## 🚀 One-Liner Commands

```bash
# Dry run (preview backup)
~/.skills/bot-update/backup-bot-dryrun.sh

# Backup everything
~/.skills/bot-update/backup-bot-full.sh

# Show checklist
cat ~/.skills/bot-update/UPDATE_CHECKLIST.md

# Restore from backup
~/.skills/bot-update/restore-bot.sh <backup-dir>

# List backups
ls -lth ~/.bot-backups/

# View last backup
cat $(ls -td ~/.bot-backups/*/ | head -1)/BACKUP_INFO.txt
```

## ⚡ Emergency Rollback

```bash
# Stop gateway
cd ~/code/bot && pnpm bot gateway stop

# Restore latest backup
LATEST=$(ls -t ~/.bot-backups/ | head -1)
~/.skills/bot-update/restore-bot.sh ~/.bot-backups/$LATEST

# Start gateway
pnpm bot gateway start
```

## 🔧 Config Quick Fixes

```bash
# Switch to pairing (recommended)
jq '.whatsapp.dmPolicy = "pairing" | .telegram.dmPolicy = "pairing"' ~/.bot/bot.json | sponge ~/.bot/bot.json

# Set explicit sandbox scope
jq '.agent.sandbox.scope = "agent"' ~/.bot/bot.json | sponge ~/.bot/bot.json

# Set user timezone
jq '.agent.userTimezone = "America/New_York"' ~/.bot/bot.json | sponge ~/.bot/bot.json

# View current config
jq '.' ~/.bot/bot.json | less
```

## 📊 Status Checks

```bash
# Gateway status
pnpm bot gateway status

# Live logs
pnpm bot logs --follow

# Agents
pnpm bot agents list

# Providers with usage
pnpm bot providers list --usage

# Full status
pnpm bot status
```

## 🧪 Test Commands

```bash
# New CLIs
pnpm bot agents list
pnpm bot logs --tail 50
pnpm bot providers list --usage
pnpm bot skills list

# Web UI
open http://localhost:3001/logs

# Check routing
jq '.routing.bindings' ~/.bot/bot.json
```

## 🎯 Critical Checks

```bash
# DM policies
jq '.whatsapp.dmPolicy, .telegram.dmPolicy' ~/.bot/bot.json

# Groups config
jq '.telegram.groups, .whatsapp.groups' ~/.bot/bot.json

# Sandbox config
jq '.agent.sandbox' ~/.bot/bot.json

# Per-agent config
jq '.routing.agents[] | {name, workspace, sandbox}' ~/.bot/bot.json

# Workspaces list
jq -r '.routing.agents | to_entries[] | "\(.key): \(.value.workspace)"' ~/.bot/bot.json
```

## 🔥 Troubleshooting

```bash
# Logs with errors
pnpm bot logs --grep error

# Run doctor
pnpm bot doctor --yes

# Restart gateway
pnpm bot gateway restart

# Kill stuck processes
pkill -f "bot gateway"

# Check gateway ports
lsof -i :3001 -i :3002
```

## 📦 Update Flow (Copy-Paste)

```bash
# 0. Dry run (optional)
~/.skills/bot-update/backup-bot-dryrun.sh

# 1. Backup
~/.skills/bot-update/backup-bot-full.sh

# 2. Stop
cd ~/code/bot && pnpm bot gateway stop

# 3. Update
git checkout main
git pull --rebase origin main
pnpm install
pnpm build

# 4. Config (adjust as needed)
jq '.whatsapp.dmPolicy = "pairing"' ~/.bot/bot.json | sponge ~/.bot/bot.json
jq '.agent.sandbox.scope = "agent"' ~/.bot/bot.json | sponge ~/.bot/bot.json

# 5. Doctor
pnpm bot doctor --yes

# 6. Start
pnpm bot gateway start --daemon

# 7. Verify
pnpm bot gateway status
pnpm bot logs --tail 20
```

## 🎓 Version Check

```bash
# Current version
cd ~/code/bot && git log -1 --oneline

# Upstream version
git fetch origin && git log main..origin/main --oneline | head -5

# Check for updates
git fetch origin && git diff --stat main..origin/main
```

## 💾 Workspace Checks

```bash
# List configured workspaces
jq -r '.routing.agents | to_entries[] | "\(.key): \(.value.workspace)"' ~/.bot/bot.json

# Check workspace sizes
du -sh ~/bot*

# Check .bot size
du -sh ~/.bot

# Backup size
du -sh ~/.bot-backups/
```

## 🔐 Auth Check

```bash
# List credentials
ls -la ~/.bot/credentials/

# Check auth profiles
jq '.models' ~/.bot/bot.json

# Provider login status
pnpm bot providers list
```

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Backup | 2-3 min |
| Update code | 3-5 min |
| Config changes | 5-10 min |
| Doctor | 2-3 min |
| Testing | 10-15 min |
| **Total** | **25-35 min** |

## 📞 Emergency Contacts

**Logs:** `~/.bot/logs/`  
**Backups:** `~/.bot-backups/`  
**Config:** `~/.bot/bot.json`  
**Skill:** `~/.skills/bot-update/`

---

**Last Updated:** 2026-01-08  
**Target Version:** v2026.1.8  
**Repository:** https://github.com/bot/bot
