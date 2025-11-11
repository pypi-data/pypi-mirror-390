"""
Gmail Runner - Zentrale Einstiegspunktfunktionen für Gmail-Operationen

Dieses Modul stellt die Hauptfunktionen für die Interaktion mit Gmail bereit.
"""

import logging

from .config.gmail_config import GmailConfig
from .gmail_helpers import GmailService
from .schemas.gmail_schemas import EmailInput, EmailOutput, EmailTriggerOutput, FolderOutput, LabelOutput, MoveEmailInput, ReplyEmailInput

logger = logging.getLogger(__name__)


def check_new_emails(
    query: str | None = None,
    max_results: int = 10,
    config: GmailConfig | None = None
) -> EmailTriggerOutput:
    """
    Prüft auf neue E-Mails basierend auf einer Suchanfrage.
    
    Args:
        query: Gmail-Suchanfrage (z.B. "is:unread", "from:example@gmail.com")
        max_results: Maximale Anzahl der zurückgegebenen E-Mails
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        EmailTriggerOutput: Ergebnis mit gefundenen E-Mails
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        
        # Standardabfrage für ungelesene E-Mails
        if query is None:
            query = "is:unread"
        
        emails = gmail_service.search_emails(query, max_results)
        
        return EmailTriggerOutput(
            success=True,
            emails=emails,
            count=len(emails),
            query=query,
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Prüfen neuer E-Mails: {e!s}")
        return EmailTriggerOutput(
            success=False,
            error_message=str(e),
            emails=[],
            count=0,
            query=query or ""
        )


def create_email(
    email_input: EmailInput,
    config: GmailConfig | None = None
) -> EmailOutput:
    """
    Erstellt und sendet eine neue E-Mail.
    
    Args:
        email_input: E-Mail-Daten (Empfänger, Betreff, Inhalt, etc.)
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        EmailOutput: Ergebnis der E-Mail-Erstellung
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        message_id = gmail_service.send_email(email_input)
        
        return EmailOutput(
            success=True,
            message_id=message_id,
            operation="create",
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der E-Mail: {e!s}")
        return EmailOutput(
            success=False,
            error_message=str(e),
            operation="create",
            message_id=None # Explicitly set to None on failure
        )


def reply_to_email(
    reply_input: ReplyEmailInput,
    config: GmailConfig | None = None
) -> EmailOutput:
    """
    Antwortet auf eine bestehende E-Mail.
    
    Args:
        reply_input: Antwort-Daten (ursprüngliche Message-ID, Antworttext, etc.)
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        EmailOutput: Ergebnis der E-Mail-Antwort
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        message_id = gmail_service.reply_to_email(reply_input)
        
        return EmailOutput(
            success=True,
            message_id=message_id,
            operation="reply",
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Antworten auf E-Mail: {e!s}")
        return EmailOutput(
            success=False,
            error_message=str(e),
            operation="reply",
            message_id=None # Explicitly set to None on failure
        )


def delete_email(
    message_id: str,
    config: GmailConfig | None = None
) -> EmailOutput:
    """
    Löscht eine E-Mail.
    
    Args:
        message_id: ID der zu löschenden E-Mail
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        EmailOutput: Ergebnis der E-Mail-Löschung
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        gmail_service.delete_email(message_id)
        
        return EmailOutput(
            success=True,
            message_id=message_id,
            operation="delete",
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Löschen der E-Mail: {e!s}")
        return EmailOutput(
            success=False,
            error_message=str(e),
            message_id=message_id,
            operation="delete"
        )


def move_email(
    move_input: MoveEmailInput,
    config: GmailConfig | None = None
) -> EmailOutput:
    """
    Verschiebt eine E-Mail zwischen Ordnern/Labels.
    
    Args:
        move_input: Verschiebungs-Daten (Message-ID, Ziel-Label, etc.)
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        EmailOutput: Ergebnis der E-Mail-Verschiebung
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        gmail_service.move_email(move_input)
        
        return EmailOutput(
            success=True,
            message_id=move_input.message_id,
            operation="move",
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Verschieben der E-Mail: {e!s}")
        return EmailOutput(
            success=False,
            error_message=str(e),
            message_id=move_input.message_id,
            operation="move"
        )


def create_folder(
    folder_name: str,
    config: GmailConfig | None = None
) -> FolderOutput:
    """
    Erstellt einen neuen Ordner (Label) in Gmail.
    
    Args:
        folder_name: Name des zu erstellenden Ordners
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        FolderOutput: Ergebnis der Ordner-Erstellung
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        label_id = gmail_service.create_label(folder_name)
        
        return FolderOutput(
            success=True,
            folder_name=folder_name,
            label_id=label_id,
            operation="create",
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Ordners: {e!s}")
        return FolderOutput(
            success=False,
            error_message=str(e),
            folder_name=folder_name,
            operation="create",
            label_id=None # Explicitly set to None on failure
        )


def delete_folder(
    folder_name: str,
    config: GmailConfig | None = None
) -> FolderOutput:
    """
    Löscht einen Ordner (Label) in Gmail.
    
    Args:
        folder_name: Name des zu löschenden Ordners
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        FolderOutput: Ergebnis der Ordner-Löschung
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        gmail_service.delete_label(folder_name)
        
        return FolderOutput(
            success=True,
            folder_name=folder_name,
            operation="delete",
            label_id="",
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Ordners: {e!s}")
        return FolderOutput(
            success=False,
            error_message=str(e),
            folder_name=folder_name,
            operation="delete",
            label_id=None # Explicitly set to None on failure
        )


def create_label(
    label_name: str,
    config: GmailConfig | None = None
) -> LabelOutput:
    """
    Erstellt ein neues Label in Gmail.
    
    Args:
        label_name: Name des zu erstellenden Labels
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        LabelOutput: Ergebnis der Label-Erstellung
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        label_id = gmail_service.create_label(label_name)
        
        return LabelOutput(
            success=True,
            label_name=label_name,
            label_id=label_id,
            operation="create",
            message_id="",
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Labels: {e!s}")
        return LabelOutput(
            success=False,
            error_message=str(e),
            label_name=label_name,
            operation="create",
            message_id="",
            label_id=None # Explicitly set to None on failure
        )


def add_label_to_email(
    message_id: str,
    label_name: str,
    config: GmailConfig | None = None
) -> LabelOutput:
    """
    Fügt ein Label zu einer E-Mail hinzu.
    
    Args:
        message_id: ID der E-Mail
        label_name: Name des Labels
        config: Gmail-Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        LabelOutput: Ergebnis der Label-Hinzufügung
    """
    try:
        if config is None:
            config = GmailConfig()
        
        gmail_service = GmailService(config)
        gmail_service.add_label_to_email(message_id, label_name)
        
        return LabelOutput(
            success=True,
            label_name=label_name,
            message_id=message_id,
            operation="add_to_email",
            label_id="",
            error_message=""
        )
    
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen des Labels zur E-Mail: {e!s}")
        return LabelOutput(
            success=False,
            error_message=str(e),
            label_name=label_name,
            message_id=None, # Explicitly set to None on failure
            operation="add_to_email",
            label_id=None # Explicitly set to None on failure
        )
