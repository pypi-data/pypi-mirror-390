import os

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from automation_lib.config_constants import ModuleConfigConstants

# Import the custom YAML settings source
from automation_lib.config_utils import YamlConfigSettingsSource


class BaseConfig(BaseSettings):
    """
    A generic base class for Pydantic configurations that handles loading
    from YAML files and environment variables in a prioritized order.
    """
    def __init__(self, env_file: str | None = None, **kwargs):
        # Pass env_file directly to the BaseSettings constructor
        super().__init__(_env_file=env_file, **kwargs)

    # Define model_config at the class level, it will be used by BaseSettings
    # The _env_file passed in __init__ will take precedence for that instance.
    model_config = SettingsConfigDict(
        env_prefix="", # Default empty prefix, can be overridden by subclasses
        env_file=ModuleConfigConstants.DEFAULT_ENV_FILES, # Use standard .env file order
        case_sensitive=False,
        use_enum_values=True, # Use string values for enums in config
        extra='ignore' # Ignore extra fields from environment variables or other sources
    )
    @classmethod
    def create_settings_class(cls, module_base_path: str, config_section_name: str) -> type[BaseSettings]:
        """
        Dynamically creates a Pydantic BaseSettings class with customized sources
        for a specific module.

        Args:
            module_base_path (str): The base path of the module (e.g., os.path.dirname(__file__)).
                                    This is used to locate the default_config.yaml.
            config_section_name (str): The name of the section in the default_config.yaml
                                       that corresponds to this module's configuration.

        Returns:
            Type[BaseSettings]: A Pydantic BaseSettings class configured for the module.
        """
        # Determine the path to the default_config.yaml relative to the module
        default_config_path = os.path.join(module_base_path, 'config', 'default_config.yaml')

        class DynamicSettings(cls):
            @classmethod
            def settings_customise_sources(
                cls,
                settings_cls: type[BaseSettings],
                init_settings: PydanticBaseSettingsSource,
                env_settings: PydanticBaseSettingsSource,
                dotenv_settings: PydanticBaseSettingsSource,
                file_secret_settings: PydanticBaseSettingsSource,
            ) -> tuple[PydanticBaseSettingsSource, ...]:
                """
                Customizes the order of settings sources for this dynamic class.
                Prioritizes init, then .env, then environment variables, then YAML defaults.
                """
                return (
                    init_settings, # Values passed directly to the constructor
                    dotenv_settings, # Load from .env file (including env_file parameter)
                    env_settings, # Load from environment variables
                    YamlConfigSettingsSource(settings_cls, default_config_path, config_section_name), # Load from YAML
                    file_secret_settings, # Load from secrets files (if any)
                )
        return DynamicSettings
