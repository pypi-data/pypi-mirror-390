"""
Base Transcription Provider

Abstract base class for all transcription providers.
"""

from abc import ABC, abstractmethod

from automation_lib.transcription.config.transcription_config import TranscriptionConfig


class BaseTranscriptionProvider(ABC):
    """
    Abstract base class for transcription providers.
    """
    
    def __init__(self, config: TranscriptionConfig):
        """
        Initialize the transcription provider with configuration.
        
        Args:
            config: TranscriptionConfig object containing provider settings
        """
        self.config = config
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider-specific configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    async def transcribe_audio_segment(self, segment_path: str) -> str:
        """
        Transcribe a single audio segment.
        
        Args:
            segment_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        pass
    
    @abstractmethod
    def get_max_file_size_mb(self) -> int | None:
        """
        Get the maximum file size supported by this provider.
        
        Returns:
            Maximum file size in MB, or None if no limit
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name string
        """
        pass
    
    def supports_language(self, language: str) -> bool:
        """
        Check if the provider supports the given language.
        
        Args:
            language: Language code (e.g., 'de', 'en')
            
        Returns:
            True if language is supported
        """
        # Default implementation - can be overridden by specific providers
        return True
    
    def supports_speaker_diarization(self) -> bool:
        """
        Check if the provider supports speaker diarization.
        
        Returns:
            True if speaker diarization is supported
        """
        # Default implementation - can be overridden by specific providers
        return False
