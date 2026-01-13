---
name: gemini-stt
description: Transcribe audio files using Google's Gemini API
metadata: {"clawdbot":{"emoji":"🎤","os":["linux","darwin"],"requires":{"env":["GEMINI_API_KEY"]}}}
---

# Gemini Speech-to-Text Skill

Transcribe audio files using Google's Gemini API. Default model is `gemini-2.0-flash-lite` for fastest transcription.

## Requirements

- **GEMINI_API_KEY**: Set in environment (e.g., `~/.env` or `~/.clawdbot/.env`)
- Python 3.x (no external dependencies)

## Supported Formats

- `.ogg` / `.opus` (Telegram voice messages)
- `.mp3`
- `.wav`
- `.m4a`

## Usage

```bash
# Basic usage (uses default model: gemini-2.0-flash-lite)
python ~/.claude/skills/gemini-stt/transcribe.py /path/to/audio.ogg

# With a specific model
python ~/.claude/skills/gemini-stt/transcribe.py /path/to/audio.ogg --model gemini-2.5-pro

# Short form
python ~/.claude/skills/gemini-stt/transcribe.py /path/to/audio.ogg -m gemini-2.5-flash

# With Clawdbot media
python ~/.claude/skills/gemini-stt/transcribe.py ~/.clawdbot/media/inbound/voice-message.ogg
```

## Options

| Option | Description |
|--------|-------------|
| `<audio_file>` | Path to the audio file (required) |
| `--model`, `-m` | Gemini model to use (default: `gemini-2.0-flash-lite`) |

## Supported Models

Any Gemini model that supports audio input can be used. Recommended models:

| Model | Notes |
|-------|-------|
| `gemini-2.0-flash-lite` | **Default.** Fastest transcription speed. |
| `gemini-2.0-flash` | Fast and cost-effective. |
| `gemini-2.5-flash-lite` | Lightweight 2.5 model. |
| `gemini-2.5-flash` | Balanced speed and quality. |
| `gemini-2.5-pro` | Higher quality, slower. |
| `gemini-3-flash-preview` | Latest flash model. |
| `gemini-3-pro-preview` | Latest pro model, best quality. |

See [Gemini API Models](https://ai.google.dev/gemini-api/docs/models) for the latest list.

## How It Works

1. Reads the audio file and base64 encodes it
2. Sends to the selected Gemini model with transcription prompt
3. Returns the transcribed text

## Example Integration

For Clawdbot voice message handling:

```bash
# Transcribe incoming voice message
TRANSCRIPT=$(python ~/.claude/skills/gemini-stt/transcribe.py "$AUDIO_PATH")
echo "User said: $TRANSCRIPT"
```

## Error Handling

The script exits with code 1 and prints to stderr on:
- Missing `GEMINI_API_KEY`
- File not found
- API errors

## Notes

- Uses Gemini 2.0 Flash Lite by default for fastest transcription
- No external Python dependencies (uses stdlib only)
- Automatically detects MIME type from file extension
