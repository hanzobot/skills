# Council - Multi-Agent Deliberation

Council Chamber pattern for structured debate with Memory Bridge integration.

## Installation

```bash
skills install council
```

Or manual:
```bash
git clone https://github.com/emasoudy/bot-skills.git
cp -r bot-skills/council ~/.bot/skills/
~/.bot/skills/council/init-db.sh
```

## Usage

Start a council chamber:
```bash
council_chamber topic:"Your Topic" members:"architect,strategist"
```

**Chamber Pattern**: Single session with multiple personas debating, rather than separate agents.

## Default Members

- `architect` - System Architect
- `analyst` - Technical Analyst  
- `security` - Security Officer
- `designer` - UX Designer
- `strategist` - Business Strategist

## License

MIT - See LICENSE file
