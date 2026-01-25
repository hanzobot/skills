#!/usr/bin/env bash
set -euo pipefail

# GETTR Transcribe Pipeline
# Usage: run_pipeline.sh <gettr_post_url> [output_base_dir]
#
# Runs the full pipeline:
#   1. Extract video URL and slug from GETTR post
#   2. Download audio (16kHz mono WAV)
#   3. Transcribe with MLX Whisper (VTT output)
#
# Output: <output_base_dir>/gettr-transcribe-summarize/<slug>/
#   - audio.wav
#   - audio.vtt
#
# The summary step (Step 4) is left to the LLM.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: run_pipeline.sh <gettr_post_url> [output_base_dir]" >&2
  echo "" >&2
  echo "Options:" >&2
  echo "  output_base_dir  Base directory for output (default: ./out)" >&2
  exit 2
fi

GETTR_URL="$1"
OUTPUT_BASE="${2:-./out}"

# Check prerequisites
for cmd in python3 ffmpeg mlx_whisper; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[error] Required command not found: $cmd" >&2
    if [[ "$cmd" == "ffmpeg" ]]; then
      echo "[hint] Install with: brew install ffmpeg" >&2
    elif [[ "$cmd" == "mlx_whisper" ]]; then
      echo "[hint] Install with: pip install mlx-whisper" >&2
    fi
    exit 127
  fi
done

echo "=== Step 1: Extracting video URL and slug ===" >&2

# Run extraction script and capture output
EXTRACT_OUTPUT=$("$SCRIPT_DIR/extract_gettr_og_video.py" "$GETTR_URL") || {
  echo "[error] Failed to extract video URL from GETTR post" >&2
  exit 1
}

# Parse output: line 1 = video URL, line 2 = slug
VIDEO_URL=$(echo "$EXTRACT_OUTPUT" | head -n1)
SLUG=$(echo "$EXTRACT_OUTPUT" | tail -n1)

if [[ -z "$VIDEO_URL" || -z "$SLUG" ]]; then
  echo "[error] Failed to parse extraction output" >&2
  exit 1
fi

echo "[info] Video URL: $VIDEO_URL" >&2
echo "[info] Slug: $SLUG" >&2

# Set up output directory
OUT_DIR="$OUTPUT_BASE/gettr-transcribe-summarize/$SLUG"
mkdir -p "$OUT_DIR"

AUDIO_FILE="$OUT_DIR/audio.wav"
VTT_FILE="$OUT_DIR/audio.vtt"

echo "" >&2
echo "=== Step 2: Downloading audio ===" >&2

"$SCRIPT_DIR/download_audio.sh" "$VIDEO_URL" "$AUDIO_FILE" >&2 || {
  echo "[error] Failed to download audio" >&2
  exit 1
}

echo "[info] Audio saved: $AUDIO_FILE" >&2

echo "" >&2
echo "=== Step 3: Transcribing with MLX Whisper ===" >&2

# MLX Whisper transcription with optimized flags:
# -f vtt: VTT format for timestamps
# --condition-on-previous-text False: prevents hallucination propagation
# --word-timestamps True: more precise timing (if supported)
# Language is auto-detected (transcribes in original language)
mlx_whisper "$AUDIO_FILE" \
  -f vtt \
  -o "$OUT_DIR" \
  --model mlx-community/whisper-large-v3-turbo \
  --condition-on-previous-text False \
  --word-timestamps True \
  2>&1 || {
    echo "[warn] Retrying without extra flags..." >&2
    mlx_whisper "$AUDIO_FILE" \
      -f vtt \
      -o "$OUT_DIR" \
      --model mlx-community/whisper-large-v3-turbo
  }

echo "[info] Transcript saved: $VTT_FILE" >&2

echo "" >&2
echo "=== Pipeline complete ===" >&2
echo "[info] Output directory: $OUT_DIR" >&2
echo "" >&2

# Output the paths for programmatic use (stdout)
echo "$OUT_DIR"
echo "$AUDIO_FILE"
echo "$VTT_FILE"
