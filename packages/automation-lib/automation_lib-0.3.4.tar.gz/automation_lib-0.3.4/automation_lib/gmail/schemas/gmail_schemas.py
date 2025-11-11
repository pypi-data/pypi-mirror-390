"""
Gmail Schemas - Pydantic-Modelle für Input/Output

Dieses Modul definiert die Datenstrukturen für Gmail-Operationen.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class EmailData(BaseModel):
    """Represents a simplified structure for an email."""
    id: str = Field(..., description="Unique ID of the email message.")
    thread_id: str | None = Field(None, description="ID of the thread the email belongs to.") # Made optional
    sender: str | None = Field(None, description="Email address of the sender.")
    recipients: list[str] = Field([], description="List of recipient email addresses (To, Cc, Bcc).")
    subject: str | None = Field(None, description="Subject of the email.")
    snippet: str | None = Field(None, description="A short snippet of the message text.")
    body: str | None = Field(None, description="Full body of the email (plain text or HTML).")
    received_at: datetime | None = Field(None, description="Timestamp when the email was received.") # Made optional
    is_read: bool | None = Field(None, description="True if the email has been read, False otherwise.")
    labels: list[str] = Field([], description="List of labels applied to the email.")


class EmailInput(BaseModel):
    """Input schema for creating/sending an email."""
    to: list[EmailStr] = Field(..., description="List of recipient email addresses.")
    subject: str = Field(..., description="Subject of the email.")
    body: str = Field(..., description="Content of the email (plain text or HTML).")
    cc: list[EmailStr] = Field([], description="List of CC recipient email addresses.")
    bcc: list[EmailStr] = Field([], description="List of BCC recipient email addresses.")
    attachments: list[str] = Field([], description="List of file paths for attachments.")


class ReplyEmailInput(BaseModel):
    """Input schema for replying to an email."""
    original_message_id: str = Field(..., description="ID of the original email to reply to.")
    reply_body: str = Field(..., description="Content of the reply email.")
    reply_all: bool = Field(False, description="If true, reply to all recipients of the original email.")
    attachments: list[str] | None = Field(None, description="List of file paths for attachments.")


class MoveEmailInput(BaseModel):
    """Input schema for moving an email."""
    message_id: str = Field(..., description="ID of the email to move.")
    add_labels: list[str] | None = Field(None, description="List of labels to add to the email.")
    remove_labels: list[str] | None = Field(None, description="List of labels to remove from the email.")


class EmailOutput(BaseModel):
    """Output schema for email operations (create, reply, delete, move)."""
    success: bool = Field(..., description="True if the operation was successful, False otherwise.")
    message_id: str | None = Field(None, description="ID of the processed email message.")
    operation: str = Field(..., description="Type of operation performed (e.g., 'create', 'reply', 'delete', 'move').")
    error_message: str | None = Field(None, description="Error message if the operation failed.")


class EmailListOutput(BaseModel):
    """Output schema for listing emails."""
    success: bool = Field(..., description="True if the operation was successful, False otherwise.")
    emails: list[EmailData] = Field(..., description="List of email data.")
    count: int = Field(..., description="Number of emails found.")
    error_message: str | None = Field(None, description="Error message if the operation failed.")


class EmailTriggerOutput(EmailListOutput):
    """Output schema for email trigger (new emails check)."""
    query: str = Field(..., description="The query used to find new emails.")


class FolderOutput(BaseModel):
    """Output schema for folder (label) operations."""
    success: bool = Field(..., description="True if the operation was successful, False otherwise.")
    folder_name: str = Field(..., description="Name of the folder/label.")
    label_id: str | None = Field(None, description="ID of the created/deleted label.")
    operation: str = Field(..., description="Type of operation performed (e.g., 'create', 'delete').")
    error_message: str | None = Field(None, description="Error message if the operation failed.")


class LabelOutput(BaseModel):
    """Output schema for label operations."""
    success: bool = Field(..., description="True if the operation was successful, False otherwise.")
    label_name: str = Field(..., description="Name of the label.")
    label_id: str | None = Field(None, description="ID of the created label.")
    message_id: str | None = Field(None, description="ID of the email to which the label was added/removed.")
    operation: str = Field(..., description="Type of operation performed (e.g., 'create', 'add_to_email').")
    error_message: str | None = Field(None, description="Error message if the operation failed.")
