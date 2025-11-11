"""
Model Resolver

Resolves model input (Enum or string) to a model name and its fallback models.
"""
from automation_lib.llm_prompt.models import GeminiModel, ModelType, OpenAIModel


class ModelResolver:
    """
    Resolves model input (Enum or string) to a model name and its fallback models.
    """
    
    @staticmethod
    def resolve_model(model: ModelType) -> tuple[str, list[str]]:
        """
        Resolves model input and returns (model_name, fallback_models).
        
        Args:
            model: Enum value or string.
            
        Returns:
            tuple: (model_name, fallback_models_list).
            
        Raises:
            ValueError: If the model type is invalid.
        """
        if isinstance(model, (OpenAIModel | GeminiModel)):
            return model.model_name, model.fallback_models
        elif isinstance(model, str):
            # Try to match string to an Enum
            enum_model = ModelResolver.find_enum_by_name(model)
            if enum_model:
                return enum_model.model_name, enum_model.fallback_models
            else:
                # Fallback: Use string as model name, no fallbacks by default
                return model, []
        else:
            raise ValueError(f"Invalid model type: {type(model)}")
    
    @staticmethod
    def find_enum_by_name(model_name: str) -> OpenAIModel | GeminiModel | None:
        """
        Finds an Enum member based on its model_name string across all defined model enums.
        """
        # Search all OpenAI Models
        openai_enum = OpenAIModel.from_string(model_name)
        if openai_enum:
            return openai_enum
        
        # Search all Gemini Models
        gemini_enum = GeminiModel.from_string(model_name)
        if gemini_enum:
            return gemini_enum
        
        return None

    @staticmethod
    def get_smart_fallbacks(model_name: str) -> list[str]:
        """
        Generates intelligent fallbacks for unknown models based on common patterns.
        """
        if model_name.startswith("gpt-4"):
            return ["gpt-4o-mini", "gpt-3.5-turbo"]
        elif model_name.startswith("gpt-3"):
            return ["gpt-4o-mini"]
        elif model_name.startswith("gemini"):
            return ["gemini-1.5-flash", "gemini-1.0-pro"]
        else:
            return []  # No fallbacks for truly unknown models
