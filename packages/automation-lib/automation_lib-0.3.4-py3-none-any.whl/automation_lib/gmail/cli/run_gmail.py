"""
CLI-Einstiegspunkt für das Gmail-Modul.

Ermöglicht die Ausführung von Gmail-Operationen über die Kommandozeile.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[3]))

from automation_lib.gmail.config.gmail_config import GmailConfig
from automation_lib.gmail.gmail_runner import (
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
from automation_lib.gmail.schemas.gmail_schemas import EmailInput, MoveEmailInput, ReplyEmailInput

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="CLI for Gmail automation module.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a custom YAML configuration file."
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Check new emails command
    check_parser = subparsers.add_parser(
        "check-new", help="Check for new emails.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    check_parser.add_argument(
        "--query",
        type=str,
        default="is:unread",
        help="Gmail search query (e.g., 'is:unread', 'from:example@gmail.com')."
    )
    check_parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of emails to fetch."
    )
    check_parser.set_defaults(func=run_check_new_emails)

    # Create email command
    create_parser = subparsers.add_parser(
        "create-email", help="Create and send a new email.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    create_parser.add_argument(
        "--to",
        type=str,
        nargs="+",
        required=True,
        help="Recipient email addresses (space-separated)."
    )
    create_parser.add_argument(
        "--subject",
        type=str,
        required=True,
        help="Subject of the email."
    )
    create_parser.add_argument(
        "--body",
        type=str,
        required=True,
        help="Content of the email."
    )
    create_parser.add_argument(
        "--cc",
        type=str,
        nargs="*",
        default=[],
        help="CC recipient email addresses (space-separated)."
    )
    create_parser.add_argument(
        "--bcc",
        type=str,
        nargs="*",
        default=[],
        help="BCC recipient email addresses (space-separated)."
    )
    create_parser.add_argument(
        "--attachments",
        type=str,
        nargs="*",
        default=[],
        help="Paths to attachment files (space-separated)."
    )
    create_parser.set_defaults(func=run_create_email)

    # Reply to email command
    reply_parser = subparsers.add_parser(
        "reply-email", help="Reply to an existing email.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    reply_parser.add_argument(
        "--original-message-id",
        type=str,
        required=True,
        help="ID of the original email to reply to."
    )
    reply_parser.add_argument(
        "--reply-body",
        type=str,
        required=True,
        help="Content of the reply email."
    )
    reply_parser.add_argument(
        "--reply-all",
        action="store_true",
        help="Reply to all recipients of the original email."
    )
    reply_parser.add_argument(
        "--attachments",
        type=str,
        nargs="*",
        default=[],
        help="Paths to attachment files (space-separated)."
    )
    reply_parser.set_defaults(func=run_reply_to_email)

    # Delete email command
    delete_email_parser = subparsers.add_parser(
        "delete-email", help="Delete an email.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    delete_email_parser.add_argument(
        "--message-id",
        type=str,
        required=True,
        help="ID of the email to delete."
    )
    delete_email_parser.set_defaults(func=run_delete_email)

    # Move email command
    move_email_parser = subparsers.add_parser(
        "move-email", help="Move an email by adding/removing labels.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    move_email_parser.add_argument(
        "--message-id",
        type=str,
        required=True,
        help="ID of the email to move."
    )
    move_email_parser.add_argument(
        "--add-labels",
        type=str,
        nargs="*",
        default=[],
        help="Labels to add to the email (space-separated)."
    )
    move_email_parser.add_argument(
        "--remove-labels",
        type=str,
        nargs="*",
        default=[],
        help="Labels to remove from the email (space-separated)."
    )
    move_email_parser.set_defaults(func=run_move_email)

    # Create folder command (which is a label in Gmail)
    create_folder_parser = subparsers.add_parser(
        "create-folder", help="Create a new folder (Gmail label).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    create_folder_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the folder/label to create."
    )
    create_folder_parser.set_defaults(func=run_create_folder)

    # Delete folder command (which is a label in Gmail)
    delete_folder_parser = subparsers.add_parser(
        "delete-folder", help="Delete a folder (Gmail label).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    delete_folder_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the folder/label to delete."
    )
    delete_folder_parser.set_defaults(func=run_delete_folder)

    # Create label command
    create_label_parser = subparsers.add_parser(
        "create-label", help="Create a new Gmail label.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    create_label_parser.add_argument(
        "--name",
        type=str,
        required=True,
        help="Name of the label to create."
    )
    create_label_parser.set_defaults(func=run_create_label)

    # Add label to email command
    add_label_parser = subparsers.add_parser(
        "add-label-to-email", help="Add a label to an email.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    add_label_parser.add_argument(
        "--message-id",
        type=str,
        required=True,
        help="ID of the email."
    )
    add_label_parser.add_argument(
        "--label-name",
        type=str,
        required=True,
        help="Name of the label to add."
    )
    add_label_parser.set_defaults(func=run_add_label_to_email)

    args = parser.parse_args()

    # Load configuration
    config = None
    if args.config:
        config = GmailConfig.load_from_yaml(args.config)
    else:
        config = GmailConfig() # Load from .env and default_config.yaml

    if hasattr(args, "func"):
        args.func(args, config)
    else:
        parser.print_help()


def run_check_new_emails(args, config: GmailConfig):
    result = check_new_emails(query=args.query, max_results=args.max_results, config=config)
    if result.success:
        print(f"Found {result.count} emails matching query '{result.query}':")
        for email in result.emails:
            print(f"  ID: {email.id}, Subject: {email.subject}, From: {email.sender}, Read: {email.is_read}")
    else:
        print(f"Error checking new emails: {result.error_message}")


def run_create_email(args, config: GmailConfig):
    email_input = EmailInput(
        to=args.to,
        subject=args.subject,
        body=args.body,
        cc=args.cc,
        bcc=args.bcc,
        attachments=args.attachments
    )
    result = create_email(email_input=email_input, config=config)
    if result.success:
        print(f"Email created and sent successfully with Message ID: {result.message_id}")
    else:
        print(f"Error creating email: {result.error_message}")


def run_reply_to_email(args, config: GmailConfig):
    reply_input = ReplyEmailInput(
        original_message_id=args.original_message_id,
        reply_body=args.reply_body,
        reply_all=args.reply_all,
        attachments=args.attachments
    )
    result = reply_to_email(reply_input=reply_input, config=config)
    if result.success:
        print(f"Replied to email successfully with Message ID: {result.message_id}")
    else:
        print(f"Error replying to email: {result.error_message}")


def run_delete_email(args, config: GmailConfig):
    result = delete_email(message_id=args.message_id, config=config)
    if result.success:
        print(f"Email with ID '{result.message_id}' deleted successfully.")
    else:
        print(f"Error deleting email with ID '{args.message_id}': {result.error_message}")


def run_move_email(args, config: GmailConfig):
    move_input = MoveEmailInput(
        message_id=args.message_id,
        add_labels=args.add_labels,
        remove_labels=args.remove_labels
    )
    result = move_email(move_input=move_input, config=config)
    if result.success:
        print(f"Email with ID '{result.message_id}' moved/labels modified successfully.")
    else:
        print(f"Error moving email with ID '{args.message_id}': {result.error_message}")


def run_create_folder(args, config: GmailConfig):
    result = create_folder(folder_name=args.name, config=config)
    if result.success:
        print(f"Folder '{result.folder_name}' created successfully with Label ID: {result.label_id}")
    else:
        print(f"Error creating folder '{args.name}': {result.error_message}")


def run_delete_folder(args, config: GmailConfig):
    result = delete_folder(folder_name=args.name, config=config)
    if result.success:
        print(f"Folder '{result.folder_name}' deleted successfully.")
    else:
        print(f"Error deleting folder '{args.name}': {result.error_message}")


def run_create_label(args, config: GmailConfig):
    result = create_label(label_name=args.name, config=config)
    if result.success:
        print(f"Label '{result.label_name}' created successfully with Label ID: {result.label_id}")
    else:
        print(f"Error creating label '{args.name}': {result.error_message}")


def run_add_label_to_email(args, config: GmailConfig):
    result = add_label_to_email(message_id=args.message_id, label_name=args.label_name, config=config)
    if result.success:
        print(f"Label '{result.label_name}' added to email '{result.message_id}' successfully.")
    else:
        print(f"Error adding label '{args.label_name}' to email '{args.message_id}': {result.error_message}")


if __name__ == "__main__":
    main()
