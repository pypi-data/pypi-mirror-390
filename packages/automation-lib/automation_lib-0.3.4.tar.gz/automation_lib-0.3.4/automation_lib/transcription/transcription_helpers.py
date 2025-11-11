import math
import os

from pydub import AudioSegment

from automation_lib.transcription.config.transcription_config import TranscriptionConfig
from automation_lib.transcription.providers.provider_factory import TranscriptionProviderFactory

# Define the maximum audio length for OpenAI Whisper (25MB or 25 minutes)
# We'll use 20 minutes as a safe upper bound for splitting to avoid hitting the 25MB limit
# Define the maximum audio length for OpenAI Whisper (25MB or 25 minutes)
# We'll use 20 minutes as a safe upper bound for splitting to avoid hitting the 25MB limit
# This constant is now a fallback/default, as dynamic calculation based on file size is preferred.
DEFAULT_MAX_AUDIO_LENGTH_MINUTES = 20

def get_audio_duration(audio_path: str) -> float:
    """
    Gets the duration of an audio file in minutes.
    """
    audio = AudioSegment.from_file(audio_path)
    return len(audio) / (1000 * 60) # Duration in minutes

def get_file_size_mb(file_path: str) -> float:
    """
    Gets the size of a file in megabytes.
    """
    return os.path.getsize(file_path) / (1024 * 1024)

def split_audio_file(audio_path: str, config: TranscriptionConfig) -> list[str]:
    """
    Splits an audio file into smaller segments based on the provider's maximum file size.
    Returns a list of file paths to the segments.
    """
    audio = AudioSegment.from_file(audio_path)
    total_length_ms = len(audio)
    total_length_minutes = total_length_ms / (1000 * 60)
    
    # Get max file size from provider
    try:
        provider = TranscriptionProviderFactory.create_provider(config)
        max_file_size_mb = provider.get_max_file_size_mb()
    except Exception as e:
        print(f"Warning: Could not get max file size from provider: {e}. Using default.")
        max_file_size_mb = None
    
    # Determine the effective max_length_minutes based on file size if provided
    effective_max_length_minutes = DEFAULT_MAX_AUDIO_LENGTH_MINUTES
    if max_file_size_mb is not None:
        current_file_size_mb = get_file_size_mb(audio_path)
        if current_file_size_mb > 0 and total_length_minutes > 0:
            # Calculate bytes per minute of the original audio
            bytes_per_minute = (current_file_size_mb * 1024 * 1024) / total_length_minutes
            
            # Calculate the duration that corresponds to the max_file_size_mb
            target_bytes = max_file_size_mb * 1024 * 1024
            if bytes_per_minute > 0:
                calculated_max_length_minutes = target_bytes / bytes_per_minute
                # The 20-minute default is no longer a hard cap when max_file_size_mb is provided.
                # The effective max length is now solely determined by the file size calculation.
                effective_max_length_minutes = calculated_max_length_minutes - 1 # Subtract 1 minute to ensure we stay under the limit
            else:
                print("Warning: Bytes per minute is zero, cannot calculate dynamic max length. Using default.")
        else:
            print("Warning: Audio file size or duration is zero, cannot calculate dynamic max length. Using default.")
    
    max_length_ms = effective_max_length_minutes * 60 * 1000

    if total_length_ms <= max_length_ms:
        return [audio_path]

    num_segments = math.ceil(total_length_ms / max_length_ms)
    segment_paths = []
    base_name, ext = os.path.splitext(audio_path)

    for i in range(num_segments):
        start_ms = i * max_length_ms
        end_ms = min((i + 1) * max_length_ms, total_length_ms)
        segment = audio[start_ms:end_ms]
        segment_path = f"{base_name}_part{i+1}{ext}"
        segment.export(segment_path, format=ext[1:]) # Remove the dot from extension
        segment_paths.append(segment_path)
    return segment_paths

async def transcribe_audio_segment(segment_path: str, config: TranscriptionConfig) -> str:
    """
    Transcribes a single audio segment using the configured provider.
    Uses the new provider system for unified interface.
    """
    try:
        # Create provider instance using factory
        provider = TranscriptionProviderFactory.create_provider(config)
        
        # Use provider to transcribe the segment
        return await provider.transcribe_audio_segment(segment_path)
        
    except Exception as e:
        print(f"Error transcribing segment {segment_path} with {config.transcription_provider}: {e}")
        raise
