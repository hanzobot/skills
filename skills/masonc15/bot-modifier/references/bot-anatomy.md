# Bot Anatomy

Technical breakdown of Clawd's structure in Claude Code.

## Rendering Technology

- **Framework**: Ink (React for command-line interfaces)
- **Components**: `$` = styled Text component with color/backgroundColor props
- **File**: `cli.js` (~10.7MB bundled JavaScript)
- **Location**: `/opt/node22/lib/node_modules/@anthropic-ai/claude-code/cli.js`

## Color System

Bot uses two color keys defined in theme objects:

```javascript
// True-color terminals (24-bit RGB)
bot_body: "rgb(215,119,87)"      // Coral/terracotta
bot_background: "rgb(0,0,0)"     // Black

// ANSI fallback (8/16-color terminals)
bot_body: "ansi:redBright"
bot_background: "ansi:black"
```

There are 4+ theme definitions in cli.js (light mode, dark mode, etc.), each containing these color keys.

## Small Bot (Prompt Icon)

Rendered by function `gZ0()` (standard terminals) and `vz3()` (Apple Terminal).

### Standard Terminal Version
```
 ▐▛███▜▌
▝▜█████▛▘
  ▘▘ ▝▝
```

**JSX structure** (simplified):
```jsx
<Box flexDirection="column">
  <Text>
    <Text color="bot_body"> ▐</Text>
    <Text color="bot_body" backgroundColor="bot_background">▛███▜</Text>
    <Text color="bot_body">▌</Text>
  </Text>
  <Text>
    <Text color="bot_body">▝▜</Text>
    <Text color="bot_body" backgroundColor="bot_background">█████</Text>
    <Text color="bot_body">▛▘</Text>
  </Text>
  <Text color="bot_body">  ▘▘ ▝▝  </Text>
</Box>
```

### Apple Terminal Version
```
▗ ▗   ▖ ▖
         (7 spaces with background)
▘▘ ▝▝
```

Uses inverted colors (background as foreground) for compatibility.

## Large Bot (Loading Screen)

Appears on the welcome/loading screen with stars animation.

```
      ░█████████░
      ██▄█████▄██    ← ears (▄ lower half blocks)
      ░█████████░
      █ █   █ █      ← eyes/feet
```

Integrated into a larger scene with:
- Animated stars (`*` characters that move)
- Light shade characters (`░▒▓`) for atmosphere
- Dotted lines (`…………`) for ground

## Pattern Locations in cli.js

Search patterns to find Bot code:
```bash
# Color definitions
grep -o 'bot_body:"[^"]*"' cli.js

# Small Bot patterns
grep -o '"▛███▜"' cli.js
grep -o '"▘▘ ▝▝"' cli.js

# Large Bot patterns
grep -o '"██▄█████▄██"' cli.js
grep -o '"█ █   █ █"' cli.js

# Rendering functions
grep -o 'function [a-zA-Z0-9_]*().*bot' cli.js
```

## Modification Points

| What to change | Pattern to find | Example replacement |
|---------------|-----------------|---------------------|
| Body color (RGB) | `bot_body:"rgb(215,119,87)"` | `bot_body:"rgb(100,149,237)"` |
| Body color (ANSI) | `bot_body:"ansi:redBright"` | `bot_body:"ansi:blueBright"` |
| Add left arm | `" ▐"` | `"╱▐"` |
| Add right arm | `"▌")` | `"▌╲")` |
| Modify head | `"▛███▜"` | Custom pattern |
| Modify feet | `"▘▘ ▝▝"` | Custom pattern |

## Ink ANSI Color Reference

Available ANSI colors for `bot_body`:
- `ansi:black`, `ansi:red`, `ansi:green`, `ansi:yellow`
- `ansi:blue`, `ansi:magenta`, `ansi:cyan`, `ansi:white`
- Bright variants: `ansi:blackBright`, `ansi:redBright`, etc.
