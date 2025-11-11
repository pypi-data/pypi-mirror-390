"""
LLM Provider Factory

Responsible for creating the correct LLMProvider instance based on the model name.
"""

from automation_lib.llm_prompt.config.llm_prompt_config import LLMPromptConfig

from .base_provider import LLMProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider


class LLMProviderFactory:
    """
    Factory class to create instances of LLMProvider based on the model name.
    """
    
    @staticmethod
    def create_provider(model_name: str, config: LLMPromptConfig) -> LLMProvider:
        """
        Creates and returns an LLMProvider instance for the given model name.
        
        Args:
            model_name: The name of the LLM model (e.g., "gpt-4o-mini", "gemini-1.5-pro").
            config: The LLMPromptConfig instance containing API keys and other settings.
            
        Returns:
            An instance of a concrete LLMProvider (e.g., OpenAIProvider, GeminiProvider).
            
        Raises:
            ValueError: If no suitable provider is found for the given model name.
        """
        if model_name.startswith(("gpt", "o1", "o3")):
            return OpenAIProvider(config)
        elif model_name.startswith("gemini"):
            return GeminiProvider(config)
        else:
            raise ValueError(f"No suitable LLM provider found for model: {model_name}")
