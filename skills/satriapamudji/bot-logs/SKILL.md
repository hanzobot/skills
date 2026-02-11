---
name: bot-logs
description: Analyze Bot logs and diagnostics. Use when the user asks about bot performance, response times, errors, session stats, token usage, API costs, or wants to debug slow responses.
---

# Bot Logs & Diagnostics

Analyze Bot performance, errors, and session data.

## Quick Commands

### Response Times (last N messages)
```bash
scripts/response-times.sh [count]
```

### Recent Errors
```bash
journalctl --user -u bot-gateway.service --no-pager --since "1 hour ago" | grep -iE "(error|fail|invalid)" | tail -20
```

### Session Stats
```bash
scripts/session-stats.sh
```

### Gateway Status
```bash
systemctl --user status bot-gateway.service --no-pager
```

### Config Validation
```bash
cat ~/.bot/bot.json | jq . > /dev/null && echo "Config valid" || echo "Config invalid"
```

## Log Sources

| Source | Location | Contains |
|--------|----------|----------|
| Journal | `journalctl --user -u bot-gateway.service` | Session state, errors, tool exec |
| Daily log | `/tmp/bot/bot-YYYY-MM-DD.log` | Detailed JSON logs |
| Session file | `~/.bot/agents/main/sessions/*.jsonl` | Full conversation, token usage, costs |
| Sessions meta | `~/.bot/agents/main/sessions/sessions.json` | Current session state, model info |

## Common Diagnostics

### Slow Responses
1. Check response times: `scripts/response-times.sh 20`
2. Check token count in sessions.json: `jq '.["agent:main:main"].totalTokens' ~/.bot/agents/main/sessions/sessions.json`
3. If tokens > 30000, run `/compact` in Telegram or start new session

### Config Errors
```bash
journalctl --user -u bot-gateway.service --no-pager --since "10 minutes ago" | grep -i "invalid config"
```

### API Costs (from session)
```bash
scripts/session-stats.sh
```

## Useful Patterns

### Filter journal by category
```bash
# Session state changes
journalctl --user -u bot-gateway.service | grep "session state"

# Tool execution
journalctl --user -u bot-gateway.service | grep "\[tools\]"

# Telegram activity
journalctl --user -u bot-gateway.service | grep "\[telegram\]"
```

### Parse session file for recent messages
```bash
tail -20 ~/.bot/agents/main/sessions/*.jsonl | jq -r 'select(.message.role=="user") | .message.content[0].text' 2>/dev/null | tail -10
```
