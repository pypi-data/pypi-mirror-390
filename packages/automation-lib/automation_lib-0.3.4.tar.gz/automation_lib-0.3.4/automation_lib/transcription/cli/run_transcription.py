# automation_lib/transcription/cli/run_transcription.py

import argparse
import asyncio
import os

from dotenv import load_dotenv

from automation_lib.transcription.transcription_runner import transcribe_audio_file


def main():
    load_dotenv() # Load environment variables at the CLI entry point

    parser = argparse.ArgumentParser(description="Transcribe an audio file using the transcription module.")
    parser.add_argument("audio_path", type=str, help="Path to the audio file to transcribe.")
    parser.add_argument("--no-cleanup", action="store_true", help="Do not clean up temporary audio segments after transcription.")

    args = parser.parse_args()

    if not os.path.exists(args.audio_path):
        print(f"Error: Audio file not found at '{args.audio_path}'")
        return

    try:
        full_transcript = asyncio.run(transcribe_audio_file(args.audio_path, cleanup_segments=not args.no_cleanup))
        print("\n--- Full Transcript ---")
        print(full_transcript)
    except Exception as e:
        print(f"An error occurred during transcription: {e}")

if __name__ == "__main__":
    main()
