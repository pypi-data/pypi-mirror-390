# automation_lib/transcription/transcription_config.py

import os
from typing import Literal

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from automation_lib.config_base import BaseConfig
from automation_lib.config_constants import ModuleConfigConstants

# Dynamically create the BaseSettings class for TranscriptionConfig
# This ensures the settings sources are correctly configured for this module
_TranscriptionBaseSettings = BaseConfig.create_settings_class(
    module_base_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
    config_section_name='transcription'
)

# Pydantic model for Transcription Configuration
class TranscriptionConfig(_TranscriptionBaseSettings):
    # General Configuration
    transcription_provider: Literal["openai", "google_cloud"] = Field(
        "openai", description="The transcription provider to use (openai or google_cloud)."
    )
    language: str = Field("de", description="The language of the audio to transcribe.")
    max_audio_length_minutes: int = Field(20, description="Maximum audio length in minutes for transcription.")

    # OpenAI Specific Configuration
    model: str | None = Field("whisper-1", description="The transcription model to use (e.g., 'whisper-1' for OpenAI).")
    openai_api_key: str | None = Field(None, description="OpenAI API key for transcription services.")
    openai_max_file_size_mb: int | None = Field(25, description="Maximum audio file size in MB for OpenAI Whisper.")

    # Google Cloud Specific Configuration (relies on GOOGLE_APPLICATION_CREDENTIALS environment variable)
    google_max_file_size_mb: int | None = Field(10, description="Maximum audio file size in MB for Google Cloud Speech-to-Text.")
    enable_speaker_diarization: bool = Field(
        True, description="Enable speaker diarization for Google Cloud Speech-to-Text."
    )
    min_speaker_count: int | None = Field(
        2, description="Minimum number of speakers for diarization (Google Cloud)."
    )
    max_speaker_count: int | None = Field(
        5, description="Maximum number of speakers for diarization (Google Cloud)."
    )
    audio_encoding: str | None = Field(
        None, description="Explicit audio encoding for Google Cloud Speech-to-Text (e.g., 'LINEAR16', 'FLAC', 'MP3')."
    )
    sample_rate_hertz: int | None = Field(
        None, description="Explicit sample rate in Hertz for Google Cloud Speech-to-Text (e.g., 16000, 44100)."
    )

    model_config = SettingsConfigDict(
        env_prefix='TRANSCRIPTION_', # Prefix for environment variables
        env_file=ModuleConfigConstants.DEFAULT_ENV_FILES, # Load from .env file
        extra='ignore' # Ignore extra fields not defined in the model
    )

def load_transcription_config() -> TranscriptionConfig:
    """
    Loads transcription configuration using Pydantic BaseSettings.
    """
    return TranscriptionConfig()
