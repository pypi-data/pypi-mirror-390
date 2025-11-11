"""
Gmail Config - Konfiguration und Parameter

Dieses Modul definiert die Konfigurationsstrukturen für das Gmail-Modul.
"""

import os
from enum import Enum
from typing import Any

from pydantic import Field, ValidationError
from pydantic_settings import SettingsConfigDict

from automation_lib.config_base import BaseConfig
from automation_lib.config_constants import ModuleConfigConstants

# Dynamically create the BaseSettings class for GmailConfig
# This ensures the settings sources are correctly configured for this module
_GmailBaseSettings = BaseConfig.create_settings_class(
    module_base_path=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
    config_section_name='gmail'
)

class AuthMethod(str, Enum):
    """Definiert die unterstützten Authentifizierungsmethoden."""
    OAUTH = "oauth"
    SERVICE_ACCOUNT = "service_account"

class GmailConfig(_GmailBaseSettings):
    """
    Konfigurationsklasse für das Gmail-Modul.
    Lädt Einstellungen aus Umgebungsvariablen, .env-Dateien und YAML-Dateien.
    """
    def __init__(self, env_file: str | None = None, **kwargs):
        """
        Initializes the configuration instance.

        Args:
            env_file (Optional[str]): Path to a specific .env file to load.
                                      This overrides any default .env file paths.
            **kwargs: Additional keyword arguments passed to the Pydantic model.
        """
        super().__init__(env_file=env_file, **kwargs)
    
    # Authentifizierungsmethode
    gmail_auth_method: AuthMethod | None = Field(
        default=None, description="Authentifizierungsmethode: 'oauth' oder 'service_account'. Standard ist None."
    )

    # OAuth 2.0 Credentials
    gmail_api_client_id: str | None = Field(default=None, description="Google API Client ID for Gmail (OAuth).")
    gmail_api_client_secret: str | None = Field(default=None, description="Google API Client Secret for Gmail (OAuth).")
    gmail_api_refresh_token: str | None = Field(default=None, description="Google API Refresh Token for Gmail (OAuth).")
    
    # Service Account Credentials
    gmail_service_account_file: str | None = Field(
        default=None, description="Pfad zur Service Account JSON-Schlüsseldatei."
    )
    gmail_service_account_email: str | None = Field(
        default=None, description="E-Mail-Adresse des Service Accounts (für Umgebungsvariablen-Auth)."
    )
    gmail_service_account_private_key_id: str | None = Field(
        default=None, description="Private Key ID des Service Accounts (für Umgebungsvariablen-Auth)."
    )
    gmail_service_account_private_key: str | None = Field(
        default=None, description="Privater Schlüssel des Service Accounts (für Umgebungsvariablen-Auth)."
    )
    gmail_impersonate_user: str | None = Field(
        default=None, description="E-Mail-Adresse des Benutzers für Domain-weite Delegation (Service Account)."
    )

    # Optional: Default settings for Gmail operations
    gmail_default_sender_email: str = Field(
        default="me", description="Default sender email address (e.g., 'me' or an email address)."
    )
    gmail_check_interval_seconds: int = Field(
        default=300, description="Interval in seconds for checking new emails."
    )
    gmail_max_email_fetch_results: int = Field(
        default=10, description="Maximum number of emails to fetch per request."
    )
    
    model_config = SettingsConfigDict(
        env_prefix="GMAIL_",
        case_sensitive=False,
        use_enum_values=True, # Use string values for enums in config
        env_file=ModuleConfigConstants.DEFAULT_ENV_FILES,  # Use standard .env file order
        extra='ignore'  # Ignore extra fields not defined in the model
    )

    def model_post_init(self, __context: Any) -> None:
        """Validiert die Konfiguration nach der Initialisierung."""
        if self.gmail_auth_method is None:
            # If no auth method is specified, assume no authentication is needed or it's handled externally.
            # No specific credentials are required in this case.
            pass
        elif self.gmail_auth_method == AuthMethod.OAUTH:
            # For OAuth, we only strictly need the client_id and client_secret.
            # The refresh token can be in token.json or provided via env var.
            # The helper will handle the logic of finding the token.
            if not (self.gmail_api_client_id and self.gmail_api_client_secret):
                raise ValidationError(
                    [{"loc": ("gmail_api_client_id",), "msg": "Für die OAuth-Authentifizierung müssen 'gmail_api_client_id' und 'gmail_api_client_secret' konfiguriert sein."}]
                )
        elif self.gmail_auth_method == AuthMethod.SERVICE_ACCOUNT:
            if not self.gmail_service_account_file:
                # If file is not provided, check for environment variables
                if not (self.gmail_service_account_email and
                        self.gmail_service_account_private_key_id and
                        self.gmail_service_account_private_key):
                    raise ValidationError(
                        [{"loc": ("gmail_service_account_file",), "msg": "Für die Service Account-Authentifizierung muss entweder 'gmail_service_account_file' oder alle 'gmail_service_account_email', 'gmail_service_account_private_key_id' und 'gmail_service_account_private_key' konfiguriert sein."}]
                    )
            elif not os.path.exists(self.gmail_service_account_file):
                raise ValidationError(
                    [{"loc": ("gmail_service_account_file",), "msg": f"Service Account JSON-Datei nicht gefunden: {self.gmail_service_account_file}"}]
                )
