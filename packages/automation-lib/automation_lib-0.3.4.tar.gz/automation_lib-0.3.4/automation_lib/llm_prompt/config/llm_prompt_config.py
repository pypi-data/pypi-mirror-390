import os

from pydantic import AliasChoices, Field
from pydantic_settings import SettingsConfigDict

from automation_lib.config_base import BaseConfig
from automation_lib.config_constants import ModuleConfigConstants

_LLMPromptBaseSettings = BaseConfig.create_settings_class(
    module_base_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
    config_section_name='llm_prompt'
)

class LLMPromptConfig(_LLMPromptBaseSettings):
    model_name: str = Field("gpt-4o-mini", description="The LLM model to use (e.g., 'gpt-4o-mini', 'gemini-pro').")
    openai_api_key: str | None = Field(
        None,
        validation_alias=AliasChoices('OPENAI_API_KEY', 'LLM_PROMPT_OPENAI_API_KEY'),
        description="API key for OpenAI services."
    )
    gemini_api_key: str | None = Field(
        None,
        validation_alias=AliasChoices('GEMINI_API_KEY', 'LLM_PROMPT_GEMINI_API_KEY'),
        description="API key for Google Gemini services."
    )
    temperature: float = Field(0.7, description="Controls the randomness of the output. Higher values mean more random.")
    max_tokens: int | None = Field(None, description="The maximum number of tokens to generate in the completion.")
    timeout: int = Field(60, description="Timeout for the LLM API call in seconds.")
    fallback_delay: float = Field(1.0, description="Delay between fallback attempts in seconds.")
    enable_thinking: bool = Field(False, description="Enable thinking mode for supported models (shows reasoning process).")

    model_config = SettingsConfigDict(
        env_prefix='LLM_PROMPT_',
        env_file=ModuleConfigConstants.DEFAULT_ENV_FILES,  # Use standard .env file order
        extra='ignore'
    )
    
    @staticmethod
    def default() -> 'LLMPromptConfig':
        """Returns a default configuration instance."""
        return LLMPromptConfig() # type: ignore
