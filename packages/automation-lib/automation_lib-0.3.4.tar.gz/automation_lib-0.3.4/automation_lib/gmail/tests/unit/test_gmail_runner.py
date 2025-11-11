"""
Unit-Tests für das Gmail-Runner-Modul.

Testet einzelne Funktionen des gmail_runner.py mit Mocking.
"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

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
from automation_lib.gmail.schemas.gmail_schemas import (
    EmailData,
    EmailInput,
    MoveEmailInput,
    ReplyEmailInput,
)


class TestGmailRunner(unittest.TestCase):

    def setUp(self):
        # Mock the GmailConfig to avoid actual config loading
        self.mock_config = MagicMock(spec=GmailConfig)
        self.mock_config.gmail_api_client_id = "mock_client_id"
        self.mock_config.gmail_api_client_secret = "mock_client_secret"
        self.mock_config.gmail_api_refresh_token = "mock_refresh_token"
        self.mock_config.gmail_default_sender_email = "test@example.com"

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_check_new_emails_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        
        mock_email_data = [
            EmailData(
                id="123", thread_id="t1", sender="sender1@example.com",
                recipients=["test@example.com"], subject="Test Subject 1",
                snippet="Snippet 1", body="Body 1", received_at=datetime.now(),
                is_read=False, labels=["INBOX", "UNREAD"]
            )
        ]
        mock_service_instance.search_emails.return_value = mock_email_data

        result = check_new_emails(query="is:unread", max_results=1, config=self.mock_config)
        
        self.assertTrue(result.success)
        self.assertEqual(result.count, 1)
        self.assertEqual(result.emails[0].id, "123")
        MockGmailService.assert_called_once_with(self.mock_config)
        mock_service_instance.search_emails.assert_called_once_with("is:unread", 1)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_create_email_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.send_email.return_value = "new_message_id_123"

        email_input = EmailInput(
            to=["recipient@example.com"],
            subject="Test Email",
            body="Hello World",
            cc=[], bcc=[], attachments=[]
        )
        result = create_email(email_input, config=self.mock_config)

        self.assertTrue(result.success)
        self.assertEqual(result.message_id, "new_message_id_123")
        self.assertEqual(result.operation, "create")
        mock_service_instance.send_email.assert_called_once_with(email_input)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_reply_to_email_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.reply_to_email.return_value = "reply_message_id_456"

        reply_input = ReplyEmailInput(
            original_message_id="original_id",
            reply_body="This is a reply.",
            reply_all=False,
            attachments=[]
        )
        result = reply_to_email(reply_input, config=self.mock_config)

        self.assertTrue(result.success)
        self.assertEqual(result.message_id, "reply_message_id_456")
        self.assertEqual(result.operation, "reply")
        mock_service_instance.reply_to_email.assert_called_once_with(reply_input)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_delete_email_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.delete_email.return_value = None # delete_email doesn't return anything

        result = delete_email("message_to_delete_id", config=self.mock_config)

        self.assertTrue(result.success)
        self.assertEqual(result.message_id, "message_to_delete_id")
        self.assertEqual(result.operation, "delete")
        mock_service_instance.delete_email.assert_called_once_with("message_to_delete_id")

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_move_email_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.move_email.return_value = None

        move_input = MoveEmailInput(
            message_id="message_to_move_id",
            add_labels=["Important"],
            remove_labels=["Inbox"]
        )
        result = move_email(move_input, config=self.mock_config)

        self.assertTrue(result.success)
        self.assertEqual(result.message_id, "message_to_move_id")
        self.assertEqual(result.operation, "move")
        mock_service_instance.move_email.assert_called_once_with(move_input)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_create_folder_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.create_label.return_value = "new_label_id_789"

        result = create_folder("NewFolder", config=self.mock_config)

        self.assertTrue(result.success)
        self.assertEqual(result.folder_name, "NewFolder")
        self.assertEqual(result.label_id, "new_label_id_789")
        self.assertEqual(result.operation, "create")
        mock_service_instance.create_label.assert_called_once_with("NewFolder")

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_delete_folder_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.delete_label.return_value = None

        result = delete_folder("OldFolder", config=self.mock_config)

        self.assertTrue(result.success)
        self.assertEqual(result.folder_name, "OldFolder")
        self.assertEqual(result.operation, "delete")
        mock_service_instance.delete_label.assert_called_once_with("OldFolder")

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_create_label_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.create_label.return_value = "new_label_id_abc"

        result = create_label("MyCustomLabel", config=self.mock_config)

        self.assertTrue(result.success)
        self.assertEqual(result.label_name, "MyCustomLabel")
        self.assertEqual(result.label_id, "new_label_id_abc")
        self.assertEqual(result.operation, "create")
        mock_service_instance.create_label.assert_called_once_with("MyCustomLabel")

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_add_label_to_email_success(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.add_label_to_email.return_value = None

        result = add_label_to_email("email_id_to_label", "Important", config=self.mock_config)

        self.assertTrue(result.success)
        self.assertEqual(result.label_name, "Important")
        self.assertEqual(result.message_id, "email_id_to_label")
        self.assertEqual(result.operation, "add_to_email")
        mock_service_instance.add_label_to_email.assert_called_once_with("email_id_to_label", "Important")

    # Test error cases for each function
    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_check_new_emails_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.search_emails.side_effect = Exception("API Error")

        result = check_new_emails(config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("API Error", result.error_message or "") # Handle None case
        self.assertEqual(result.emails, [])
        self.assertEqual(result.count, 0)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_create_email_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.send_email.side_effect = Exception("Send Error")

        email_input = EmailInput(to=["test@example.com"], subject="Sub", body="Body", cc=[], bcc=[], attachments=[])
        result = create_email(email_input, config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("Send Error", result.error_message or "") # Handle None case
        self.assertIsNone(result.message_id)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_reply_to_email_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.reply_to_email.side_effect = Exception("Reply Error")

        reply_input = ReplyEmailInput(original_message_id="id", reply_body="body", reply_all=False, attachments=[])
        result = reply_to_email(reply_input, config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("Reply Error", result.error_message or "") # Handle None case
        self.assertIsNone(result.message_id)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_delete_email_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.delete_email.side_effect = Exception("Delete Error")

        result = delete_email("id_to_delete", config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("Delete Error", result.error_message or "") # Handle None case
        self.assertEqual(result.message_id, "id_to_delete") # Message ID should still be present

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_move_email_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.move_email.side_effect = Exception("Move Error")

        move_input = MoveEmailInput(message_id="id_to_move", add_labels=["Label"], remove_labels=[])
        result = move_email(move_input, config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("Move Error", result.error_message or "") # Handle None case
        self.assertEqual(result.message_id, "id_to_move")

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_create_folder_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.create_label.side_effect = Exception("Folder Create Error")

        result = create_folder("NewFolder", config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("Folder Create Error", result.error_message or "") # Handle None case
        self.assertEqual(result.folder_name, "NewFolder")
        self.assertIsNone(result.label_id)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_delete_folder_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.delete_label.side_effect = Exception("Folder Delete Error")

        result = delete_folder("OldFolder", config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("Folder Delete Error", result.error_message or "") # Handle None case
        self.assertEqual(result.folder_name, "OldFolder")
        self.assertIsNone(result.label_id)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_create_label_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.create_label.side_effect = Exception("Label Create Error")

        result = create_label("MyLabel", config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("Label Create Error", result.error_message or "") # Handle None case
        self.assertEqual(result.label_name, "MyLabel")
        self.assertIsNone(result.label_id)

    @patch('automation_lib.gmail.gmail_runner.GmailService')
    @patch('automation_lib.gmail.gmail_runner.GmailConfig')
    def test_add_label_to_email_failure(self, MockGmailConfig, MockGmailService):
        MockGmailConfig.return_value = self.mock_config
        mock_service_instance = MockGmailService.return_value
        mock_service_instance.add_label_to_email.side_effect = Exception("Add Label Error")

        result = add_label_to_email("email_id", "LabelName", config=self.mock_config)
        self.assertFalse(result.success)
        self.assertIn("Add Label Error", result.error_message or "") # Handle None case
        self.assertEqual(result.label_name, "LabelName")
        self.assertEqual(result.message_id, "email_id")
        self.assertIsNone(result.label_id)


if __name__ == '__main__':
    unittest.main()
