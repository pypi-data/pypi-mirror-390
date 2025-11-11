"""
Gemini Provider

Implementation of LLMProvider for Google's Gemini models using the new google.genai API.
"""

import time
from datetime import datetime

from google import genai
from google.api_core import exceptions as google_exceptions
from google.genai import types

from ...utils.image_schemas import ImageInput
from ..exceptions import EmptyResponseError, RateLimitExceededError
from ..models import GeminiModel
from ..schemas.llm_response_schemas import LLMResponse, RateLimitInfo, TokenUsage
from .base_provider import LLMProvider


class GeminiProvider(LLMProvider):
    """
    Provider for Google Gemini models using the new google.genai library.
    """
    
    def __init__(self, config):
        """Initialize Gemini provider with configuration."""
        super().__init__(config)
        self.client = genai.Client(api_key=self.config.gemini_api_key)
    
    def validate_config(self) -> bool:
        """
        Validate Gemini configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If API key is missing
        """
        if not self.config.gemini_api_key:
            raise ValueError("Gemini API key is required but not provided")
        return True
    
    def get_supported_models(self) -> list[str]:
        """
        Get list of supported Gemini models.
        
        Returns:
            List of supported model names
        """
        return GeminiModel.get_all_model_names()
    
    def supports_vision(self) -> bool:
        """
        Check if this provider supports vision/image processing.
        
        Returns:
            True since Gemini supports vision
        """
        return True
    
    def get_vision_models(self) -> list[str]:
        """
        Get list of Gemini models that support vision/image processing.
        
        Returns:
            List of vision-capable model names
        """
        # Alle Gemini-Modelle unterstützen Vision
        return self.get_supported_models()
    
    def _is_gemini_2_5_model(self, model_name: str) -> bool:
        """
        Check if the model is a Gemini 2.5 model that supports thinking configuration.
        
        Args:
            model_name: The model name to check
            
        Returns:
            True if it's a Gemini 2.5 model
        """
        model_name_lower = model_name.lower()
        return "2.5" in model_name_lower or "gemini-2.5" in model_name_lower
    
    def execute_prompt_detailed(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute a prompt using Gemini's API with detailed response.
        
        Args:
            prompt: The user prompt to send to the LLM
            model: Optional model override
            system_prompt: Optional system prompt to set context/instructions
            **kwargs: Additional Gemini-specific parameters
            
        Returns:
            LLMResponse object containing content and metadata
            
        Raises:
            Exception: If the Gemini API call fails
        """
        # Use provided model or default from config
        final_model = model if model is not None else self.config.model_name
        
        # Remove "gemini-" prefix if present for the API call
        if final_model.startswith("gemini-"):
            api_model_name = final_model
        else:
            api_model_name = f"gemini-{final_model}"
        
        # Record start time for response time calculation
        start_time = time.time()
        
        try:
            # Prepare the content
            contents = [prompt]
            
            # Prepare generation config
            generation_config = types.GenerateContentConfig()
            
            # Add config parameters if not overridden by kwargs
            if "temperature" not in kwargs:
                generation_config.temperature = self.config.temperature
            
            # Handle max_tokens parameter, mapping it to max_output_tokens for Gemini
            if "max_tokens" in kwargs:
                generation_config.max_output_tokens = kwargs.pop("max_tokens")
            elif self.config.max_tokens is not None:
                generation_config.max_output_tokens = self.config.max_tokens
            
            # Configure thinking for Gemini 2.5 models
            if self._is_gemini_2_5_model(api_model_name):
                # Check if thinking should be enabled (default is False)
                enable_thinking = getattr(self.config, 'enable_thinking', False)
                
                if not enable_thinking:
                    # Disable thinking by setting includeThoughts to False
                    generation_config.thinking_config = types.ThinkingConfig(include_thoughts=False)
            
            # Add system instruction if provided
            if system_prompt:
                generation_config.system_instruction = system_prompt
            
            # Merge remaining kwargs (Gemini-specific parameters)
            for key, value in kwargs.items():
                if hasattr(generation_config, key):
                    setattr(generation_config, key, value)
            
            # Generate response
            response = self.client.models.generate_content(
                model=api_model_name,
                contents=contents,
                config=generation_config
            )
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract content from response
            if not response.text or response.text.strip() == "":
                raise EmptyResponseError("Gemini returned an empty response")
            
            # Extract token usage from response
            token_usage = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                token_usage = TokenUsage(
                    prompt_tokens=getattr(response.usage_metadata, 'prompt_token_count', 0),
                    completion_tokens=getattr(response.usage_metadata, 'candidates_token_count', 0),
                    total_tokens=getattr(response.usage_metadata, 'total_token_count', 0)
                )
            
            # Extract finish reason
            finish_reason = None
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = str(candidate.finish_reason)
            
            # Extract rate limit info (Gemini doesn't provide this in response)
            rate_limit_info = self._extract_rate_limit_info(response)
                
            llm_response = LLMResponse(
                content=response.text,
                model=final_model,
                provider=self.get_provider_name(),
                token_usage=token_usage,
                rate_limit_info=rate_limit_info,
                response_time_ms=response_time_ms,
                finish_reason=finish_reason,
                request_id=None,  # Gemini doesn't provide request IDs
                created_at=datetime.now(),
                raw_response=self._convert_response_to_dict(response)
            )
            
            return llm_response
            
        except google_exceptions.ResourceExhausted as e:
            raise RateLimitExceededError(f"Gemini rate limit exceeded: {e}", original_exception=e) from e
        except Exception as e:
            raise Exception(f"Gemini API call failed: {e}") from e

    def _extract_rate_limit_info(self, response) -> RateLimitInfo | None:
        """
        Extract rate limit information from Gemini response.
        
        Args:
            response: Gemini API response object
            
        Returns:
            RateLimitInfo object or None if not available
        """
        # Gemini doesn't typically provide rate limit information in the response
        # This could be extended if such information becomes available
        return None

    def _convert_response_to_dict(self, response) -> dict | None:
        """
        Convert Gemini response to dictionary for raw_response field.
        
        Args:
            response: Gemini API response object
            
        Returns:
            Dictionary representation or None if conversion fails
        """
        try:
            # Try to convert response to dict for debugging purposes
            response_dict = {
                "text": response.text,
                "candidates": []
            }
            
            if hasattr(response, 'candidates') and response.candidates:
                for candidate in response.candidates:
                    candidate_dict = {
                        "content": getattr(candidate, 'content', None),
                        "finish_reason": str(getattr(candidate, 'finish_reason', None))
                    }
                    response_dict["candidates"].append(candidate_dict)
            
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                response_dict["usage_metadata"] = {
                    "prompt_token_count": getattr(response.usage_metadata, 'prompt_token_count', None),
                    "candidates_token_count": getattr(response.usage_metadata, 'candidates_token_count', None),
                    "total_token_count": getattr(response.usage_metadata, 'total_token_count', None)
                }
            
            return response_dict
        except Exception:
            # If conversion fails, return None
            return None
    
    def execute_prompt_with_images_detailed(
        self,
        prompt: str,
        images: list[ImageInput],
        model: str | None = None,
        system_prompt: str | None = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute a prompt with image inputs using Gemini's vision capabilities.
        
        Args:
            prompt: The user prompt to send to the LLM
            images: List of ImageInput objects to include
            model: Optional model override
            system_prompt: Optional system prompt to set context/instructions
            **kwargs: Additional Gemini-specific parameters
            
        Returns:
            LLMResponse object containing content and metadata
            
        Raises:
            Exception: If the Gemini API call fails
        """
        # Use provided model or default from config
        final_model = model if model is not None else self.config.model_name
        
        # Remove "gemini-" prefix if present for the API call
        if final_model.startswith("gemini-"):
            api_model_name = final_model
        else:
            api_model_name = f"gemini-{final_model}"
        
        # Record start time for response time calculation
        start_time = time.time()
        
        try:
            # Prepare the content with images
            contents = []
            
            # Add images first
            for image_input in images:
                image_bytes = image_input.to_bytes()
                mime_type = image_input.detected_mime_type or "image/jpeg"
                
                # Create Gemini image part
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                )
                contents.append(image_part)
            
            # Add text prompt
            contents.append(prompt)
            
            # Prepare generation config
            generation_config = types.GenerateContentConfig()
            
            # Add config parameters if not overridden by kwargs
            if "temperature" not in kwargs:
                generation_config.temperature = self.config.temperature
            
            # Handle max_tokens parameter, mapping it to max_output_tokens for Gemini
            if "max_tokens" in kwargs:
                generation_config.max_output_tokens = kwargs.pop("max_tokens")
            elif self.config.max_tokens is not None:
                generation_config.max_output_tokens = self.config.max_tokens
            
            # Configure thinking for Gemini 2.5 models
            if self._is_gemini_2_5_model(api_model_name):
                # Check if thinking should be enabled (default is False)
                enable_thinking = getattr(self.config, 'enable_thinking', False)
                
                if not enable_thinking:
                    # Disable thinking by setting includeThoughts to False
                    generation_config.thinking_config = types.ThinkingConfig(include_thoughts=False)
            
            # Add system instruction if provided
            if system_prompt:
                generation_config.system_instruction = system_prompt
            
            # Merge remaining kwargs (Gemini-specific parameters)
            for key, value in kwargs.items():
                if hasattr(generation_config, key):
                    setattr(generation_config, key, value)
            
            # Generate response
            response = self.client.models.generate_content(
                model=api_model_name,
                contents=contents,
                config=generation_config
            )
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract content from response
            if not response.text or response.text.strip() == "":
                raise EmptyResponseError("Gemini returned an empty response")
            
            # Extract token usage from response
            token_usage = None
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                token_usage = TokenUsage(
                    prompt_tokens=getattr(response.usage_metadata, 'prompt_token_count', 0),
                    completion_tokens=getattr(response.usage_metadata, 'candidates_token_count', 0),
                    total_tokens=getattr(response.usage_metadata, 'total_token_count', 0)
                )
            
            # Extract finish reason
            finish_reason = None
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = str(candidate.finish_reason)
            
            # Extract rate limit info (Gemini doesn't provide this in response)
            rate_limit_info = self._extract_rate_limit_info(response)
                
            llm_response = LLMResponse(
                content=response.text,
                model=final_model,
                provider=self.get_provider_name(),
                token_usage=token_usage,
                rate_limit_info=rate_limit_info,
                response_time_ms=response_time_ms,
                finish_reason=finish_reason,
                request_id=None,  # Gemini doesn't provide request IDs
                created_at=datetime.now(),
                raw_response=self._convert_response_to_dict(response)
            )
            
            return llm_response
            
        except google_exceptions.ResourceExhausted as e:
            raise RateLimitExceededError(f"Gemini rate limit exceeded: {e}", original_exception=e) from e
        except Exception as e:
            raise Exception(f"Gemini API call with images failed: {e}") from e
