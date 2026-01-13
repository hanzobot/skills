#!/usr/bin/env python3
"""
Gemini-based Speech-to-Text transcription.

Uses Google's Gemini API to transcribe audio files.
Requires GEMINI_API_KEY environment variable.

Usage:
    python transcribe.py <audio_file> [--model MODEL]

Supports: audio/ogg (opus), audio/mp3, audio/wav, audio/m4a
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_MODEL = "gemini-2.0-flash-lite"

SUPPORTED_EXTENSIONS = {
    ".ogg": "audio/ogg",
    ".opus": "audio/ogg",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
}


def get_mime_type(file_path: str) -> str:
    """Determine MIME type from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return SUPPORTED_EXTENSIONS.get(ext, "audio/ogg")


def transcribe(file_path: str, api_key: str, model: str = DEFAULT_MODEL) -> str:
    """
    Transcribe an audio file using Gemini API.

    Args:
        file_path: Path to the audio file
        api_key: Gemini API key
        model: Gemini model to use (default: gemini-2.0-flash-lite)

    Returns:
        Transcribed text

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If API call fails
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    with open(file_path, "rb") as f:
        audio_data = f.read()

    b64_data = base64.b64encode(audio_data).decode("utf-8")
    mime_type = get_mime_type(file_path)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Transcribe this audio file exactly. Return only the transcription text, no preamble."
                    },
                    {"inline_data": {"mime_type": mime_type, "data": b64_data}},
                ]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
            return result["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP Error {e.code}: {error_body}")
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected API response format: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using Google's Gemini API"
    )
    parser.add_argument("audio_file", help="Path to the audio file to transcribe")
    parser.add_argument(
        "--model",
        "-m",
        default=DEFAULT_MODEL,
        help=f"Gemini model to use (default: {DEFAULT_MODEL})",
    )
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        text = transcribe(args.audio_file, api_key, args.model)
        print(text)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
