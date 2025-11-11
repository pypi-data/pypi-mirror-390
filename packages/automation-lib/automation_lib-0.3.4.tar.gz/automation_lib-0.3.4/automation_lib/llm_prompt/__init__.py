"""
LLM Prompt Module

This module provides functionalities for interacting with various Large Language Models (LLMs).
It includes a flexible provider-based architecture to support different LLM services
like OpenAI and Google Gemini, along with model enums and a fallback mechanism for robustness.
"""

from ..utils.image_schemas import ImageInput
from ..utils.image_utils import download_image_from_url
from .config.llm_prompt_config import LLMPromptConfig
from .llm_prompt_helpers import validate_prompt_input
from .llm_prompt_runner import execute_prompt, execute_prompt_detailed, execute_prompt_with_images, execute_prompt_with_images_detailed
from .model_resolver import ModelResolver
from .models import GeminiModel, ModelType, OpenAIModel
from .schemas.llm_response_schemas import LLMResponse, RateLimitInfo, TokenUsage

__all__ = [
    "GeminiModel",
    "ImageInput",
    "LLMPromptConfig",
    "LLMResponse",
    "ModelResolver",
    "ModelType",
    "OpenAIModel",
    "RateLimitInfo",
    "TokenUsage",
    "download_image_from_url",
    "execute_prompt",
    "execute_prompt_detailed",
    "execute_prompt_with_images",
    "execute_prompt_with_images_detailed",
    "validate_prompt_input"
]
