"""
Gmail Schemas - Pydantic-Modelle für Input/Output

Dieses Modul definiert die Datenstrukturen für Gmail-Operationen.
"""

from .gmail_schemas import (
    EmailData,
    EmailInput,
    EmailListOutput,
    EmailOutput,
    EmailTriggerOutput,
    FolderOutput,
    LabelOutput,
    MoveEmailInput,
    ReplyEmailInput,
)

__all__ = [
    "EmailData",
    "EmailInput",
    "EmailListOutput",
    "EmailOutput",
    "EmailTriggerOutput",
    "FolderOutput",
    "LabelOutput",
    "MoveEmailInput",
    "ReplyEmailInput"
]
