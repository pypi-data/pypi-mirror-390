"""
Test script for the new transcription implementation with provider pattern.
"""

import asyncio
import os

from automation_lib.transcription.config.transcription_config import load_transcription_config
from automation_lib.transcription.transcription_runner import transcribe_audio_file


async def test_transcription():
    """Test the transcription functionality with a sample audio file."""
    
    # Load configuration
    config = load_transcription_config()
    print(f"Loaded config with provider: {config.transcription_provider}")
    
    # Test with a sample audio file (if it exists)
    test_audio_path = "automation_lib/transcription/tests/data/voice_record.m4a"
    
    if os.path.exists(test_audio_path):
        print(f"Testing transcription with: {test_audio_path}")
        try:
            transcript = await transcribe_audio_file(test_audio_path, config=config)
            print(f"Transcription result: {transcript}")
        except Exception as e:
            print(f"Error during transcription: {e}")
    else:
        print(f"Test audio file not found at: {test_audio_path}")
        print("Please provide a valid audio file path to test the transcription.")

if __name__ == "__main__":
    asyncio.run(test_transcription())
