
from pydantic import BaseModel

from automation_lib.llm_prompt.config.llm_prompt_config import LLMPromptConfig
from automation_lib.llm_prompt.llm_providers.provider_factory import LLMProviderFactory
from automation_lib.llm_prompt.model_resolver import ModelResolver
from automation_lib.llm_prompt.models import ModelType
from automation_lib.llm_prompt.schemas.llm_response_schemas import LLMResponse
from automation_lib.utils.image_schemas import ImageInput


def execute_prompt_detailed(
    prompt: str,
    model: ModelType | None = None,
    api_key: str | None = None, # This parameter is now largely redundant due to provider-specific API key handling
    config: LLMPromptConfig | None = None,
    system_prompt: str | None = None,
    response_model: type[BaseModel] | None = None,

    **kwargs
) -> LLMResponse:
    """
    Executes a given prompt using the specified LLM model with detailed response including metadata.

    Args:
        prompt (str): The user prompt to send to the LLM.
        model (Optional[ModelType]): The LLM model to use. Can be a string (e.g., "gpt-4o-mini")
                                     or an Enum member (e.g., OpenAIModel.GPT_4O_MINI).
                                     If None, the default model from configuration will be used.
        api_key (Optional[str]): DEPRECATED: This parameter is now largely redundant. API keys
                                 are handled by the provider-specific configuration.
        config (Optional[LLMPromptConfig]): The configuration object for LLM prompts.
        system_prompt (Optional[str]): Optional system prompt to set context/instructions for the LLM.
        **kwargs: Additional parameters to pass to the LLM completion API
                  (e.g., temperature, max_tokens, top_p, etc.).

    Returns:
        LLMResponse: Detailed response object containing content, token usage, rate limits, and other metadata.

    Raises:
        Exception: If the LLM API call fails or returns an error.
    """
    if config is None:
        config = LLMPromptConfig.default()

    # Resolve the model name and its fallback models
    resolved_model_name, fallback_models = ModelResolver.resolve_model(
        model if model is not None else config.model_name
    )

    # If api_key is explicitly passed, it takes precedence for the initial call
    # However, providers will primarily use keys from config
    if api_key is not None:
        # This might override a config-loaded key for this specific call,
        # but the primary mechanism is via config.
        # For now, we'll let the provider handle its own API key logic.
        pass

    try:
        # Create the provider using the resolved model name
        provider = LLMProviderFactory.create_provider(resolved_model_name, config)
        
        # Execute prompt with potential fallback logic and get detailed response
        response = provider.execute_prompt_detailed_with_fallback(
            prompt,
            model=resolved_model_name,
            fallback_models=fallback_models,
            system_prompt=system_prompt,
            response_model=response_model,
            **kwargs
        )
        return response
    except Exception as e:
        print(f"Error executing LLM prompt: {e}")
        raise

def execute_prompt_with_images_detailed(
    prompt: str,
    images: list[ImageInput],
    model: ModelType | None = None,
    api_key: str | None = None,
    config: LLMPromptConfig | None = None,
    system_prompt: str | None = None,
    **kwargs
) -> LLMResponse:
    """
    Executes a prompt with image inputs using the specified LLM model with detailed response.

    Args:
        prompt (str): The user prompt to send to the LLM.
        images (List[ImageInput]): List of ImageInput objects to include with the prompt.
        model (Optional[ModelType]): The LLM model to use. Can be a string (e.g., "gpt-4o")
                                     or an Enum member (e.g., OpenAIModel.GPT_4O).
                                     If None, the default model from configuration will be used.
        api_key (Optional[str]): DEPRECATED: This parameter is now largely redundant. API keys
                                 are handled by the provider-specific configuration.
        config (Optional[LLMPromptConfig]): The configuration object for LLM prompts.
        system_prompt (Optional[str]): Optional system prompt to set context/instructions for the LLM.
        **kwargs: Additional parameters to pass to the LLM completion API
                  (e.g., temperature, max_tokens, top_p, etc.).

    Returns:
        LLMResponse: Detailed response object containing content, token usage, rate limits, and other metadata.

    Raises:
        Exception: If the LLM API call fails or returns an error.
        ValueError: If the model doesn't support vision or no images are provided.
    """
    if config is None:
        config = LLMPromptConfig.default()
        
        if not images:
            raise ValueError("At least one image must be provided for vision prompts")

    # Resolve the model name and its fallback models
    resolved_model_name, fallback_models = ModelResolver.resolve_model(
        model if model is not None else config.model_name
    )

    try:
        # Create the provider using the resolved model name
        provider = LLMProviderFactory.create_provider(resolved_model_name, config)
        
        # Check if provider supports vision
        if not provider.supports_vision():
            raise ValueError(f"Provider {provider.get_provider_name()} does not support vision/image processing")
        
        # Check if the resolved model supports vision
        vision_models = provider.get_vision_models()
        if resolved_model_name not in vision_models:
            # Try to find a vision-capable fallback model
            vision_fallbacks = [m for m in fallback_models if m in vision_models]
            if not vision_fallbacks:
                raise ValueError(f"Model {resolved_model_name} does not support vision. Available vision models: {vision_models}")
            
            # Use the first vision-capable fallback as primary
            resolved_model_name = vision_fallbacks[0]
            fallback_models = vision_fallbacks[1:]
        
        # Execute prompt with images and potential fallback logic
        response = provider.execute_prompt_with_images_detailed_with_fallback(
            prompt,
            images,
            model=resolved_model_name,
            fallback_models=fallback_models,
            system_prompt=system_prompt,
            **kwargs
        )
        return response
    except Exception as e:
        print(f"Error executing LLM prompt with images: {e}")
        raise
