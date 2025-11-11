import asyncio
import os

from prefect import task

from automation_lib.transcription.config.transcription_config import TranscriptionConfig, load_transcription_config  # Import TranscriptionConfig
from automation_lib.transcription.transcription_helpers import split_audio_file, transcribe_audio_segment


@task
async def transcribe_audio_file(audio_path: str, cleanup_segments: bool = True, config: TranscriptionConfig | None = None) -> str:
    """
    Main function to transcribe an audio file, handling splitting if necessary.
    If cleanup_segments is True, temporary audio segments will be deleted after transcription.
    """
    if config is None:
        config = load_transcription_config()

    print(f"Starting transcription for: {audio_path} using {config.transcription_provider} provider.")
    
    segments = split_audio_file(audio_path, config)
    full_transcript = []

    for i, segment_path in enumerate(segments):
        print(f"Transcribing segment {i+1}/{len(segments)}: {segment_path}")
        try:
            transcript_text = await transcribe_audio_segment(segment_path, config)
            full_transcript.append(transcript_text)
            # Clean up segment file after transcription, if enabled and it's a temporary segment
            if cleanup_segments and segment_path != audio_path: # Only remove if it's a created segment, not the original file
                os.remove(segment_path)
        except Exception as e:
            print(f"Error transcribing segment {segment_path}: {e}")
            # Depending on error handling strategy, you might want to re-raise or log more
            raise

    print("Transcription complete.")
    return " ".join(full_transcript)

if __name__ == "__main__":
    # Example usage (replace with actual audio file path)
    # For testing, you might need a small audio file first.
    # If you have a long audio file, it will be split.
    example_audio_file = "path/to/your/audio.mp3" # TODO: Replace with a real audio file path for testing
    if os.path.exists(example_audio_file):
        asyncio.run(transcribe_audio_file(example_audio_file))
    else:
        print(f"Error: Example audio file not found at {example_audio_file}")
        print("Please replace 'path/to/your/audio.mp3' with a valid audio file path to test the module.")
