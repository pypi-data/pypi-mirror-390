"""
Unit-Tests für das Gmail-Helpers-Modul.

Testet die GmailService-Klasse und ihre Hilfsfunktionen mit Mocking.
"""

import unittest
from datetime import datetime
from unittest.mock import MagicMock, call, mock_open, patch

from google.auth.exceptions import RefreshError  # Added for RefreshError
from google.oauth2 import service_account  # Added for service account testing
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

from automation_lib.gmail.config.gmail_config import AuthMethod, GmailConfig
from automation_lib.gmail.gmail_auth import SCOPES
from automation_lib.gmail.gmail_helpers import GmailService
from automation_lib.gmail.schemas.gmail_schemas import EmailData, EmailInput, MoveEmailInput, ReplyEmailInput


class TestGmailHelpers(unittest.TestCase):

    def setUp(self):
        self.mock_config = MagicMock(spec=GmailConfig)
        self.mock_config.gmail_api_client_id = "mock_client_id"
        self.mock_config.gmail_api_client_secret = "mock_client_secret"
        self.mock_config.gmail_api_refresh_token = "mock_refresh_token"
        self.mock_config.gmail_default_sender_email = "test@example.com"
        self.mock_config.gmail_max_email_fetch_results = 10
        # Default to OAuth for most tests, override in specific tests
        self.mock_config.gmail_auth_method = AuthMethod.OAUTH
        self.mock_config.gmail_service_account_file = None
        self.mock_config.gmail_service_account_email = None
        self.mock_config.gmail_service_account_private_key_id = None
        self.mock_config.gmail_service_account_private_key = None
        self.mock_config.gmail_impersonate_user = None


        # Mock the build function from googleapiclient.discovery
        self.patcher_build = patch('automation_lib.gmail.gmail_helpers.build')
        self.mock_build = self.patcher_build.start()

        # Mock the InstalledAppFlow from google_auth_oauthlib.flow
        self.patcher_flow = patch('automation_lib.gmail.gmail_helpers.InstalledAppFlow')
        self.mock_flow = self.patcher_flow.start()

        # Mock the Request from google.auth.transport.requests
        self.patcher_request = patch('automation_lib.gmail.gmail_helpers.Request')
        self.mock_request = self.patcher_request.start()

        # Mock the Credentials from google.oauth2.credentials
        self.patcher_credentials = patch('automation_lib.gmail.gmail_helpers.Credentials.from_authorized_user_file')
        self.mock_from_authorized_user_file = self.patcher_credentials.start()

        # Mock the service_account.Credentials
        self.patcher_service_account_creds_file = patch('automation_lib.gmail.gmail_helpers.service_account.Credentials.from_service_account_file')
        self.mock_from_service_account_file = self.patcher_service_account_creds_file.start()
        self.patcher_service_account_creds_info = patch('automation_lib.gmail.gmail_helpers.service_account.Credentials.from_service_account_info')
        self.mock_from_service_account_info = self.patcher_service_account_creds_info.start()


        # Mock the base64.urlsafe_b64decode
        self.patcher_b64decode = patch('automation_lib.gmail.gmail_helpers.base64.urlsafe_b64decode')
        self.mock_b64decode = self.patcher_b64decode.start()

        # Mock the base64.urlsafe_b64encode
        self.patcher_b64encode = patch('automation_lib.gmail.gmail_helpers.base64.urlsafe_b64encode')
        self.mock_b64encode = self.patcher_b64encode.start()

        # Mock MIMEText and MIMEMultipart
        self.patcher_mime_text = patch('automation_lib.gmail.gmail_helpers.MIMEText')
        self.mock_mime_text = self.patcher_mime_text.start()
        self.patcher_mime_multipart = patch('automation_lib.gmail.gmail_helpers.MIMEMultipart')
        self.mock_mime_multipart = self.patcher_mime_multipart.start()

        # Mock the logger
        self.patcher_logger = patch('automation_lib.gmail.gmail_helpers.logger')
        self.mock_logger = self.patcher_logger.start()

    def tearDown(self):
        self.patcher_build.stop()
        self.patcher_flow.stop()
        self.patcher_request.stop()
        self.patcher_credentials.stop()
        self.patcher_service_account_creds_file.stop()
        self.patcher_service_account_creds_info.stop()
        self.patcher_b64decode.stop()
        self.patcher_b64encode.stop()
        self.patcher_mime_text.stop()
        self.patcher_mime_multipart.stop()
        self.patcher_logger.stop()

    def test_init_and_build_service_oauth_existing_token(self):
        mock_creds_instance = MagicMock(spec=Credentials)
        mock_creds_instance.valid = True
        mock_creds_instance.expired = False
        mock_creds_instance.refresh_token = "mock_refresh_token"
        self.mock_from_authorized_user_file.return_value = mock_creds_instance

        mock_service_object = MagicMock()
        self.mock_build.return_value = mock_service_object

        with patch('automation_lib.gmail.gmail_helpers.os.path.exists', return_value=True):
            service = GmailService(self.mock_config)
            self.assertIsInstance(service, GmailService)
            self.assertEqual(service.config, self.mock_config)
            self.assertEqual(service.service, mock_service_object)

            self.mock_from_authorized_user_file.assert_called_once_with('token.json', SCOPES)
            mock_creds_instance.refresh.assert_not_called()
            self.mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds_instance)
            self.mock_logger.info.assert_not_called() # No info log for successful token load

    def test_init_and_build_service_oauth_no_token_file(self):
        self.mock_config.gmail_api_client_id = "test_client_id"
        self.mock_config.gmail_api_client_secret = "test_client_secret"
        
        mock_flow_instance = MagicMock()
        mock_creds_from_flow = MagicMock(spec=Credentials)
        mock_creds_from_flow.to_json.return_value = '{"token": "new_token"}'
        mock_flow_instance.run_local_server.return_value = mock_creds_from_flow
        self.mock_flow.from_client_config.return_value = mock_flow_instance

        mock_service_object = MagicMock()
        self.mock_build.return_value = mock_service_object

        with patch('automation_lib.gmail.gmail_helpers.os.path.exists', return_value=False), \
             patch('builtins.open', mock_open()) as mock_file_open:
            
            service = GmailService(self.mock_config)
            self.assertIsInstance(service, GmailService)
            self.assertEqual(service.service, mock_service_object)
            
            self.mock_from_authorized_user_file.assert_not_called()
            self.mock_flow.from_client_config.assert_called_once()
            mock_flow_instance.run_local_server.assert_called_once_with(port=0)
            mock_file_open.assert_called_once_with('token.json', 'w')
            mock_file_open().write.assert_called_once_with('{"token": "new_token"}')
            self.mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds_from_flow)

    def test_init_and_build_service_oauth_expired_token_refresh_success(self):
        mock_creds_instance = MagicMock(spec=Credentials)
        mock_creds_instance.valid = False
        mock_creds_instance.expired = True
        mock_creds_instance.refresh_token = "mock_refresh_token"
        mock_creds_instance.refresh.return_value = None # Simulate successful refresh
        self.mock_from_authorized_user_file.return_value = mock_creds_instance

        mock_service_object = MagicMock()
        self.mock_build.return_value = mock_service_object

        with patch('automation_lib.gmail.gmail_helpers.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open()):
            
            service = GmailService(self.mock_config)
            self.assertIsInstance(service, GmailService)
            mock_creds_instance.refresh.assert_called_once_with(self.mock_request.return_value)
            self.mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds_instance)
            self.mock_logger.error.assert_not_called() # No error if refresh succeeds

    def test_init_and_build_service_oauth_expired_token_refresh_fail_flow_success(self):
        mock_creds_instance = MagicMock(spec=Credentials)
        mock_creds_instance.valid = False
        mock_creds_instance.expired = True
        mock_creds_instance.refresh_token = "mock_refresh_token"
        mock_creds_instance.refresh.side_effect = RefreshError("Refresh failed")
        self.mock_from_authorized_user_file.return_value = mock_creds_instance

        self.mock_config.gmail_api_client_id = "test_client_id"
        self.mock_config.gmail_api_client_secret = "test_client_secret"

        mock_flow_instance = MagicMock()
        mock_new_creds_from_flow = MagicMock(spec=Credentials)
        mock_new_creds_from_flow.to_json.return_value = '{"token": "new_token_from_flow"}'
        mock_flow_instance.run_local_server.return_value = mock_new_creds_from_flow
        self.mock_flow.from_client_config.return_value = mock_flow_instance

        mock_service_object = MagicMock()
        self.mock_build.return_value = mock_service_object

        with patch('automation_lib.gmail.gmail_helpers.os.path.exists', return_value=True), \
             patch('builtins.open', mock_open()) as mock_file_open:
            
            service = GmailService(self.mock_config)
            self.assertIsInstance(service, GmailService)
            mock_creds_instance.refresh.assert_called_once_with(self.mock_request.return_value)
            self.mock_logger.error.assert_called_once_with("Fehler beim Aktualisieren des Tokens: Refresh failed. Versuche Neuauthentifizierung.")
            self.mock_flow.from_client_config.assert_called_once()
            mock_flow_instance.run_local_server.assert_called_once_with(port=0)
            mock_file_open.assert_called_once_with('token.json', 'w')
            mock_file_open().write.assert_called_once_with('{"token": "new_token_from_flow"}')
            self.mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_new_creds_from_flow)

    def test_authenticate_service_account_from_file(self):
        self.mock_config.gmail_auth_method = AuthMethod.SERVICE_ACCOUNT
        self.mock_config.gmail_service_account_file = "/path/to/service_account.json"
        
        mock_sa_creds = MagicMock(spec=service_account.Credentials)
        self.mock_from_service_account_file.return_value = mock_sa_creds

        mock_service_object = MagicMock()
        self.mock_build.return_value = mock_service_object

        with patch('automation_lib.gmail.gmail_helpers.os.path.exists', return_value=True):
            service = GmailService(self.mock_config)
            self.assertIsInstance(service, GmailService)
            self.mock_from_service_account_file.assert_called_once_with(
                self.mock_config.gmail_service_account_file, scopes=SCOPES
            )
            self.mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_sa_creds)
            self.mock_logger.info.assert_any_call(f"Service Account authentifiziert über Datei: {self.mock_config.gmail_service_account_file}")
            self.mock_logger.info.assert_any_call("Service Account authentifiziert ohne Domain-weite Delegation.")


    def test_authenticate_service_account_from_env(self):
        self.mock_config.gmail_auth_method = AuthMethod.SERVICE_ACCOUNT
        self.mock_config.gmail_service_account_email = "sa@example.com"
        self.mock_config.gmail_service_account_private_key_id = "key_id"
        self.mock_config.gmail_service_account_private_key = "private_key"
        self.mock_config.gmail_api_client_id = "client_id_for_sa" # Reused for SA client_id

        mock_sa_creds = MagicMock(spec=service_account.Credentials)
        self.mock_from_service_account_info.return_value = mock_sa_creds

        mock_service_object = MagicMock()
        self.mock_build.return_value = mock_service_object

        service = GmailService(self.mock_config)
        self.assertIsInstance(service, GmailService)
        self.mock_from_service_account_info.assert_called_once()
        _, kwargs = self.mock_from_service_account_info.call_args
        info_dict = kwargs['info']
        self.assertEqual(info_dict['client_email'], "sa@example.com")
        self.assertEqual(info_dict['private_key_id'], "key_id")
        self.assertEqual(info_dict['private_key'], "private_key")
        self.assertEqual(info_dict['client_id'], "client_id_for_sa")
        self.assertEqual(kwargs['scopes'], SCOPES)
        
        self.mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_sa_creds)
        self.mock_logger.info.assert_any_call("Service Account authentifiziert über Umgebungsvariablen.")
        self.mock_logger.info.assert_any_call("Service Account authentifiziert ohne Domain-weite Delegation.")


    def test_authenticate_service_account_impersonation(self):
        self.mock_config.gmail_auth_method = AuthMethod.SERVICE_ACCOUNT
        self.mock_config.gmail_service_account_email = "sa@example.com"
        self.mock_config.gmail_service_account_private_key_id = "key_id"
        self.mock_config.gmail_service_account_private_key = "private_key"
        self.mock_config.gmail_impersonate_user = "impersonated@example.com"
        self.mock_config.gmail_api_client_id = "client_id_for_sa"

        mock_sa_creds = MagicMock(spec=service_account.Credentials)
        self.mock_from_service_account_info.return_value = mock_sa_creds # This will be called twice

        mock_service_object = MagicMock()
        self.mock_build.return_value = mock_service_object

        service = GmailService(self.mock_config)
        self.assertIsInstance(service, GmailService)
        # First call to from_service_account_info for base creds, then for delegated creds
        self.assertEqual(self.mock_from_service_account_info.call_count, 2)
        
        # Check the second call for impersonation
        _, kwargs = self.mock_from_service_account_info.call_args_list[1]
        self.assertEqual(kwargs['subject'], "impersonated@example.com")
        self.assertEqual(kwargs['scopes'], SCOPES)
        
        self.mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_sa_creds)
        self.mock_logger.info.assert_any_call(f"Service Account authentifiziert mit Domain-weiter Delegation für Benutzer: {self.mock_config.gmail_impersonate_user}")

    def test_authenticate_service_account_incomplete_config(self):
        self.mock_config.gmail_auth_method = AuthMethod.SERVICE_ACCOUNT
        self.mock_config.gmail_service_account_file = None # No file
        self.mock_config.gmail_service_account_email = "sa@example.com" # Missing other env vars
        
        with self.assertRaisesRegex(ValueError, "Service Account-Konfiguration unvollständig"):
            GmailService(self.mock_config)
        self.mock_from_service_account_file.assert_not_called()
        self.mock_from_service_account_info.assert_not_called()

    def test_parse_email_message(self):
        mock_message = {
            'id': 'msg123',
            'threadId': 'thd123',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'Sender Name <sender@example.com>'},
                    {'name': 'To', 'value': 'Recipient Name <recipient@example.com>'},
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'Date', 'value': 'Thu, 04 Jul 2025 10:00:00 +0200'}
                ],
                'parts': [
                    {'mimeType': 'text/plain', 'body': {'data': 'SGVsbG8gV29ybGQ='}}, # Base64 for "Hello World"
                    {'mimeType': 'text/html', 'body': {'data': 'PGh0bWw+SGVsbG8gV29ybGQ8L2h0bWw+'}}
                ]
            },
            'snippet': 'Hello World',
            'labelIds': ['INBOX', 'UNREAD']
        }
        self.mock_b64decode.side_effect = [b'Hello World', b'<html>Hello World</html>']

        service = GmailService(self.mock_config)
        email_data = service._parse_email_message(mock_message)

        self.assertIsInstance(email_data, EmailData)
        self.assertEqual(email_data.id, 'msg123')
        self.assertEqual(email_data.thread_id, 'thd123')
        self.assertEqual(email_data.sender, 'sender@example.com')
        self.assertEqual(email_data.recipients, ['recipient@example.com'])
        self.assertEqual(email_data.subject, 'Test Subject')
        self.assertEqual(email_data.snippet, 'Hello World')
        self.assertEqual(email_data.body, 'Hello World')
        self.assertIsInstance(email_data.received_at, datetime)
        self.assertFalse(email_data.is_read)
        self.assertEqual(email_data.labels, ['INBOX', 'UNREAD'])
        self.mock_b64decode.assert_has_calls([
            call('SGVsbG8gV29ybGQ='),
            call('PGh0bWw+SGVsbG8gV29ybGQ8L2h0bWw+')
        ])

    def test_parse_email_message_no_body_data(self):
        mock_message = {
            'id': 'msg123',
            'threadId': 'thd123',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'Subject', 'value': 'Test Subject'}
                ],
                'parts': [
                    {'mimeType': 'text/plain', 'body': {}},
                ]
            },
            'snippet': 'No body',
            'labelIds': ['INBOX']
        }
        service = GmailService(self.mock_config)
        email_data = service._parse_email_message(mock_message)
        self.assertEqual(email_data.body, '')
        self.mock_b64decode.assert_not_called()

    def test_get_label_id_existing(self):
        mock_labels_list = MagicMock()
        mock_labels_list.list.return_value.execute.return_value = {
            'labels': [
                {'id': 'LABEL_1', 'name': 'ExistingLabel'},
                {'id': 'LABEL_2', 'name': 'AnotherLabel'}
            ]
        }
        self.mock_build.return_value.users.return_value.labels.return_value = mock_labels_list

        service = GmailService(self.mock_config)
        label_id = service._get_label_id("ExistingLabel")
        self.assertEqual(label_id, 'LABEL_1')
        mock_labels_list.list.assert_called_once_with(userId='me')

    def test_get_label_id_not_existing(self):
        mock_labels_list = MagicMock()
        mock_labels_list.list.return_value.execute.return_value = {
            'labels': [
                {'id': 'LABEL_1', 'name': 'ExistingLabel'}
            ]
        }
        self.mock_build.return_value.users.return_value.labels.return_value = mock_labels_list

        service = GmailService(self.mock_config)
        label_id = service._get_label_id("NonExistingLabel")
        self.assertIsNone(label_id)

    @patch('automation_lib.gmail.gmail_helpers.GmailService._parse_email_message')
    def test_search_emails_success(self, mock_parse_email_message):
        mock_messages_list = MagicMock()
        mock_messages_list.list.return_value.execute.return_value = {
            'messages': [{'id': 'msg1'}, {'id': 'msg2'}],
            'nextPageToken': 'token'
        }
        mock_messages_list.get.side_effect = [
            MagicMock(execute=lambda: {'id': 'msg1', 'payload': {'headers': []}, 'snippet': 's1', 'labelIds': []}),
            MagicMock(execute=lambda: {'id': 'msg2', 'payload': {'headers': []}, 'snippet': 's2', 'labelIds': []})
        ]
        self.mock_build.return_value.users.return_value.messages.return_value = mock_messages_list
        mock_parse_email_message.side_effect = [
            EmailData(id='msg1', thread_id='t1', sender='s1@e.com', recipients=[], subject='sub1', snippet='s1', body='b1', received_at=datetime.now(), is_read=False, labels=[]),
            EmailData(id='msg2', thread_id='t2', sender='s2@e.com', recipients=[], subject='sub2', snippet='s2', body='b2', received_at=datetime.now(), is_read=False, labels=[])
        ]

        service = GmailService(self.mock_config)
        emails = service.search_emails("test query", 2)

        self.assertEqual(len(emails), 2)
        self.assertEqual(emails[0].id, 'msg1')
        self.assertEqual(emails[1].id, 'msg2')
        mock_messages_list.list.assert_called_once_with(userId='me', q='test query', maxResults=2)
        mock_messages_list.get.assert_has_calls([
            call(userId='me', id='msg1', format='full'),
            call(userId='me', id='msg2', format='full')
        ])
        mock_parse_email_message.assert_has_calls([call({'id': 'msg1', 'payload': {'headers': []}, 'snippet': 's1', 'labelIds': []}),
                                                   call({'id': 'msg2', 'payload': {'headers': []}, 'snippet': 's2', 'labelIds': []})])

    def test_search_emails_no_messages(self):
        mock_messages_list = MagicMock()
        mock_messages_list.list.return_value.execute.return_value = {}
        self.mock_build.return_value.users.return_value.messages.return_value = mock_messages_list

        service = GmailService(self.mock_config)
        emails = service.search_emails("no results", 5)
        self.assertEqual(len(emails), 0)
        mock_messages_list.list.assert_called_once_with(userId='me', q='no results', maxResults=5)

    def test_send_email_text_only(self):
        email_input = EmailInput(
            to=["to@example.com"],
            subject="Test Subject",
            body="Test Body",
            cc=[],
            bcc=[],
            attachments=[]
        )
        mock_message_create = MagicMock()
        mock_message_create.send.return_value.execute.return_value = {'id': 'sent_msg_id'}
        self.mock_build.return_value.users.return_value.messages.return_value = mock_message_create

        mock_mime_text_instance = MagicMock()
        mock_mime_text_instance.as_string.return_value = "MIME_TEXT_STRING"
        self.mock_mime_text.return_value = mock_mime_text_instance

        self.mock_b64encode.return_value = b'base64_encoded_raw_message'

        service = GmailService(self.mock_config)
        message_id = service.send_email(email_input)

        self.assertEqual(message_id, 'sent_msg_id')
        self.mock_mime_text.assert_called_once_with("Test Body")
        mock_mime_text_instance['to'] = "to@example.com"
        mock_mime_text_instance['subject'] = "Test Subject"
        mock_message_create.send.assert_called_once_with(
            userId='me',
            body={'raw': 'base64_encoded_raw_message'}
        )

    def test_send_email_with_attachments(self):
        email_input = EmailInput(
            to=["to@example.com"],
            subject="Test Subject",
            body="Test Body",
            cc=[],
            bcc=[],
            attachments=["/path/to/file.txt"]
        )
        mock_message_create = MagicMock()
        mock_message_create.send.return_value.execute.return_value = {'id': 'sent_msg_id_attach'}
        self.mock_build.return_value.users.return_value.messages.return_value = mock_message_create

        mock_mime_multipart_instance = MagicMock()
        mock_mime_multipart_instance.as_string.return_value = "MIME_MULTIPART_STRING"
        self.mock_mime_multipart.return_value = mock_mime_multipart_instance

        self.mock_b64encode.return_value = b'base64_encoded_raw_message_attach'

        with patch('builtins.open', mock_open(read_data=b"file content")), \
             patch('automation_lib.gmail.gmail_helpers.os.path.basename', return_value="file.txt"):
            
            service = GmailService(self.mock_config)
            message_id = service.send_email(email_input)

            self.assertEqual(message_id, 'sent_msg_id_attach')
            self.mock_mime_multipart.assert_called_once_with()
            self.mock_mime_text.assert_called_once_with("Test Body")
            mock_mime_multipart_instance.attach.assert_any_call(self.mock_mime_text.return_value)
            mock_message_create.send.assert_called_once_with(
                userId='me',
                body={'raw': 'base64_encoded_raw_message_attach'}
            )

    def test_reply_to_email(self):
        reply_input = ReplyEmailInput(
            original_message_id="original_msg_id",
            reply_body="This is a reply.",
            reply_all=False,
            attachments=[]
        )
        mock_message_get = MagicMock()
        mock_message_get.get.return_value.execute.return_value = {
            'id': 'original_msg_id',
            'threadId': 'original_thread_id',
            'payload': {
                'headers': [
                    {'name': 'From', 'value': 'original_sender@example.com'},
                    {'name': 'To', 'value': 'test@example.com'},
                    {'name': 'Subject', 'value': 'Original Subject'}
                ]
            }
        }
        mock_message_send = MagicMock()
        mock_message_send.send.return_value.execute.return_value = {'id': 'reply_msg_id'}
        self.mock_build.return_value.users.return_value.messages.return_value = MagicMock(
            get=mock_message_get.get, send=mock_message_send.send
        )
        self.mock_b64encode.return_value = b'base64_encoded_reply_message'

        service = GmailService(self.mock_config)
        reply_id = service.reply_to_email(reply_input)

        self.assertEqual(reply_id, 'reply_msg_id')
        mock_message_get.get.assert_called_once_with(userId='me', id='original_msg_id', format='full')
        mock_message_send.send.assert_called_once_with(
            userId='me',
            body={'raw': 'base64_encoded_reply_message'},
            threadId='original_thread_id'
        )
        mock_mime_multipart_instance = self.mock_mime_multipart.return_value
        mock_mime_multipart_instance.__setitem__.assert_any_call('to', 'original_sender@example.com')
        mock_mime_multipart_instance.__setitem__.assert_any_call('subject', 'Re: Original Subject')
        mock_mime_multipart_instance.__setitem__.assert_any_call('In-Reply-To', 'original_msg_id')
        mock_mime_multipart_instance.__setitem__.assert_any_call('References', 'original_thread_id')
        self.mock_mime_text.assert_called_once_with("This is a reply.")
        mock_mime_multipart_instance.attach.assert_any_call(self.mock_mime_text.return_value)

    def test_delete_email(self):
        mock_message_trash = MagicMock()
        mock_message_trash.trash.return_value.execute.return_value = None
        self.mock_build.return_value.users.return_value.messages.return_value = mock_message_trash

        service = GmailService(self.mock_config)
        service.delete_email("msg_to_delete")
        mock_message_trash.trash.assert_called_once_with(userId='me', id='msg_to_delete')

    def test_move_email(self):
        move_input = MoveEmailInput(
            message_id="msg_to_move",
            add_labels=["ADD_LABEL_ID"],
            remove_labels=["REMOVE_LABEL_ID"]
        )
        mock_message_modify = MagicMock()
        mock_message_modify.modify.return_value.execute.return_value = {'id': 'msg_to_move'}
        self.mock_build.return_value.users.return_value.messages.return_value = mock_message_modify

        with patch('automation_lib.gmail.gmail_helpers.GmailService._get_label_id', side_effect=['ADD_LABEL_ID', 'REMOVE_LABEL_ID']):
            service = GmailService(self.mock_config)
            service.move_email(move_input)
            mock_message_modify.modify.assert_called_once_with(
                userId='me',
                id='msg_to_move',
                body={'addLabelIds': ['ADD_LABEL_ID'], 'removeLabelIds': ['REMOVE_LABEL_ID']}
            )

    def test_create_label(self):
        mock_labels_create = MagicMock()
        mock_labels_create.create.return_value.execute.return_value = {'id': 'new_label_id', 'name': 'NewLabel'}
        self.mock_build.return_value.users.return_value.labels.return_value = mock_labels_create

        service = GmailService(self.mock_config)
        label_id = service.create_label("NewLabel")
        self.assertEqual(label_id, 'new_label_id')
        mock_labels_create.create.assert_called_once_with(
            userId='me',
            body={'name': 'NewLabel', 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
        )

    def test_delete_label(self):
        mock_labels_delete = MagicMock()
        mock_labels_delete.delete.return_value.execute.return_value = None
        self.mock_build.return_value.users.return_value.labels.return_value = mock_labels_delete

        with patch('automation_lib.gmail.gmail_helpers.GmailService._get_label_id', return_value='LABEL_TO_DELETE_ID'):
            service = GmailService(self.mock_config)
            service.delete_label("LabelToDelete")
            mock_labels_delete.delete.assert_called_once_with(userId='me', id='LABEL_TO_DELETE_ID')

    def test_add_label_to_email(self):
        mock_message_modify = MagicMock()
        mock_message_modify.modify.return_value.execute.return_value = {'id': 'msg_id'}
        self.mock_build.return_value.users.return_value.messages.return_value = mock_message_modify

        with patch('automation_lib.gmail.gmail_helpers.GmailService._get_label_id', return_value='LABEL_TO_ADD_ID'):
            service = GmailService(self.mock_config)
            service.add_label_to_email("msg_id", "LabelToAdd")
            mock_message_modify.modify.assert_called_once_with(
                userId='me',
                id='msg_id',
                body={'addLabelIds': ['LABEL_TO_ADD_ID'], 'removeLabelIds': []}
            )

    def test_api_error_handling(self):
        mock_messages_list = MagicMock()
        mock_messages_list.list.return_value.execute.side_effect = HttpError(MagicMock(status=404), b'Not Found')
        self.mock_build.return_value.users.return_value.messages.return_value = mock_messages_list

        service = GmailService(self.mock_config)
        with self.assertRaises(HttpError):
            service.search_emails("error query", 1)
        self.mock_logger.error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
