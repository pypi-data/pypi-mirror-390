"""
Transcription Provider Factory

Factory class for creating transcription provider instances.
"""


from typing import ClassVar

from automation_lib.transcription.config.transcription_config import TranscriptionConfig

from .base_provider import BaseTranscriptionProvider
from .google_cloud_provider import GoogleCloudTranscriptionProvider
from .openai_provider import OpenAITranscriptionProvider


class TranscriptionProviderFactory:
    """
    Factory for creating transcription provider instances.
    """
    
    # Registry of available providers
    _providers: ClassVar[dict[str, type[BaseTranscriptionProvider]]] = {
        "openai": OpenAITranscriptionProvider,
        "google_cloud": GoogleCloudTranscriptionProvider,
    }
    
    @classmethod
    def create_provider(cls, config: TranscriptionConfig) -> BaseTranscriptionProvider:
        """
        Create a transcription provider instance based on configuration.
        
        Args:
            config: TranscriptionConfig object containing provider settings
            
        Returns:
            BaseTranscriptionProvider instance
            
        Raises:
            ValueError: If provider is not supported
        """
        provider_name = config.transcription_provider
        
        if provider_name not in cls._providers:
            available_providers = list(cls._providers.keys())
            raise ValueError(
                f"Unsupported transcription provider: {provider_name}. "
                f"Available providers: {available_providers}"
            )
        
        provider_class = cls._providers[provider_name]
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        Get list of available provider names.
        
        Returns:
            List of provider names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type[BaseTranscriptionProvider]) -> None:
        """
        Register a new transcription provider.
        
        Args:
            name: Provider name
            provider_class: Provider class that extends BaseTranscriptionProvider
        """
        cls._providers[name] = provider_class
    
    @classmethod
    def is_provider_supported(cls, provider_name: str) -> bool:
        """
        Check if a provider is supported.
        
        Args:
            provider_name: Name of the provider to check
            
        Returns:
            True if provider is supported
        """
        return provider_name in cls._providers
