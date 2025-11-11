"""
Gmail Automation Module

Dieses Modul stellt eine einfache und sichere Schnittstelle für die Interaktion
mit Gmail über die Google API bereit. Es ermöglicht E-Mail-Trigger, E-Mail-Verwaltung,
Ordnerverwaltung und Label-Verwaltung.
"""

from .gmail_runner import (
    add_label_to_email,
    check_new_emails,
    create_email,
    create_folder,
    create_label,
    delete_email,
    delete_folder,
    move_email,
    reply_to_email,
)

__version__ = "0.1.0"
__all__ = [
    "add_label_to_email",
    "check_new_emails",
    "create_email",
    "create_folder",
    "create_label",
    "delete_email",
    "delete_folder",
    "move_email",
    "reply_to_email"
]
