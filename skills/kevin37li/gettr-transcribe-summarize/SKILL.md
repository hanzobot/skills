---
name: gettr-transcribe-summarize
description: Download audio from a GETTR post (via HTML og:video), transcribe it locally with MLX Whisper on Apple Silicon (with timestamps via VTT), and summarize the transcript into bullet points and/or a timestamped outline. Use when given a GETTR post URL and asked to produce a transcript or summary.
---

# Gettr Transcribe + Summarize (MLX Whisper)

## Quick start (single command)

Run the full pipeline (Steps 1–3) with one command:
```bash
bash scripts/run_pipeline.sh "<GETTR_POST_URL>"
```

This outputs:
- `./out/gettr-transcribe-summarize/<slug>/audio.wav`
- `./out/gettr-transcribe-summarize/<slug>/audio.vtt`

Then proceed to Step 4 (Summarize) to generate the final deliverable.

---

## Workflow (GETTR URL → transcript → summary)

### Inputs to confirm
Ask for:
- GETTR post URL
- Output format: **bullets only** or **bullets + timestamped outline**
- Summary size: **short**, **medium** (default), or **detailed**

Notes:
- This skill does **not** handle authentication-gated GETTR posts.
- This skill does **not** translate; outputs stay in the video’s original language.

### Prereqs (local)
- `mlx_whisper` installed and on PATH
- `ffmpeg` installed (recommended: `brew install ffmpeg`)

### Step 0 — Pick an output directory
Recommended convention: `./out/gettr-transcribe-summarize/<slug>/`

Extract the slug from the GETTR post URL (e.g., `https://gettr.com/post/p1abc2def` → slug = `p1abc2def`).

Directory structure:
- `./out/gettr-transcribe-summarize/<slug>/audio.wav`
- `./out/gettr-transcribe-summarize/<slug>/audio.vtt`
- `./out/gettr-transcribe-summarize/<slug>/summary.md`

### Step 1 — Extract the media URL and slug
Preferred: fetch the post HTML and read `og:video*`.

```bash
python3 scripts/extract_gettr_og_video.py "<GETTR_POST_URL>"
```
This prints the best candidate video URL (often an HLS `.m3u8`) and the post slug.

Extract the slug from the URL path (e.g., `/post/p1abc2def` → `p1abc2def`) to create the output directory.

If extraction fails, ask the user to provide the `.m3u8`/MP4 URL directly (common if the post is private/gated or the HTML is dynamic).

### Step 2 — Download audio with ffmpeg
Extract audio-only (16kHz mono WAV) for faster and more stable transcription:
```bash
bash scripts/download_audio.sh "<M3U8_OR_MP4_URL>" "./out/gettr-transcribe-summarize/<slug>/audio.wav"
```

This directly extracts audio without intermediate video, reducing disk I/O and processing time.

### Step 3 — Transcribe with MLX Whisper
Generate VTT output with timestamps:
```bash
mlx_whisper "./out/gettr-transcribe-summarize/<slug>/audio.wav" \
  -f vtt \
  -o "./out/gettr-transcribe-summarize/<slug>" \
  --model mlx-community/whisper-large-v3-turbo \
  --condition-on-previous-text False \
  --word-timestamps True
```

Flags explained:
- `-f vtt`: VTT format provides timestamps for building the outline.
- `--condition-on-previous-text False`: prevents hallucination errors from propagating across segments.
- `--word-timestamps True`: more precise timing for section boundaries.

Notes:
- Language is auto-detected; transcription stays in the original language.
- If too slow or memory-heavy, try smaller models: `mlx-community/whisper-medium` or `mlx-community/whisper-small`.
- If quality is poor, try the full model: `mlx-community/whisper-large-v3` (slower but more accurate).
- If `--word-timestamps` causes issues, omit it (the pipeline script handles this automatically).

### Step 4 — Summarize
Write the final deliverable to `./out/gettr-transcribe-summarize/<slug>/summary.md`.

Pick a **summary size** (user-selectable):
- **Short:** 5–8 bullets; (if outline) 4–6 sections
- **Medium (default):** 8–20 bullets; (if outline) 6–15 sections
- **Detailed:** 20–40 bullets; (if outline) 15–30 sections

Include:
- **Bullets** (per size above)
- Optional **timestamped outline** (per size above)

Timestamped outline format (default heading style):
```
[00:00 - 02:15] Section heading
- 1–3 sub-bullets
```

When building the outline from VTT cues:
- Group adjacent cues into coherent sections.
- Use the start time of the first cue and end time of the last cue in the section.

## Bundled scripts
- `scripts/run_pipeline.sh`: full pipeline wrapper (Steps 1–3 in one command)
- `scripts/extract_gettr_og_video.py`: fetch GETTR HTML and extract `og:video*` URL + post slug (with retry/backoff)
- `scripts/download_audio.sh`: download/extract audio from HLS or MP4 URL to 16kHz mono WAV

### Error handling
- **Non-video posts**: The extraction script detects image/text posts and provides a helpful error message.
- **Network errors**: Automatic retry with exponential backoff (up to 3 attempts).
- **No audio track**: The download script validates output and reports if the source has no audio.

## Troubleshooting
See `references/troubleshooting.md`.
