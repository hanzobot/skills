# ⚠️ DEPRECATED — Bot Handles This Natively

**This skill is no longer needed.**

As of January 2026, Bot has built-in OAuth support that:
- Connects to Claude via the setup wizard (`bot onboard --auth-choice claude-cli`)
- Automatically refreshes tokens before expiry
- Updates auth profiles without any user intervention

**You don't need to install this skill.** Just run `bot onboard` and select Claude CLI auth — it pulls tokens from Keychain automatically.

---

## What This Skill Was For

This skill was created to solve two issues before native support existed:
1. Getting Bot to recognize Claude tokens from Keychain
2. Keeping tokens refreshed automatically

**Bot now does both of these automatically.**

---

## If You Have This Installed

You can safely:
1. Remove the launchd job: `launchctl unload ~/Library/LaunchAgents/com.bot.claude-oauth-refresh.plist`
2. Delete the skill folder: `rm -rf ~/bot/skills/claude-connect`
3. Remove any related cron jobs

Your tokens will continue to work via Bot's native support.

---

## Still Having Issues?

If `bot onboard` doesn't find your Claude tokens:

1. Make sure Claude CLI is installed and logged in:
   ```bash
   claude
   # Then run: /login
   ```

2. Re-run the Bot wizard:
   ```bash
   bot onboard --auth-choice claude-cli
   ```

---

## Historical Reference

This repo is kept for historical reference only. The code is no longer maintained.

**Original purpose:** Connect Claude subscription to Bot and keep tokens refreshed.

---

## License

MIT
