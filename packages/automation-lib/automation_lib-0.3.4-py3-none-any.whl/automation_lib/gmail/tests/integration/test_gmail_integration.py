"""
Integrationstests für das Gmail-Modul.

Diese Tests interagieren mit der echten Gmail API.
Stellen Sie sicher, dass die Umgebungsvariablen in .env.test korrekt gesetzt sind
und Sie die erforderlichen OAuth 2.0 Credentials haben.
"""

import logging
import os
import sys
import time
import unittest
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[4]))

from dotenv import load_dotenv  # Re-add load_dotenv

from automation_lib.gmail.config.gmail_config import GmailConfig  # Import AuthMethod
from automation_lib.gmail.gmail_runner import (
    add_label_to_email,
    check_new_emails,
    create_email,
    create_label,
    delete_email,
    delete_folder,
    move_email,
    reply_to_email,
)
from automation_lib.gmail.schemas.gmail_schemas import EmailInput, MoveEmailInput, ReplyEmailInput

# Load environment variables from .env.test for os.getenv calls
load_dotenv(Path(__file__).resolve().parent / ".env.test")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if integration tests should run
RUN_INTEGRATION_TESTS = os.getenv("RUN_GMAIL_INTEGRATION_TESTS", "false").lower() == "true"

# Get test specific emails
TEST_RECIPIENT_EMAIL = os.getenv("GMAIL_TEST_RECIPIENT_EMAIL")
TEST_SENDER_EMAIL = os.getenv("GMAIL_TEST_SENDER_EMAIL") # This should be the authenticated user's email


@unittest.skipUnless(RUN_INTEGRATION_TESTS, "Gmail Integration tests skipped, set RUN_GMAIL_INTEGRATION_TESTS=true in .env.test")
class TestGmailIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load config from .env.test based on auth method
        # Pass the .env.test file path directly to the GmailConfig constructor
        cls.config = GmailConfig(env_file=str(Path(__file__).resolve().parent / ".env.test"))
        auth_method_display = cls.config.gmail_auth_method.upper() if cls.config.gmail_auth_method else "NONE"
        logger.info(f"Using {auth_method_display} authentication for integration tests.")

        cls.test_label_name = "AutomationTestLabel"
        cls.test_email_subject = f"Integration Test Email - {time.time()}"
        cls.sent_message_id = None # To store message ID for cleanup

        if not TEST_RECIPIENT_EMAIL or not TEST_SENDER_EMAIL:
            raise ValueError("GMAIL_TEST_RECIPIENT_EMAIL and GMAIL_TEST_SENDER_EMAIL must be set in .env.test for integration tests.")
        
        logger.info(f"Running Gmail Integration Tests with sender: {TEST_SENDER_EMAIL}, recipient: {TEST_RECIPIENT_EMAIL}")

        # Ensure the test label exists for some tests, create if not
        try:
            create_label_result = create_label(cls.test_label_name, config=cls.config)
            if create_label_result.success:
                logger.info(f"Test label '{cls.test_label_name}' ensured.")
            else:
                logger.warning(f"Could not ensure test label: {create_label_result.error_message}")
        except Exception as e:
            logger.warning(f"Exception ensuring test label: {e}")


    @classmethod
    def tearDownClass(cls):
        # Clean up: delete the test label
        try:
            delete_folder_result = delete_folder(cls.test_label_name, config=cls.config)
            if delete_folder_result.success:
                logger.info(f"Test label '{cls.test_label_name}' cleaned up.")
            else:
                logger.warning(f"Could not clean up test label: {delete_folder_result.error_message}")
        except Exception as e:
            logger.warning(f"Exception during test label cleanup: {e}")
        
        # Clean up: delete the sent email if it exists
        if cls.sent_message_id:
            try:
                delete_email_result = delete_email(cls.sent_message_id, config=cls.config)
                if delete_email_result.success:
                    logger.info(f"Sent email '{cls.sent_message_id}' cleaned up.")
                else:
                    logger.warning(f"Could not clean up sent email: {delete_email_result.error_message}")
            except Exception as e:
                logger.warning(f"Exception during sent email cleanup: {e}")


    def test_1_create_and_send_email(self):
        logger.info("\n--- Running test_1_create_and_send_email ---")
        email_input = EmailInput(
            to=[TEST_RECIPIENT_EMAIL] if TEST_RECIPIENT_EMAIL else [], # Ensure it's a list of strings
            subject=self.test_email_subject,
            body="This is an integration test email sent by automation_lib Gmail module.",
            cc=[], bcc=[], attachments=[]
        )
        result = create_email(email_input=email_input, config=self.config)
        self.assertTrue(result.success, f"Email creation failed: {result.error_message}")
        self.assertIsNotNone(result.message_id)
        self.assertEqual(result.operation, "create")
        TestGmailIntegration.sent_message_id = result.message_id
        logger.info(f"Email sent with ID: {result.message_id}")
        time.sleep(5) # Give Gmail time to process

    def test_2_check_new_emails(self):
        logger.info("\n--- Running test_2_check_new_emails ---")
        # Search for the email sent in test_1
        query = f"subject:\"{self.test_email_subject}\" to:{TEST_RECIPIENT_EMAIL}"
        result = check_new_emails(query=query, max_results=1, config=self.config)
        self.assertTrue(result.success, f"Check new emails failed: {result.error_message}")
        self.assertGreaterEqual(result.count, 1, f"Email with subject '{self.test_email_subject}' not found.")
        self.assertEqual(result.emails[0].subject, self.test_email_subject)
        logger.info(f"Found email with subject: {result.emails[0].subject}")
        
        # Store the found message ID for reply/move tests if it's different from sent_message_id
        # (e.g., if we're testing receiving an email from external source)
        if not TestGmailIntegration.sent_message_id:
            TestGmailIntegration.sent_message_id = result.emails[0].id


    def test_3_add_label_to_email(self):
        logger.info("\n--- Running test_3_add_label_to_email ---")
        if not TestGmailIntegration.sent_message_id:
            self.skipTest("No message ID available to add label to.")
        
        result = add_label_to_email(
            message_id=TestGmailIntegration.sent_message_id,
            label_name=self.test_label_name,
            config=self.config
        )
        self.assertTrue(result.success, f"Add label to email failed: {result.error_message}")
        self.assertEqual(result.label_name, self.test_label_name)
        self.assertEqual(result.message_id, TestGmailIntegration.sent_message_id)
        logger.info(f"Label '{self.test_label_name}' added to email '{TestGmailIntegration.sent_message_id}'.")
        time.sleep(2) # Give Gmail time to process

    def test_4_move_email_by_removing_label(self):
        logger.info("\n--- Running test_4_move_email_by_removing_label ---")
        if not TestGmailIntegration.sent_message_id:
            self.skipTest("No message ID available to move email.")
        
        # Remove INBOX label (effectively moves it out of inbox)
        move_input = MoveEmailInput(
            message_id=TestGmailIntegration.sent_message_id,
            add_labels=[],
            remove_labels=["INBOX"]
        )
        result = move_email(move_input=move_input, config=self.config)
        self.assertTrue(result.success, f"Move email failed: {result.error_message}")
        self.assertEqual(result.message_id, TestGmailIntegration.sent_message_id)
        logger.info(f"Email '{TestGmailIntegration.sent_message_id}' moved out of INBOX.")
        time.sleep(2) # Give Gmail time to process

    def test_5_reply_to_email(self):
        logger.info("\n--- Running test_5_reply_to_email ---")
        if not TestGmailIntegration.sent_message_id:
            self.skipTest("No message ID available to reply to.")
        
        reply_body = "This is an automated reply from the integration test."
        reply_input = ReplyEmailInput(
            original_message_id=TestGmailIntegration.sent_message_id,
            reply_body=reply_body,
            reply_all=False,
            attachments=[]
        )
        result = reply_to_email(reply_input=reply_input, config=self.config)
        self.assertTrue(result.success, f"Reply to email failed: {result.error_message}")
        self.assertIsNotNone(result.message_id)
        logger.info(f"Replied to email '{TestGmailIntegration.sent_message_id}'. New message ID: {result.message_id}")
        time.sleep(5) # Give Gmail time to process

    def test_6_delete_email(self):
        logger.info("\n--- Running test_6_delete_email ---")
        if not TestGmailIntegration.sent_message_id:
            self.skipTest("No message ID available to delete.")
        
        result = delete_email(message_id=TestGmailIntegration.sent_message_id, config=self.config)
        self.assertTrue(result.success, f"Delete email failed: {result.error_message}")
        self.assertEqual(result.message_id, TestGmailIntegration.sent_message_id)
        logger.info(f"Email '{TestGmailIntegration.sent_message_id}' deleted.")
        TestGmailIntegration.sent_message_id = None # Clear for cleanup


if __name__ == '__main__':
    unittest.main()
