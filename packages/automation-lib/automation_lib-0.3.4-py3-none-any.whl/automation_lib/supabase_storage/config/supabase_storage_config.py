# automation_lib/supabase_storage/config/supabase_storage_config.py

import os

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from automation_lib.config_base import BaseConfig
from automation_lib.config_constants import ModuleConfigConstants

# Dynamically create the BaseSettings class for SupabaseStorageConfig
# This ensures the settings sources are correctly configured for this module
_SupabaseStorageBaseSettings = BaseConfig.create_settings_class(
    module_base_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
    config_section_name='supabase_storage'
)

# Pydantic model for Supabase Storage Configuration
class SupabaseStorageConfig(_SupabaseStorageBaseSettings):
    def __init__(self, env_file: str | None = None, **kwargs):
        """
        Initializes the configuration instance.

        Args:
            env_file (Optional[str]): Path to a specific .env file to load.
                                      This overrides any default .env file paths.
            **kwargs: Additional keyword arguments passed to the Pydantic model.
        """
        super().__init__(env_file=env_file, **kwargs)
        
    # Connection Settings
    supabase_url: str | None = Field(None, description="Supabase Projekt URL", alias="SUPABASE_URL")
    supabase_key: str | None = Field(None, description="Supabase Service Role Key", alias="SUPABASE_KEY")
    
    # Default Bucket Settings
    default_bucket_name: str = Field("files", description="Standard Bucket Name")
    
    # Operation Settings
    download_timeout_seconds: int = Field(300, description="Timeout für Downloads in Sekunden")
    max_file_size_mb: int = Field(100, description="Maximale Dateigröße für Downloads in MB")
    
    # Batch Operation Settings
    max_batch_delete_size: int = Field(100, description="Maximale Anzahl Dateien für Batch-Löschung")
    
    # List Operation Settings
    default_list_limit: int = Field(1000, description="Standard-Limit für Dateilisten-Operationen")

    model_config = SettingsConfigDict(
        env_prefix="SUPABASE_STORAGE_",  # Prefix for environment variables
        env_file=ModuleConfigConstants.DEFAULT_ENV_FILES,  # Use standard .env file order
        extra='ignore'  # Ignore extra fields not defined in the model
    )
