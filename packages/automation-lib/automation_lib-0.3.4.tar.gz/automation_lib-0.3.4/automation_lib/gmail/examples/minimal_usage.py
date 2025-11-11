"""
Minimales Anwendungsbeispiel für das Gmail-Modul.

Dieses Skript demonstriert die grundlegende Nutzung der Gmail-Modul-Funktionen.
Stellen Sie sicher, dass Ihre .env-Datei korrekt konfiguriert ist
(siehe automation_lib/gmail/config/.env.example).
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[3]))

from automation_lib.gmail.gmail_runner import (
    add_label_to_email,
    check_new_emails,
    create_email,
    create_folder,
    delete_folder,
    move_email,
    reply_to_email,
)
from automation_lib.gmail.schemas.gmail_schemas import EmailInput, MoveEmailInput, ReplyEmailInput

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_example():
    logger.info("Starte minimales Gmail-Modul-Beispiel...")

    # --- Konfiguration laden ---
    # Die Konfiguration wird automatisch geladen, wenn 'config' nicht übergeben wird.
    # Sie können auch eine benutzerdefinierte Konfiguration übergeben:
    #
    # Beispiel für OAuth 2.0 Authentifizierung:
    # oauth_config = GmailConfig(
    #     gmail_auth_method=AuthMethod.OAUTH,
    #     gmail_api_client_id=os.getenv("GMAIL_API_CLIENT_ID"),
    #     gmail_api_client_secret=os.getenv("GMAIL_API_CLIENT_SECRET"),
    #     gmail_api_refresh_token=os.getenv("GMAIL_API_REFRESH_TOKEN"),
    #     gmail_default_sender_email="your_oauth_email@example.com"
    # )
    #
    # Beispiel für Service Account Authentifizierung (via JSON-Datei):
    # service_account_file_config = GmailConfig(
    #     gmail_auth_method=AuthMethod.SERVICE_ACCOUNT,
    #     gmail_service_account_file="/path/to/your-service-account-key.json", # Pfad zur JSON-Datei
    #     gmail_impersonate_user="user_to_impersonate@your-domain.com", # Optional: Für Domain-weite Delegation
    #     gmail_default_sender_email="your_service_account_email@example.com"
    # )
    #
    # Beispiel für Service Account Authentifizierung (via Umgebungsvariablen):
    # service_account_env_config = GmailConfig(
    #     gmail_auth_method=AuthMethod.SERVICE_ACCOUNT,
    #     gmail_service_account_email=os.getenv("GMAIL_SERVICE_ACCOUNT_EMAIL"),
    #     gmail_service_account_private_key_id=os.getenv("GMAIL_SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
    #     gmail_service_account_private_key=os.getenv("GMAIL_SERVICE_ACCOUNT_PRIVATE_KEY"),
    #     gmail_impersonate_user="user_to_impersonate@your-domain.com", # Optional
    #     gmail_default_sender_email="your_service_account_email@example.com"
    # )
    #
    # Wählen Sie die gewünschte Konfiguration:
    # current_config = oauth_config
    # current_config = service_account_file_config
    # current_config = service_account_env_config
    #
    # Wenn keine 'config' übergeben wird, lädt das Modul die Konfiguration automatisch
    # basierend auf Umgebungsvariablen und default_config.yaml.

    # --- 1. Neue E-Mails prüfen (ungelesen) ---
    logger.info("\n--- Beispiel: Ungelesene E-Mails abrufen ---")
    new_emails_result = check_new_emails(query="is:unread", max_results=5) # , config=current_config)
    if new_emails_result.success:
        logger.info(f"Gefundene ungelesene E-Mails ({new_emails_result.count}):")
        for email in new_emails_result.emails:
            logger.info(f"  ID: {email.id}, Betreff: {email.subject}, Von: {email.sender}, Snippet: {email.snippet}")
    else:
        logger.error(f"Fehler beim Abrufen ungelesener E-Mails: {new_emails_result.error_message}")

    # Beispiel: Eine neue E-Mail senden
    logger.info("\n--- Beispiel: Neue E-Mail senden ---")
    test_recipient = os.getenv("GMAIL_TEST_RECIPIENT_EMAIL", "your_test_email@example.com")
    if test_recipient == "your_test_email@example.com":
        logger.warning("Bitte GMAIL_TEST_RECIPIENT_EMAIL in .env.example anpassen, um E-Mails zu senden.")
    else:
        email_input = EmailInput(
            to=[test_recipient],
            subject="Test-E-Mail von automation_lib Gmail-Modul",
            body="Dies ist eine Testnachricht, gesendet vom Gmail-Modul der automation_lib.",
            cc=[], # Explicitly provide empty list for optional fields
            bcc=[],
            attachments=[]
        )
        send_email_result = create_email(email_input=email_input) # , config=current_config)
        if send_email_result.success:
            logger.info(f"E-Mail erfolgreich gesendet. Message ID: {send_email_result.message_id}")
            # Speichern der Message ID für weitere Beispiele
            sent_message_id = send_email_result.message_id
        else:
            logger.error(f"Fehler beim Senden der E-Mail: {send_email_result.error_message}")
            sent_message_id = None # Ensure it's None if sending failed

    # Beispiel: Auf eine E-Mail antworten (benötigt eine existierende Message ID)
    # Ersetzen Sie 'YOUR_MESSAGE_ID_TO_REPLY_TO' durch eine tatsächliche E-Mail-ID
    logger.info("\n--- Beispiel: Auf E-Mail antworten ---")
    message_id_to_reply = "YOUR_MESSAGE_ID_TO_REPLY_TO"
    if sent_message_id: # Use the ID of the email we just sent
        message_id_to_reply = sent_message_id

    if message_id_to_reply != "YOUR_MESSAGE_ID_TO_REPLY_TO":
        reply_input = ReplyEmailInput(
            original_message_id=message_id_to_reply,
            reply_body="Dies ist eine automatische Antwort auf Ihre E-Mail.",
            reply_all=False,
            attachments=[] # Explicitly provide empty list for optional fields
        )
        reply_email_result = reply_to_email(reply_input=reply_input) # , config=current_config)
        if reply_email_result.success:
            logger.info(f"Erfolgreich auf E-Mail geantwortet. Neue Message ID: {reply_email_result.message_id}")
        else:
            logger.error(f"Fehler beim Antworten auf E-Mail: {reply_email_result.error_message}")
    else:
        logger.info("Überspringe Beispiel 'Auf E-Mail antworten': Keine Message ID zum Antworten verfügbar.")

    # Beispiel: Ordner (Label) erstellen
    logger.info("\n--- Beispiel: Ordner (Label) erstellen ---")
    test_folder_name = "AutomationTestFolder"
    create_folder_result = create_folder(folder_name=test_folder_name) # , config=current_config)
    if create_folder_result.success:
        logger.info(f"Ordner '{create_folder_result.folder_name}' erfolgreich erstellt. Label ID: {create_folder_result.label_id}")
    else:
        logger.error(f"Fehler beim Erstellen des Ordners '{test_folder_name}': {create_folder_result.error_message}")

    # Beispiel: Label zu einer E-Mail hinzufügen (benötigt eine existierende Message ID)
    logger.info("\n--- Beispiel: Label zu E-Mail hinzufügen ---")
    email_to_label_id = None
    if new_emails_result.success and new_emails_result.emails:
        email_to_label_id = new_emails_result.emails[0].id
    elif sent_message_id:
        email_to_label_id = sent_message_id

    if email_to_label_id and create_folder_result.success:
        add_label_result = add_label_to_email(
            message_id=email_to_label_id,
            label_name=test_folder_name
        ) # , config=current_config)
        if add_label_result.success:
            logger.info(f"Label '{add_label_result.label_name}' erfolgreich zu E-Mail '{add_label_result.message_id}' hinzugefügt.")
        else:
            logger.error(f"Fehler beim Hinzufügen des Labels zu E-Mail: {add_label_result.error_message}")
    else:
        logger.info("Überspringe Beispiel 'Label zu E-Mail hinzufügen': Keine E-Mail-ID oder Ordner nicht erstellt.")

    # Beispiel: E-Mail verschieben (Beispiel: von INBOX nach TRASH)
    logger.info("\n--- Beispiel: E-Mail verschieben ---")
    if sent_message_id:
        move_input = MoveEmailInput(
            message_id=sent_message_id,
            add_labels=["TRASH"], # Gmail's Papierkorb ist ein Label
            remove_labels=["INBOX"]
        )
        move_email_result = move_email(move_input=move_input) # , config=current_config)

        if move_email_result.success:
            logger.info(f"E-Mail mit ID {move_input.message_id} erfolgreich in den Papierkorb verschoben.")
        else:
            logger.error(f"Fehler beim Verschieben der E-Mail: {move_email_result.error_message}")
    else:
        logger.info("Überspringe Beispiel 'E-Mail verschieben': Keine gesendete E-Mail-ID verfügbar.")

    # Beispiel: Ordner (Label) löschen
    logger.info("\n--- Beispiel: Ordner (Label) löschen ---")
    if create_folder_result.success: # Nur löschen, wenn zuvor erfolgreich erstellt
        delete_folder_result = delete_folder(folder_name=test_folder_name) # , config=current_config)
        if delete_folder_result.success:
            logger.info(f"Ordner '{delete_folder_result.folder_name}' erfolgreich gelöscht.")
        else:
            logger.error(f"Fehler beim Löschen des Ordners: {delete_folder_result.error_message}")
    else:
        logger.info("Überspringe Beispiel 'Ordner löschen': Ordner wurde zuvor nicht erfolgreich erstellt.")

    logger.info("\nAlle Gmail-Modul-Beispiele abgeschlossen.")


if __name__ == "__main__":
    run_example()
