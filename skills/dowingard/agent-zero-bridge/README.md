# Agent Zero Bridge - Bot Skill

Bidirectional communication bridge between [Bot](https://github.com/bot/bot) and [Agent Zero](https://github.com/frdel/agent-zero).

## What It Does

```
┌─────────────┐                    ┌─────────────┐
│  Bot   │◄──────────────────►│ Agent Zero  │
│  (Claude)   │                    │   (A0)      │
└─────────────┘                    └─────────────┘
```

- **Bot → Agent Zero**: Delegate complex coding/research tasks
- **Agent Zero → Bot**: Report progress, ask questions, notify completion
- **Task Breakdown**: Break complex tasks into tracked, checkable steps

## Installation

### Option 1: Let Bot Install It

Just tell Bot:
> "Install the Agent Zero bridge skill"

Or if you have this repo cloned:
> "Install the Agent Zero bridge skill from ~/path/to/this/folder"

### Option 2: Manual Installation

```bash
# Clone or download this repo
git clone https://github.com/DOWingard/Bot-Agent0-Bridge.git

# Copy to Bot skills directory
cp -r Bot-Agent0-Bridge ~/.bot/skills/agent-zero-bridge

# Configure
cd ~/.bot/skills/agent-zero-bridge
cp .env.example .env
# Edit .env with your API keys (see SKILL.md for details)
```

## Quick Start

After installation, tell Bot:
- "Ask Agent Zero to build a REST API"
- "Delegate this coding task to A0"
- "Have Agent Zero review this code"

Or use the CLI directly:
```bash
node ~/.bot/skills/agent-zero-bridge/scripts/a0_client.js "Your task here"
```

## File Structure

```
agent-zero-bridge/
├── SKILL.md          # Bot skill definition + setup guide
├── .env.example      # Configuration template
├── .gitignore
├── LICENSE           # MIT
├── README.md         # This file
└── scripts/
    ├── a0_client.js        # CLI: Bot → Agent Zero
    ├── bot_client.js  # CLI: Agent Zero → Bot
    ├── task_breakdown.js   # Task breakdown workflow
    └── lib/
        ├── config.js       # Configuration loader
        ├── a0_api.js       # Agent Zero API client
        ├── bot_api.js # Bot API client
        └── cli.js          # CLI argument parser
```

## Configuration

See `SKILL.md` for detailed setup instructions, including:
- How to get your Agent Zero API token
- Bot Gateway configuration
- Docker deployment for bidirectional communication

## Requirements

- Node.js 18+ (for built-in fetch)
- Agent Zero running (Docker recommended)
- Bot Gateway with HTTP endpoints enabled

## License

MIT
