"""
Unit-Tests für das Gmail-Schemas-Modul.

Testet die Pydantic-Schemas für das Gmail-Modul.
"""

import unittest
from datetime import datetime

from pydantic import ValidationError

from automation_lib.gmail.schemas.gmail_schemas import (
    EmailData,
    EmailInput,
    EmailOutput,
    EmailTriggerOutput,
    FolderOutput,
    LabelOutput,
    MoveEmailInput,
    ReplyEmailInput,
)


class TestGmailSchemas(unittest.TestCase):

    def test_email_input_valid(self):
        data = {
            "to": ["test@example.com"],
            "subject": "Test Subject",
            "body": "Test Body",
            "cc": ["cc@example.com"],
            "bcc": ["bcc@example.com"],
            "attachments": ["/path/to/file.txt"]
        }
        email_input = EmailInput(**data)
        self.assertEqual(str(email_input.to[0]), "test@example.com")
        self.assertEqual(email_input.subject, "Test Subject")
        self.assertEqual(email_input.body, "Test Body")
        self.assertEqual(str(email_input.cc[0]) if email_input.cc else None, "cc@example.com")
        self.assertEqual(str(email_input.bcc[0]) if email_input.bcc else None, "bcc@example.com")
        self.assertEqual(email_input.attachments, ["/path/to/file.txt"])

    def test_email_input_minimal_valid(self):
        data = {
            "to": ["test@example.com"],
            "subject": "Test Subject",
            "body": "Test Body"
        }
        email_input = EmailInput(**data)
        self.assertEqual(str(email_input.to[0]), "test@example.com")
        self.assertEqual(email_input.subject, "Test Subject")
        self.assertEqual(email_input.body, "Test Body")
        self.assertEqual(email_input.cc, [])
        self.assertEqual(email_input.bcc, [])
        self.assertEqual(email_input.attachments, [])

    def test_email_input_invalid_email(self):
        data = {
            "to": ["invalid-email"],
            "subject": "Test Subject",
            "body": "Test Body"
        }
        with self.assertRaises(ValidationError):
            EmailInput(**data)

    def test_email_data_valid(self):
        now = datetime.now()
        data = {
            "id": "123",
            "thread_id": "t1",
            "sender": "sender@example.com",
            "recipients": ["rec1@example.com", "rec2@example.com"],
            "subject": "Data Subject",
            "snippet": "Data Snippet",
            "body": "Data Body",
            "received_at": now, # Pass datetime object directly
            "is_read": True,
            "labels": ["INBOX", "IMPORTANT"]
        }
        email_data = EmailData(**data)
        self.assertEqual(email_data.id, "123")
        self.assertEqual(email_data.thread_id, "t1")
        self.assertEqual(str(email_data.sender), "sender@example.com")
        self.assertEqual([str(r) for r in email_data.recipients], ["rec1@example.com", "rec2@example.com"])
        self.assertEqual(email_data.subject, "Data Subject")
        self.assertEqual(email_data.snippet, "Data Snippet")
        self.assertEqual(email_data.body, "Data Body")
        self.assertIsNotNone(email_data.received_at) # Ensure it's not None
        self.assertEqual(email_data.received_at.isoformat(timespec='seconds'), now.isoformat(timespec='seconds'))
        self.assertTrue(email_data.is_read)
        self.assertEqual(email_data.labels, ["INBOX", "IMPORTANT"])

    def test_email_data_minimal_valid(self):
        now = datetime.now()
        data = {
            "id": "123",
            "thread_id": "t1",
            "sender": "sender@example.com",
            "recipients": [],
            "subject": "Data Subject",
            "snippet": "Data Snippet",
            "body": "Data Body",
            "received_at": now, # Pass datetime object directly
            "is_read": False,
            "labels": []
        }
        email_data = EmailData(**data)
        self.assertEqual(email_data.recipients, [])
        self.assertEqual(email_data.labels, [])
        self.assertIsNotNone(email_data.received_at) # Ensure it's not None
        self.assertEqual(email_data.received_at.isoformat(timespec='seconds'), now.isoformat(timespec='seconds'))

    def test_email_data_optional_fields_none(self):
        data = {
            "id": "123",
            "thread_id": None,
            "sender": None,
            "recipients": [],
            "subject": None,
            "snippet": None,
            "body": None,
            "received_at": None,
            "is_read": None,
            "labels": []
        }
        email_data = EmailData(**data)
        self.assertIsNone(email_data.thread_id)
        self.assertIsNone(email_data.sender)
        self.assertIsNone(email_data.subject)
        self.assertIsNone(email_data.snippet)
        self.assertIsNone(email_data.body)
        self.assertIsNone(email_data.received_at)
        self.assertIsNone(email_data.is_read)

    def test_email_output_valid(self):
        data = {
            "success": True,
            "operation": "create",
            "message_id": "msg123",
            "error_message": None
        }
        email_output = EmailOutput(**data)
        self.assertTrue(email_output.success)
        self.assertEqual(email_output.operation, "create")
        self.assertEqual(email_output.message_id, "msg123")
        self.assertIsNone(email_output.error_message)

    def test_email_output_failure(self):
        data = {
            "success": False,
            "operation": "delete",
            "message_id": "msg123",
            "error_message": "Failed to delete"
        }
        email_output = EmailOutput(**data)
        self.assertFalse(email_output.success)
        self.assertEqual(email_output.operation, "delete")
        self.assertEqual(email_output.message_id, "msg123")
        self.assertEqual(email_output.error_message, "Failed to delete")

    def test_email_trigger_output_valid(self):
        now = datetime.now()
        email_data = EmailData(
            id="1", thread_id="t1", sender="s@e.com", recipients=[], subject="Sub",
            snippet="Snip", body="Body", received_at=now, is_read=False, labels=[] # Pass datetime object
        )
        data = {
            "success": True,
            "emails": [email_data], # Pass EmailData object directly
            "count": 1,
            "query": "is:unread",
            "error_message": None
        }
        trigger_output = EmailTriggerOutput(**data)
        self.assertTrue(trigger_output.success)
        self.assertEqual(trigger_output.count, 1)
        self.assertEqual(trigger_output.query, "is:unread")
        self.assertEqual(trigger_output.emails[0].id, "1")

    def test_reply_email_input_valid(self):
        data = {
            "original_message_id": "orig123",
            "reply_body": "Reply text",
            "reply_all": True,
            "attachments": ["/path/to/reply_file.pdf"]
        }
        reply_input = ReplyEmailInput(**data)
        self.assertEqual(reply_input.original_message_id, "orig123")
        self.assertEqual(reply_input.reply_body, "Reply text")
        self.assertTrue(reply_input.reply_all)
        self.assertEqual(reply_input.attachments, ["/path/to/reply_file.pdf"])

    def test_move_email_input_valid(self):
        data = {
            "message_id": "move123",
            "add_labels": ["NewLabel"],
            "remove_labels": ["OldLabel"]
        }
        move_input = MoveEmailInput(**data)
        self.assertEqual(move_input.message_id, "move123")
        self.assertEqual(move_input.add_labels, ["NewLabel"])
        self.assertEqual(move_input.remove_labels, ["OldLabel"])

    def test_folder_output_valid(self):
        data = {
            "success": True,
            "operation": "create",
            "folder_name": "NewFolder",
            "label_id": "folder123",
            "error_message": None
        }
        folder_output = FolderOutput(**data)
        self.assertTrue(folder_output.success)
        self.assertEqual(folder_output.operation, "create")
        self.assertEqual(folder_output.folder_name, "NewFolder")
        self.assertEqual(folder_output.label_id, "folder123")

    def test_label_output_valid(self):
        data = {
            "success": True,
            "operation": "add_to_email",
            "label_name": "Important",
            "label_id": "label456",
            "message_id": "msg789",
            "error_message": None
        }
        label_output = LabelOutput(**data)
        self.assertTrue(label_output.success)
        self.assertEqual(label_output.operation, "add_to_email")
        self.assertEqual(label_output.label_name, "Important")
        self.assertEqual(label_output.label_id, "label456")
        self.assertEqual(label_output.message_id, "msg789")


if __name__ == '__main__':
    unittest.main()
