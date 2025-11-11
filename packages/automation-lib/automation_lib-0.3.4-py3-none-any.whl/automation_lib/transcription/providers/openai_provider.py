"""
OpenAI Transcription Provider

Implementation of BaseTranscriptionProvider for OpenAI Whisper.
"""

import os

import openai

from automation_lib.transcription.config.transcription_config import TranscriptionConfig

from .base_provider import BaseTranscriptionProvider


class OpenAITranscriptionProvider(BaseTranscriptionProvider):
    """
    Provider for OpenAI Whisper transcription using the official openai library.
    """
    
    def __init__(self, config: TranscriptionConfig):
        """Initialize OpenAI transcription provider with configuration."""
        super().__init__(config)
        self.client = openai.OpenAI(api_key=self.config.openai_api_key)
    
    def validate_config(self) -> bool:
        """
        Validate OpenAI configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If required configuration is missing
        """
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        
        if not self.config.model:
            raise ValueError("OpenAI transcription requires a 'model' to be specified in the configuration")
        
        return True
    
    async def transcribe_audio_segment(self, segment_path: str) -> str:
        """
        Transcribe a single audio segment using OpenAI Whisper.
        
        Args:
            segment_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        # Store original environment variables
        original_openai_key = os.getenv("OPENAI_API_KEY")
        original_google_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        try:
            # Set OpenAI API key
            if self.config.openai_api_key:
                os.environ["OPENAI_API_KEY"] = self.config.openai_api_key
            else:
                # If config.openai_api_key is None, ensure the env var is also unset
                if "OPENAI_API_KEY" in os.environ:
                    del os.environ["OPENAI_API_KEY"]
            
            # Temporarily unset Google Cloud credentials to prevent conflicts
            if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
            
            with open(segment_path, "rb") as audio_file:
                # Ensure model is not None (already validated in validate_config)
                model = self.config.model
                if model is None:
                    raise ValueError("Model cannot be None")
                
                transcript_response = self.client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    language=self.config.language
                )
            
            if transcript_response.text is None:
                raise ValueError("Transcription returned no text")
            
            return transcript_response.text
            
        except Exception as e:
            print(f"Error transcribing segment {segment_path} with OpenAI: {e}")
            raise
        finally:
            # Restore original environment variables
            if original_openai_key is not None:
                os.environ["OPENAI_API_KEY"] = original_openai_key
            elif "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]

            if original_google_credentials is not None:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = original_google_credentials
            elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    
    def get_max_file_size_mb(self) -> int | None:
        """
        Get the maximum file size supported by OpenAI Whisper.
        
        Returns:
            Maximum file size in MB
        """
        return self.config.openai_max_file_size_mb or 25
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return "openai"
    
    def supports_language(self, language: str) -> bool:
        """
        Check if OpenAI Whisper supports the given language.
        
        Args:
            language: Language code (e.g., 'de', 'en')
            
        Returns:
            True if language is supported (OpenAI Whisper supports many languages)
        """
        # OpenAI Whisper supports a wide range of languages
        # For simplicity, we return True here, but this could be enhanced
        # with a specific list of supported language codes
        return True
    
    def supports_speaker_diarization(self) -> bool:
        """
        Check if OpenAI Whisper supports speaker diarization.
        
        Returns:
            False (OpenAI Whisper does not support speaker diarization)
        """
        return False
