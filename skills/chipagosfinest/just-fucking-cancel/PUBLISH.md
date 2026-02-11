# Publishing just-fucking-cancel to Skills

## Attribution
- **Original**: https://github.com/rohunvora/just-fucking-cancel by @rohunvora
- **Adapted for Hanzo Bot**: @chipagosfinest
- **Mostly written by**: Claude (Anthropic)

## Publish Command

```bash
# 1. Install Skills CLI (if not already)
npm i -g skills

# 2. Login to Skills
skills login

# 3. Publish the skill
cd /path/to/bot-railway
skills publish ./skills/just-fucking-cancel \
  --slug just-fucking-cancel \
  --name "just-fucking-cancel" \
  --version 1.0.0 \
  --changelog "Initial release - subscription audit and cancellation skill.

Originally created by rohunvora (https://github.com/rohunvora/just-fucking-cancel).
Adapted for Hanzo Bot by @chipagosfinest.
Mostly written by Claude.

Features:
- Analyze bank CSV exports to find recurring charges
- Interactive categorization (Cancel/Investigate/Keep)
- HTML audit report with privacy toggle
- Browser automation for cancellations
- 50+ common service cancel URLs

DM @chipagosfinest on X if you need anything."
```

## After Publishing

The skill will be available at:
```
https://skills.com/chipagosfinest/just-fucking-cancel
```

Add to any bot.json:
```json
"just-fucking-cancel": {
  "location": "https://skills.com/chipagosfinest/just-fucking-cancel"
}
```

Or install via CLI:
```bash
skills install chipagosfinest/just-fucking-cancel
```
