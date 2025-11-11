# automation_lib/transcription/examples/minimal_usage.py

import asyncio
import os

from dotenv import load_dotenv

from automation_lib.transcription.config.transcription_config import load_transcription_config
from automation_lib.transcription.transcription_runner import transcribe_audio_file


async def main():
    load_dotenv() # Load environment variables from .env file

    # --- Example 1: Using OpenAI (default provider) ---
    print("--- Running OpenAI Transcription Example ---")
    openai_audio_file_path = "automation_lib/transcription/tests/data/voice_record.m4a"

    if not os.path.exists(openai_audio_file_path):
        print(f"Error: OpenAI audio file not found at '{openai_audio_file_path}'")
        print("Please ensure 'voice_record.m4a' exists or update the path.")
    else:
        # The configuration will be loaded from default_config.yaml and .env
        # Ensure TRANSCRIPTION_TRANSCRIPTION_PROVIDER is "openai" and TRANSCRIPTION_OPENAI_API_KEY is set in your .env
        print(f"Transcribing with OpenAI: {openai_audio_file_path}")
        openai_transcript = await transcribe_audio_file(openai_audio_file_path, cleanup_segments=False)
        print("\nOpenAI Transcript:")
        print(openai_transcript)
        print("-" * 50)

    # --- Example 2: Using Google Cloud Speech-to-Text with Diarization ---
    print("\n--- Running Google Cloud Transcription Example with Diarization ---")
    google_cloud_audio_file_path = "automation_lib/transcription/tests/data/audio-aufnahme-zwei-sprecher.m4a"

    if not os.path.exists(google_cloud_audio_file_path):
        print(f"Error: Google Cloud audio file not found at '{google_cloud_audio_file_path}'")
        print("Please ensure 'audio-aufnahme-zwei-sprecher.m4a' exists or update the path.")
    else:
        # To use Google Cloud, you need to:
        # 1. Set TRANSCRIPTION_TRANSCRIPTION_PROVIDER="google_cloud" in your .env file.
        # 2. Set TRANSCRIPTION_GOOGLE_CLOUD_CREDENTIALS_PATH to your service account key JSON file.
        #    (e.g., TRANSCRIPTION_GOOGLE_CLOUD_CREDENTIALS_PATH="/path/to/your/key.json")
        # 3. Optionally, set TRANSCRIPTION_ENABLE_SPEAKER_DIARIZATION="true"
        #    and TRANSCRIPTION_MIN_SPEAKER_COUNT/TRANSCRIPTION_MAX_SPEAKER_COUNT.

        # For this example, we'll temporarily override the config to force Google Cloud with diarization.
        # In a real application, you'd manage this via .env or default_config.yaml.
        print(f"Transcribing with Google Cloud: {google_cloud_audio_file_path}")
        
        # Load current config
        current_config = load_transcription_config()
        
        # Temporarily modify config for this example
        original_provider = current_config.transcription_provider
        original_diarization = current_config.enable_speaker_diarization
        original_min_speakers = current_config.min_speaker_count
        original_max_speakers = current_config.max_speaker_count

        try:
            # Set Google Cloud specific settings for this run
            current_config.transcription_provider = "google_cloud"
            # Google Cloud credentials are now handled uniformly via GOOGLE_APPLICATION_CREDENTIALS
            # environment variable, which the client library automatically picks up.
            current_config.enable_speaker_diarization = True
            current_config.min_speaker_count = 1
            current_config.max_speaker_count = 2

            # Note: The transcribe_audio_file function loads its own config.
            # For simplicity, this example assumes you've set the .env variables correctly for Google Cloud.
            # If you want to test this example, ensure your .env has:
            # TRANSCRIPTION_TRANSCRIPTION_PROVIDER="google_cloud"
            # GOOGLE_APPLICATION_CREDENTIALS="path/to/your/google-cloud-service-account-key.json"
            # TRANSCRIPTION_ENABLE_SPEAKER_DIARIZATION="true"
            # TRANSCRIPTION_MIN_SPEAKER_COUNT="1"
            # TRANSCRIPTION_MAX_SPEAKER_COUNT="2"

            # Call the main transcription function
            google_cloud_transcript = await transcribe_audio_file(google_cloud_audio_file_path, cleanup_segments=False)
            print("\nGoogle Cloud Transcript:")
            print(google_cloud_transcript)
        except Exception as e:
            print(f"Error during Google Cloud transcription: {e}")
        finally:
            # Restore original config values (important if running multiple examples or in a larger app)
            current_config.transcription_provider = original_provider
            current_config.enable_speaker_diarization = original_diarization
            current_config.min_speaker_count = original_min_speakers
            current_config.max_speaker_count = original_max_speakers
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
