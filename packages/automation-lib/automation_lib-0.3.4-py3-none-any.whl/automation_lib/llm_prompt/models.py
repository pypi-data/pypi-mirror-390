"""
LLM Model Enums

Defines enums for OpenAI and Gemini models with their respective fallback models.
"""

from enum import Enum
from typing import Optional


class OpenAIModel(Enum):
    """
    Enum for OpenAI models with their fallback options.
    """
    GPT_4O = ("gpt-4o", ["gpt-4o-mini", "gpt-4-turbo"])
    GPT_4O_MINI = ("gpt-4o-mini", ["gpt-3.5-turbo"])
    GPT_41_MINI = ("gpt-4.1-mini", ["gpt-4o-mini", "gpt-4.1-nano", "gpt-3.5-mini"])
    GPT_41_NANO = ("gpt-4.1-nano", ["gpt-4o-mini", "gpt-3.5-mini"])
    GPT_4_TURBO = ("gpt-4-turbo", ["gpt-4", "gpt-4o-mini"])
    GPT_4 = ("gpt-4", ["gpt-4-turbo", "gpt-4o-mini"])
    O1_PREVIEW = ("o1-preview", ["o1-mini"])
    O1_MINI = ("o1-mini", ["gpt-4o-mini"])
    
    def __init__(self, model_name: str, fallback_models: list[str]):
        self._model_name = model_name
        self._fallback_models = fallback_models

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def fallback_models(self) -> list[str]:
        return self._fallback_models

    @classmethod
    def from_string(cls, model_name: str) -> Optional['OpenAIModel']:
        """
        Finds an OpenAIModel enum member based on its model_name string.
        """
        for model in cls:
            if model.model_name == model_name:
                return model
        return None
    
    @classmethod
    def get_all_model_names(cls) -> list[str]:
        """
        Returns a list of all available OpenAI model names.
        """
        return [model.model_name for model in cls]


class GeminiModel(Enum):
    """
    Enum for Gemini models with their fallback options.
    """
    GEMINI_2_5_PRO = ("gemini-2.5-pro", ["gemini-2.5-flash", "gemini-2.0-pro"])
    GEMINI_2_5_FLASH = ("gemini-2.5-flash", ["gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-2.0-flash"])
    GEMINI_2_0_FLASH = ("gemini-2.0-flash", ["gemini-2.0-flash-lite", "gemini-2.0-pro"])
    GEMINI_2_0_FLASH_LITE = ("gemini-2.0-flash-lite", ["gemini-2.0-flash"])
    GEMINI_2_0_PRO = ("gemini-2.0-pro", ["gemini-2.0-flash"])
    
    def __init__(self, model_name: str, fallback_models: list[str]):
        self._model_name = model_name
        self._fallback_models = fallback_models

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def fallback_models(self) -> list[str]:
        return self._fallback_models

    @classmethod
    def from_string(cls, model_name: str) -> Optional['GeminiModel']:
        """
        Finds a GeminiModel enum member based on its model_name string.
        """
        for model in cls:
            if model.model_name == model_name:
                return model
        return None
    
    @classmethod
    def get_all_model_names(cls) -> list[str]:
        """
        Returns a list of all available Gemini model names.
        """
        return [model.model_name for model in cls]

ModelType = OpenAIModel | GeminiModel | str
