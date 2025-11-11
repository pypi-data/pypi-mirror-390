"""
Gmail Authenticator - Verwaltet die Authentifizierung für die Gmail API.
"""

import logging
import os
from typing import Any

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .config.gmail_config import AuthMethod, GmailConfig

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://www.googleapis.com/auth/admin.directory.user.readonly"
]

class GmailAuthenticator:
    """Verwaltet die Authentifizierung für die Gmail API."""

    def __init__(self, config: GmailConfig):
        self.config = config

    def authenticate(self) -> Any:
        """
        Authentifiziert sich bei der Gmail API basierend auf der konfigurierten Methode
        und gibt das Service-Objekt zurück.
        """
        if self.config.gmail_auth_method == AuthMethod.SERVICE_ACCOUNT:
            creds = self._authenticate_service_account()
        elif self.config.gmail_auth_method == AuthMethod.OAUTH:
            creds = self._authenticate_oauth()
        else:
            raise ValueError(
                "Authentifizierungsmethode nicht angegeben. Bitte wählen Sie 'oauth' oder 'service_account'."
            )
        
        try:
            service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail API Service erfolgreich erstellt.")
            return service
        except HttpError as e:
            self._handle_precondition_error(e)
            raise

    def _authenticate_oauth(self) -> Credentials:
        """
        Führt die OAuth 2.0 Authentifizierung durch.
        Priorisiert Refresh-Token aus der Konfiguration, dann aus 'token.json'.
        """
        creds = None
        token_path = "token.json"

        if self.config.gmail_api_refresh_token:
            logger.info("Versuche Authentifizierung mit Refresh-Token aus der Konfiguration.")
            creds = Credentials(
                None,
                refresh_token=self.config.gmail_api_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.config.gmail_api_client_id,
                client_secret=self.config.gmail_api_client_secret,
                scopes=SCOPES
            )
        elif os.path.exists(token_path):
            logger.info(f"Versuche Authentifizierung mit '{token_path}'.")
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                logger.warning(f"Fehler beim Laden von '{token_path}': {e}. Token ist möglicherweise korrupt.")
                creds = None

        if creds and creds.expired and creds.refresh_token:
            logger.info("Access Token ist abgelaufen. Versuche, es zu erneuern...")
            try:
                creds.refresh(Request())
                with open(token_path, "w") as token:
                    token.write(creds.to_json())
                logger.info("Access Token erfolgreich erneuert.")
            except RefreshError as e:
                logger.error(f"Fehler beim Erneuern des Tokens: {e}")
                if os.path.exists(token_path):
                    os.remove(token_path)
                raise ValueError(
                    f"Das Refresh-Token ist ungültig oder abgelaufen. '{token_path}' wurde gelöscht. "
                    "Bitte generieren Sie ein neues Token, indem Sie das Skript "
                    "'automation_lib.gmail.cli.generate_token' ausführen."
                ) from None

        if not creds or not creds.valid:
            raise ValueError(
                "Keine gültigen OAuth 2.0-Anmeldeinformationen gefunden. "
                "Bitte stellen Sie sicher, dass entweder 'GMAIL_API_REFRESH_TOKEN' in Ihrer "
                "Konfiguration gesetzt ist oder führen Sie das Skript "
                "'automation_lib.gmail.cli.generate_token' aus, um 'token.json' zu erstellen."
            )
        
        return creds

    def _authenticate_service_account(self):
        """Authentifiziert sich über einen Google Service Account."""
        info = None
        if self.config.gmail_service_account_file:
            # Lade die Informationen aus der Datei
            import json
            try:
                with open(self.config.gmail_service_account_file) as f:
                    info = json.load(f)
                logger.info(f"Service Account-Informationen aus Datei geladen: {self.config.gmail_service_account_file}")
            except Exception as e:
                logger.error(f"Fehler beim Laden der Service Account-Datei '{self.config.gmail_service_account_file}': {e}")
                raise
        elif self.config.gmail_service_account_email and \
             self.config.gmail_service_account_private_key_id and \
             self.config.gmail_service_account_private_key:
            # Erstelle die Informationen aus Umgebungsvariablen
            info = self._get_service_account_info_from_env()
            logger.info("Service Account-Informationen aus Umgebungsvariablen erstellt.")
        else:
            raise ValueError("Service Account-Konfiguration unvollständig. Entweder Datei oder Umgebungsvariablen angeben.")

        # Erstelle die Credentials aus den Informationen
        creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

        # Wende die Identitätsübernahme (Impersonation) an, falls konfiguriert
        if self.config.gmail_impersonate_user:
            creds = creds.with_subject(self.config.gmail_impersonate_user)
            logger.info(f"Service Account authentifiziert mit Domain-weiter Delegation für: {self.config.gmail_impersonate_user}")
        else:
            logger.info("Service Account authentifiziert ohne Domain-weite Delegation.")
        
        return creds

    def _get_service_account_info_from_env(self) -> dict:
        """Erstellt das Service Account Info-Dictionary aus Umgebungsvariablen."""
        if not self.config.gmail_service_account_private_key:
            raise ValueError("GMAIL_SERVICE_ACCOUNT_PRIVATE_KEY ist nicht gesetzt.")
            
        return {
            "type": "service_account",
            "project_id": "not-needed-for-auth-but-common",
            "private_key_id": self.config.gmail_service_account_private_key_id,
            "private_key": self.config.gmail_service_account_private_key.replace('\\n', '\n'),
            "client_email": self.config.gmail_service_account_email,
            "client_id": self.config.gmail_api_client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{self.config.gmail_service_account_email}"
        }

    def _handle_precondition_error(self, error: HttpError):
        """Zentralisierte Fehlerbehandlung für 'Precondition check failed'-Fehler."""
        if "Precondition check failed" not in str(error):
            return

        if self.config.gmail_auth_method == AuthMethod.SERVICE_ACCOUNT:
            error_message = (
                "Gmail API 'Precondition check failed'. This usually means one of two things:\n"
                "1. The Gmail API is not enabled for your Google Cloud project.\n"
                "2. Domain-wide delegation is not configured correctly."
            )
        else:
            error_message = (
                "Gmail API 'Precondition check failed'. This usually means the Gmail API is not enabled "
                "for your Google Cloud project."
            )
        logger.error(error_message)
