---
name: grok-search
description: Search the web or X/Twitter using xAI Grok server-side tools (web_search, x_search) via the xAI Responses API. Use when you need tweets/threads/users from X, or want Grok as an alternative search provider.
metadata: {"bot":{"requires":{"bins":["node"],"env":["XAI_API_KEY"]},"primaryEnv":"XAI_API_KEY"}}
---

Use Grok search via the bundled script and return structured results.

## Prereqs

- `XAI_API_KEY` must be set (env var), or present at `~/.bot/bot.json` under `env.XAI_API_KEY`.

## Run

From the agent workspace root (or `cd` into this skill folder):

- Web search (JSON):
  - `node skills/grok-search/scripts/grok_search.mjs "<query>" --web --json --max 10`

- X/Twitter search (JSON):
  - `node skills/grok-search/scripts/grok_search.mjs "<query>" --x --json --max 10`

Optional:
- `--max <n>` limit results
- `--model <id>` (default: `grok-4-1-fast`)

## Output shape

The script returns JSON:

`{ "query": string, "mode": "web"|"x", "results": [{"title": string|null, "url": string|null, "snippet": string|null}], "citations": [string] }`

## Tips

- Prefer `--x` when the user asks for tweets, threads, or “what’s happening on X”.
- Use `--web` for general web research, especially when you want xAI citations.
- If results are too broad, tighten query terms (add @handles, exact phrases, time hints like “2026”).
