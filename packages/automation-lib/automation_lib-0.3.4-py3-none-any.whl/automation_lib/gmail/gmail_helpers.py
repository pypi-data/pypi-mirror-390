"""
Gmail Helpers - Hilfsfunktionen für Gmail-Operationen

Dieses Modul enthält Hilfsfunktionen und die GmailService-Klasse
für die Interaktion mit der Google Gmail API.
"""

import base64
import logging
import os
import re
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from googleapiclient.errors import HttpError

from .config.gmail_config import AuthMethod, GmailConfig
from .gmail_auth import GmailAuthenticator
from .schemas.gmail_schemas import EmailData, EmailInput, MoveEmailInput, ReplyEmailInput

logger = logging.getLogger(__name__)

class GmailService:
    """
    Klasse zur Interaktion mit der Google Gmail API.
    Nutzt den GmailAuthenticator für die Authentifizierung.
    """

    def __init__(self, config: GmailConfig):
        self.config = config
        authenticator = GmailAuthenticator(config)
        self.service = authenticator.authenticate()

    def _handle_precondition_error(self, error: HttpError):
        """Zentralisierte Fehlerbehandlung für 'Precondition check failed'-Fehler."""
        if "Precondition check failed" not in str(error):
            return

        if self.config.gmail_auth_method == AuthMethod.SERVICE_ACCOUNT:
            error_message = (
                "Gmail API 'Precondition check failed'. This usually means one of two things:\n"
                "1. The Gmail API is not enabled for your Google Cloud project. Please enable it here: "
                "https://console.cloud.google.com/apis/library/gmail.googleapis.com\n"
                "2. Domain-wide delegation is not configured correctly. Ensure the service account's "
                "Client ID has been granted the necessary scopes in your Google Workspace Admin console."
            )
        else: # AuthMethod.OAUTH
            error_message = (
                "Gmail API 'Precondition check failed'. This usually means the Gmail API is not enabled "
                "for your Google Cloud project. Please enable it here: "
                "https://console.cloud.google.com/apis/library/gmail.googleapis.com"
            )
        logger.error(error_message)

    def search_emails(self, query: str, max_results: int = 10) -> list[EmailData]:
        """Sucht E-Mails basierend auf einer Gmail-Suchanfrage."""
        try:
            results = self.service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
            messages = results.get("messages", [])
            
            emails_data = []
            for message in messages:
                msg = self.service.users().messages().get(userId="me", id=message["id"], format="full").execute()
                email_data = self._parse_email_message(msg)
                emails_data.append(email_data)
            return emails_data
        except HttpError as error:
            logger.error(f"Fehler beim Suchen von E-Mails: {error}")
            raise

    def _parse_email_message(self, msg: dict[str, Any]) -> EmailData:
        """Parst ein Gmail-Nachrichtenobjekt in das EmailData-Schema."""
        headers = msg["payload"]["headers"]
        
        def get_header(name):
            return next((h["value"] for h in headers if h["name"].lower() == name.lower()), None)

        def extract_email_address(header_value: str | None) -> str | None:
            if not header_value:
                return None
            # Regex to find email address within angle brackets or as a plain email
            match = re.search(r'<([^>]+)>', header_value)
            if match:
                return match.group(1)
            # If no angle brackets, assume the whole string is the email address
            return header_value.strip()

        sender = extract_email_address(get_header("From"))
        
        to_recipients_raw = get_header("To")
        cc_recipients_raw = get_header("Cc")
        bcc_recipients_raw = get_header("Bcc")
        subject = get_header("Subject")
        
        recipients = []
        if to_recipients_raw:
            recipients.extend([extract_email_address(r.strip()) for r in to_recipients_raw.split(',') if extract_email_address(r.strip())])
        if cc_recipients_raw:
            recipients.extend([extract_email_address(r.strip()) for r in cc_recipients_raw.split(',') if extract_email_address(r.strip())])
        if bcc_recipients_raw:
            recipients.extend([extract_email_address(r.strip()) for r in bcc_recipients_raw.split(',') if extract_email_address(r.strip())])
        
        # Filter out None values from recipients list
        recipients = [r for r in recipients if r is not None]

        # Extract body
        body = ""
        # Prioritize plain text over HTML if both are present
        plain_text_body = ""
        html_body = ""

        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part["mimeType"] == "text/plain" and "data" in part["body"]:
                    plain_text_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                elif part["mimeType"] == "text/html" and "data" in part["body"]:
                    html_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
        elif "body" in msg["payload"] and "data" in msg["payload"]["body"]:
            # Fallback for messages without 'parts' (e.g., simple text emails)
            plain_text_body = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode("utf-8")
        
        body = plain_text_body if plain_text_body else html_body


        # Get received_at from 'Date' header
        received_at_str = get_header("Date")
        received_at = None
        if received_at_str:
            try:
                # Example: 'Thu, 04 Jul 2025 10:00:00 +0200'
                # Need to parse this robustly. Using email.utils.parsedate_to_datetime
                from email.utils import parsedate_to_datetime
                received_at = parsedate_to_datetime(received_at_str)
            except Exception as e:
                logger.warning(f"Could not parse date '{received_at_str}': {e}")

        # Get labels
        labels = msg.get("labelIds", [])
        
        return EmailData(
            id=msg["id"],
            thread_id=msg.get("threadId"), # Use .get() to avoid KeyError if threadId is missing
            sender=sender,
            recipients=recipients,
            subject=subject,
            snippet=msg.get("snippet"),
            body=body,
            received_at=received_at,
            is_read="UNREAD" not in labels, # Assuming UNREAD label indicates unread status
            labels=labels
        )

    def send_email(self, email_input: EmailInput) -> str:
        """Sendet eine E-Mail."""
        try:
            message = MIMEMultipart()
            message["to"] = ", ".join(email_input.to)
            if email_input.cc:
                message["cc"] = ", ".join(email_input.cc)
            if email_input.bcc:
                message["bcc"] = ", ".join(email_input.bcc)
            message["subject"] = email_input.subject
            
            msg_body = MIMEText(email_input.body)
            message.attach(msg_body)

            if email_input.attachments:
                for attachment_path in email_input.attachments:
                    if not os.path.exists(attachment_path):
                        logger.warning(f"Anhang nicht gefunden: {attachment_path}")
                        continue
                    
                    part = MIMEBase("application", "octet-stream")
                    with open(attachment_path, "rb") as file:
                        part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(attachment_path)}",
                    )
                    message.attach(part)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            
            sent_message = self.service.users().messages().send(
                userId="me", body={"raw": raw_message}
            ).execute()
            return sent_message["id"]
        except HttpError as error:
            self._handle_precondition_error(error)
            logger.error(f"Fehler beim Senden der E-Mail: {error}")
            raise

    def reply_to_email(self, reply_input: ReplyEmailInput) -> str:
        """Antwortet auf eine bestehende E-Mail."""
        try:
            original_message = self.service.users().messages().get(
                userId="me", id=reply_input.original_message_id, format="full"
            ).execute()
            
            headers = original_message["payload"]["headers"]
            
            def get_header(name):
                return next((h["value"] for h in headers if h["name"].lower() == name.lower()), None)

            original_subject: str | None = get_header("Subject")
            original_from = get_header("From")
            original_to = get_header("To")
            original_cc = get_header("Cc")
            
            # Construct reply subject
            reply_subject = original_subject
            
            if reply_subject is None:
                reply_subject = "Re: No Subject"
            if original_subject and not original_subject.startswith("Re:"):
                reply_subject = f"Re: {original_subject}"

            # Determine recipients
            to_recipients = []
            if original_from:
                to_recipients.append(original_from)
            cc_recipients = []
            if reply_input.reply_all:
                if original_to:
                    to_recipients.extend([r.strip() for r in original_to.split(',') if r.strip() != self.config.gmail_default_sender_email])
                if original_cc:
                    cc_recipients.extend([r.strip() for r in original_cc.split(',') if r.strip() != self.config.gmail_default_sender_email])
            
            # Remove duplicates and own email from recipients, and filter out None
            to_recipients: list[str] = list(set(filter(None, to_recipients)))
            cc_recipients: list[str] = list(set(filter(None, cc_recipients)))

            # Create the reply message
            message = MIMEMultipart()
            message["to"] = ", ".join(to_recipients) if to_recipients else ""
            if cc_recipients:
                message["cc"] = ", ".join(cc_recipients)
            message["subject"] = reply_subject
            message["In-Reply-To"] = reply_input.original_message_id
            message["References"] = original_message["threadId"] # Use threadId for references
            
            msg_body = MIMEText(reply_input.reply_body)
            message.attach(msg_body)

            if reply_input.attachments:
                for attachment_path in reply_input.attachments:
                    if not os.path.exists(attachment_path):
                        logger.warning(f"Anhang nicht gefunden: {attachment_path}")
                        continue
                    
                    part = MIMEBase("application", "octet-stream")
                    with open(attachment_path, "rb") as file:
                        part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={os.path.basename(attachment_path)}",
                    )
                    message.attach(part)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            
            sent_message = self.service.users().messages().send(
                userId="me",
                body={"raw": raw_message},
                threadId=original_message["threadId"]
            ).execute()
            return sent_message["id"]
        except HttpError as error:
            logger.error(f"Fehler beim Antworten auf E-Mail: {error}")
            raise

    def delete_email(self, message_id: str):
        """Löscht eine E-Mail (verschiebt sie in den Papierkorb)."""
        try:
            self.service.users().messages().trash(userId="me", id=message_id).execute()
            logger.info(f"E-Mail mit ID '{message_id}' in den Papierkorb verschoben.")
        except HttpError as error:
            logger.error(f"Fehler beim Löschen der E-Mail '{message_id}': {error}")
            raise

    def move_email(self, move_input: MoveEmailInput):
        """Verschiebt eine E-Mail zwischen Ordnern/Labels."""
        try:
            # Ensure addLabelIds and removeLabelIds are always present, even if empty
            label_ids_to_add = [self._get_label_id(name) for name in move_input.add_labels] if move_input.add_labels else []
            label_ids_to_remove = [self._get_label_id(name) for name in move_input.remove_labels] if move_input.remove_labels else []

            body = {
                "addLabelIds": [lid for lid in label_ids_to_add if lid],
                "removeLabelIds": [lid for lid in label_ids_to_remove if lid]
            }

            # If both lists are empty, there's nothing to modify
            if not body["addLabelIds"] and not body["removeLabelIds"]:
                logger.warning(f"Keine Labels zum Hinzufügen oder Entfernen für E-Mail '{move_input.message_id}'.")
                return

            self.service.users().messages().modify(
                userId="me", id=move_input.message_id, body=body
            ).execute()
            logger.info(f"E-Mail '{move_input.message_id}' verschoben/Labels geändert.")
        except HttpError as error:
            logger.error(f"Fehler beim Verschieben der E-Mail '{move_input.message_id}': {error}")
            raise

    def create_label(self, label_name: str) -> str:
        """Erstellt ein neues Label in Gmail."""
        try:
            label_body = {
                "name": label_name,
                "labelListVisibility": "labelShow",  # Make label visible in label list
                "messageListVisibility": "show"      # Make label visible in message list
            }
            label = self.service.users().labels().create(userId="me", body=label_body).execute()
            logger.info(f"Label '{label_name}' erstellt mit ID: {label['id']}")
            return label["id"]
        except HttpError as error:
            if error.resp.status == 409: # Conflict, label already exists
                logger.warning(f"Label '{label_name}' existiert bereits.")
                existing_label = self._get_label_id(label_name)
                if existing_label:
                    return existing_label
            self._handle_precondition_error(error)
            logger.error(f"Fehler beim Erstellen des Labels '{label_name}': {error}")
            raise

    def delete_label(self, label_name: str):
        """Löscht ein Label in Gmail."""
        try:
            label_id = self._get_label_id(label_name)
            if not label_id:
                logger.warning(f"Label '{label_name}' nicht gefunden, kann nicht gelöscht werden.")
                return
            self.service.users().labels().delete(userId="me", id=label_id).execute()
            logger.info(f"Label '{label_name}' mit ID '{label_id}' gelöscht.")
        except HttpError as error:
            logger.error(f"Fehler beim Löschen des Labels '{label_name}': {error}")
            raise

    def add_label_to_email(self, message_id: str, label_name: str):
        """Fügt ein Label zu einer E-Mail hinzu."""
        try:
            label_id = self._get_label_id(label_name)
            if not label_id:
                logger.warning(f"Label '{label_name}' nicht gefunden, kann nicht zur E-Mail '{message_id}' hinzugefügt werden.")
                # Optionally create the label if it doesn't exist
                # label_id = self.create_label(label_name)
                # if not label_id:
                #     raise ValueError(f"Could not create or find label '{label_name}'")
                return

            body = {"addLabelIds": [label_id], "removeLabelIds": []} # Ensure removeLabelIds is always present
            self.service.users().messages().modify(
                userId="me", id=message_id, body=body
            ).execute()
            logger.info(f"Label '{label_name}' zu E-Mail '{message_id}' hinzugefügt.")
        except HttpError as error:
            logger.error(f"Fehler beim Hinzufügen des Labels '{label_name}' zu E-Mail '{message_id}': {error}")
            raise

    def _get_label_id(self, label_name: str) -> str | None:
        """Gibt die ID eines Labels anhand seines Namens zurück."""
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            for label in labels:
                if label["name"].lower() == label_name.lower():
                    return label["id"]
            return None
        except HttpError as error:
            self._handle_precondition_error(error)
            logger.error(f"Fehler beim Abrufen der Label-ID für '{label_name}': {error}")
            return None
