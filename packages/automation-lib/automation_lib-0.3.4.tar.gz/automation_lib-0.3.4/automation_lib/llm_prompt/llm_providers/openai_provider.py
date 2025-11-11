"""
OpenAI Provider

Implementation of LLMProvider for OpenAI's GPT models.
"""

import base64
import time
from datetime import datetime

import openai
from pydantic import BaseModel

from ...utils.image_schemas import ImageInput
from ..exceptions import RateLimitExceededError
from ..models import OpenAIModel
from ..schemas.llm_response_schemas import LLMResponse, RateLimitInfo, TokenUsage
from .base_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """
    Provider for OpenAI GPT models using the official openai library.
    """
    
    def __init__(self, config):
        """Initialize OpenAI provider with configuration."""
        super().__init__(config)
        self.client = openai.OpenAI(api_key=self.config.openai_api_key)
    
    def validate_config(self) -> bool:
        """
        Validate OpenAI configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If API key is missing
        """
        if not self.config.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        return True
    
    def get_supported_models(self) -> list[str]:
        """
        Get list of supported OpenAI models.
        
        Returns:
            List of supported model names
        """
        return OpenAIModel.get_all_model_names()
    
    def supports_vision(self) -> bool:
        """
        Check if this provider supports vision/image processing.
        
        Returns:
            True since OpenAI supports vision
        """
        return True
    
    def get_vision_models(self) -> list[str]:
        """
        Get list of OpenAI models that support vision/image processing.
        
        Returns:
            List of vision-capable model names
        """
        # Nur GPT-4 Vision Modelle unterstützen Bilder
        vision_models = []
        for model in self.get_supported_models():
            if "vision" in model.lower() or "gpt-4o" in model.lower() or "gpt-4-turbo" in model.lower():
                vision_models.append(model)
        return vision_models
    
    def execute_prompt_detailed(
        self,
        prompt: str,
        model: str | None = None,
        system_prompt: str | None = None,
        response_model: type[BaseModel] | None = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute a prompt using OpenAI's API with detailed response.
        
        Args:
            prompt: The user prompt to send to the LLM
            model: Optional model override
            system_prompt: Optional system prompt to set context/instructions
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            LLMResponse object containing content and metadata
            
        Raises:
            Exception: If the OpenAI API call fails
        """
        # Use provided model or default from config
        final_model = model if model is not None else self.config.model_name
        
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user message
        messages.append({"role": "user", "content": prompt})
        
        # Prepare API call parameters
        api_params = {
            "model": final_model,
            "messages": messages,
        }
        
        # Add config parameters if not overridden by kwargs
        if "temperature" not in kwargs:
            api_params["temperature"] = self.config.temperature
        if "max_tokens" not in kwargs and self.config.max_tokens is not None:
            api_params["max_tokens"] = self.config.max_tokens
        if "timeout" not in kwargs:
            api_params["timeout"] = self.config.timeout
        
        # Handle structured output if response_model is provided
        if response_model:
            api_params["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "schema": response_model.model_json_schema(),
                    "strict": True
                }
            }

        # Record start time for response time calculation
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(**api_params)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Extract content from response
            if response_model and hasattr(response.choices[0].message, 'parsed') and response.choices[0].message.parsed:
                # Structured output - parse the response
                content = response_model.model_validate(response.choices[0].message.parsed)
                response_schema = response_model.model_json_schema()
            else:
                # Regular text output
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("OpenAI response content was None")
                response_schema = None

            # Extract token usage
            token_usage = None
            if response.usage:
                token_usage = TokenUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens
                )

            # Extract rate limit info from response headers (if available)
            rate_limit_info = self._extract_rate_limit_info(response)

            # Create LLMResponse object
            llm_response = LLMResponse(
                content=content,
                model=final_model,
                provider=self.get_provider_name(),
                token_usage=token_usage,
                rate_limit_info=rate_limit_info,
                response_time_ms=response_time_ms,
                finish_reason=response.choices[0].finish_reason,
                request_id=getattr(response, 'id', None),
                created_at=datetime.fromtimestamp(response.created) if hasattr(response, 'created') else datetime.now(),
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                response_schema=response_schema
            )

            return llm_response
            
        except openai.RateLimitError as e:
            raise RateLimitExceededError(f"OpenAI rate limit exceeded: {e}", original_exception=e) from e
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}") from e

    def _extract_rate_limit_info(self, response) -> RateLimitInfo | None:
        """
        Extract rate limit information from OpenAI response headers.
        
        Args:
            response: OpenAI API response object
            
        Returns:
            RateLimitInfo object or None if not available
        """
        # Note: OpenAI doesn't always provide rate limit headers in the response object
        # This would need to be implemented with access to the raw HTTP response headers
        # For now, return None - can be extended when header access is available
        return None
    
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
        Execute a prompt with image inputs using OpenAI's vision capabilities.
        
        Args:
            prompt: The user prompt to send to the LLM
            images: List of ImageInput objects to include
            model: Optional model override
            system_prompt: Optional system prompt to set context/instructions
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            LLMResponse object containing content and metadata
            
        Raises:
            Exception: If the OpenAI API call fails
        """
        # Use provided model or default from config
        final_model = model if model is not None else self.config.model_name
        
        # Validate that the model supports vision
        if final_model not in self.get_vision_models():
            raise ValueError(f"Model {final_model} does not support vision. Supported vision models: {self.get_vision_models()}")
        
        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Prepare user message with images
        user_content = []
        
        # Add images first
        for image_input in images:
            image_bytes = image_input.to_bytes()
            mime_type = image_input.detected_mime_type or "image/jpeg"
            
            # Encode image to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Create image content for OpenAI
            image_content = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_image}"
                }
            }
            user_content.append(image_content)
        
        # Add text prompt
        user_content.append({
            "type": "text",
            "text": prompt
        })
        
        # Add user message with mixed content
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        # Prepare API call parameters
        api_params = {
            "model": final_model,
            "messages": messages,
        }
        
        # Add config parameters if not overridden by kwargs
        if "temperature" not in kwargs:
            api_params["temperature"] = self.config.temperature
        if "max_tokens" not in kwargs and self.config.max_tokens is not None:
            api_params["max_tokens"] = self.config.max_tokens
        if "timeout" not in kwargs:
            api_params["timeout"] = self.config.timeout
        
        # Handle structured output if response_model is provided
        if response_model:
            api_params["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "schema": response_model.model_json_schema(),
                    "strict": True
                }
            }

        # Record start time for response time calculation
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(**api_params)

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Extract content from response
            if response_model and hasattr(response.choices[0].message, 'parsed') and response.choices[0].message.parsed:
                # Structured output - parse the response
                content = response_model.model_validate(response.choices[0].message.parsed)
                response_schema = response_model.model_json_schema()
            else:
                # Regular text output
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("OpenAI response content was None")
                response_schema = None

            # Extract token usage
            token_usage = None
            if response.usage:
                token_usage = TokenUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens
                )

            # Extract rate limit info from response headers (if available)
            rate_limit_info = self._extract_rate_limit_info(response)

            # Create LLMResponse object
            llm_response = LLMResponse(
                content=content,
                model=final_model,
                provider=self.get_provider_name(),
                token_usage=token_usage,
                rate_limit_info=rate_limit_info,
                response_time_ms=response_time_ms,
                finish_reason=response.choices[0].finish_reason,
                request_id=getattr(response, 'id', None),
                created_at=datetime.fromtimestamp(response.created) if hasattr(response, 'created') else datetime.now(),
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None,
                response_schema=response_schema
            )

            return llm_response
            
        except openai.RateLimitError as e:
            raise RateLimitExceededError(f"OpenAI rate limit exceeded: {e}", original_exception=e) from e
        except Exception as e:
            raise Exception(f"OpenAI API call with images failed: {e}") from e
