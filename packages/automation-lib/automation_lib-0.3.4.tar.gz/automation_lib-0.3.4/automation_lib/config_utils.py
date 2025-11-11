import os
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

# Load environment variables from .env file
load_dotenv()

# Custom Pydantic settings source for YAML files
class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    """
    A custom settings source for Pydantic that loads configuration from a YAML file.
    """
    def __init__(self, settings_cls: type[BaseSettings], yaml_file_path: str, config_section: str):
        super().__init__(settings_cls)
        self.yaml_file_path = yaml_file_path
        self.config_section = config_section
        self._data = self._read_yaml_file()

    def _read_yaml_file(self) -> dict[str, Any]:
        if os.path.exists(self.yaml_file_path):
            with open(self.yaml_file_path) as f:
                full_config = yaml.safe_load(f)
                if full_config and self.config_section in full_config:
                    return full_config[self.config_section]
        return {}

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        field_value = self._data.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(self, field_name: str, field: Any, value: Any, value_is_complex: bool) -> Any:
        return value

    def __call__(self) -> dict[str, Any]:
        return self._data
