"""
Base Provider Interface

Defines the interface that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from automation_lib.llm_prompt.config.llm_prompt_config import LLMPromptConfig
from automation_lib.llm_prompt.exceptions import RateLimitExceededError
from automation_lib.llm_prompt.schemas.llm_response_schemas import LLMResponse
from automation_lib.utils.image_schemas import ImageInput


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM providers must implement this interface to ensure consistent behavior
    across different LLM services (OpenAI, Gemini, Anthropic, etc.).
    """
    
    def __init__(self, config: LLMPromptConfig):
        """
        Initialize the provider with configuration.
        
        Args:
            config: LLMPromptConfig instance containing provider settings
        """
        self.config = config
        self.validate_config()
    
    @abstractmethod
    def execute_prompt_detailed(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        response_model: type[BaseModel] | None = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute a prompt using the provider's LLM service with detailed response.

        Args:
            prompt: The user prompt to send to the LLM
            model: Optional model override
            system_prompt: Optional system prompt to set context/instructions
            response_model: Optional Pydantic model for structured output
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object containing content and metadata

        Raises:
            Exception: If the LLM API call fails
        """
        raise NotImplementedError("Subclasses must implement execute_prompt_detailed")

    def execute_prompt_detailed_with_fallback(
        self,
        prompt: str,
        model: str,
        fallback_models: list[str],
        system_prompt: str | None = None,
        response_model: type[BaseModel] | None = None,
        **kwargs
    ) -> LLMResponse:
        """
        Executes a prompt with fallback logic for rate limits or other transient errors.
        Returns detailed response with metadata.

        Args:
            prompt: The user prompt to send to the LLM.
            model: The primary model to use.
            fallback_models: A list of fallback model names to try if the primary fails.
            system_prompt: Optional system prompt to set context/instructions.
            response_model: Optional Pydantic model for structured output
            **kwargs: Additional parameters for the LLM API call.

        Returns:
            LLMResponse object containing content and metadata.

        Raises:
            Exception: If all models fail to return a response.
        """
        models_to_try = [model, *fallback_models]

        for i, current_model in enumerate(models_to_try):
            try:
                print(f"Attempting to use model: {current_model} (Attempt {i+1}/{len(models_to_try)})")
                response = self.execute_prompt_detailed(prompt, model=current_model, system_prompt=system_prompt, response_model=response_model, **kwargs)
                return response
            except RateLimitExceededError as e:
                print(f"Model {current_model} failed due to rate limit: {e}")
                last_error = e
                if i < len(models_to_try) - 1:
                    print("Attempting fallback to next model...")
                    import time
                    time.sleep(self.config.fallback_delay)
                else:
                    raise Exception(f"All models failed due to rate limits after {len(models_to_try)} attempts. Last error: {last_error}") from e
            except Exception as e:
                print(f"Model {current_model} failed with unexpected error: {e}")
                raise Exception(f"Model {current_model} failed with unexpected error: {e}") from e

        # This line should ideally not be reached if all exceptions are handled or re-raised
        raise Exception(f"All models failed after {len(models_to_try)} attempts. Last error: {last_error}")
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the provider configuration is correct.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> list[str]:
        """
        Get list of models supported by this provider.
        
        Returns:
            List of supported model names
        """
        pass
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return self.__class__.__name__.replace("Provider", "").lower()
    
    def supports_vision(self) -> bool:
        """
        Check if this provider supports vision/image processing.
        
        Returns:
            True if the provider supports image inputs
        """
        # Default implementation - providers should override if they support vision
        return False
    
    def get_vision_models(self) -> list[str]:
        """
        Get list of models that support vision/image processing.
        
        Returns:
            List of vision-capable model names
        """
        # Default implementation - providers should override
        return []
    
    def execute_prompt_with_images_detailed(
        self,
        prompt: str,
        images: list[ImageInput],
        model: str | None = None,
        system_prompt: str | None = None,
        response_model: type[BaseModel] | None = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute a prompt with image inputs using detailed response.

        Args:
            prompt: The user prompt to send to the LLM
            images: List of ImageInput objects to include
            model: Optional model override
            system_prompt: Optional system prompt to set context/instructions
            response_model: Optional Pydantic model for structured output
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse object containing content and metadata

        Raises:
            NotImplementedError: If the provider doesn't support vision
            Exception: If the LLM API call fails
        """
        if not self.supports_vision():
            raise NotImplementedError(f"Provider {self.get_provider_name()} does not support vision/image processing")

        # Default implementation - providers should override
        raise NotImplementedError("Subclasses must implement execute_prompt_with_images_detailed")
    
    def execute_prompt_with_images_detailed_with_fallback(
        self,
        prompt: str,
        images: list[ImageInput],
        model: str,
        fallback_models: list[str],
        system_prompt: str | None = None,
        response_model: type[BaseModel] | None = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute a prompt with images and fallback logic for rate limits.

        Args:
            prompt: The user prompt to send to the LLM
            images: List of ImageInput objects to include
            model: The primary model to use
            fallback_models: List of fallback model names to try
            system_prompt: Optional system prompt to set context/instructions
            response_model: Optional Pydantic model for structured output
            **kwargs: Additional parameters for the LLM API call

        Returns:
            LLMResponse object containing content and metadata

        Raises:
            Exception: If all models fail to return a response
        """
        if not self.supports_vision():
            raise NotImplementedError(f"Provider {self.get_provider_name()} does not support vision/image processing")

        models_to_try = [model, *fallback_models]

        for i, current_model in enumerate(models_to_try):
            try:
                print(f"Attempting to use vision model: {current_model} (Attempt {i+1}/{len(models_to_try)})")
                response = self.execute_prompt_with_images_detailed(
                    prompt, images, model=current_model, system_prompt=system_prompt, response_model=response_model, **kwargs
                )
                return response
            except RateLimitExceededError as e:
                print(f"Vision model {current_model} failed due to rate limit: {e}")
                last_error = e
                if i < len(models_to_try) - 1:
                    print("Attempting fallback to next vision model...")
                    import time
                    time.sleep(self.config.fallback_delay)
                else:
                    raise Exception(f"All vision models failed due to rate limits after {len(models_to_try)} attempts. Last error: {last_error}") from e
            except Exception as e:
                print(f"Vision model {current_model} failed with unexpected error: {e}")
                raise Exception(f"Vision model {current_model} failed with unexpected error: {e}") from e

        raise Exception(f"All vision models failed after {len(models_to_try)} attempts. Last error: {last_error}")
