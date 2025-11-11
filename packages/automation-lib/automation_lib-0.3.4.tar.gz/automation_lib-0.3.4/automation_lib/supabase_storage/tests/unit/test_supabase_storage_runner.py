# automation_lib/supabase_storage/tests/unit/test_supabase_storage_runner.py

import unittest
from unittest.mock import Mock, mock_open, patch

from automation_lib.supabase_storage.config.supabase_storage_config import SupabaseStorageConfig
from automation_lib.supabase_storage.schemas.supabase_storage_schemas import (
    DeleteFileOutput,
    DeleteFilesOutput,
    DownloadFileOutput,
    ListFilesOutput,
    UploadFileOutput,
)
from automation_lib.supabase_storage.supabase_storage_runner import delete_file, delete_files, download_file, list_bucket_files, upload_file


class TestSupabaseStorageRunner(unittest.TestCase):
    
    def setUp(self):
        """Setup für jeden Test"""
        self.mock_config = SupabaseStorageConfig(
            supabase_url="https://test.supabase.co",
            supabase_key="test-key",
            default_bucket_name="test-bucket",
            download_timeout_seconds=300,
            max_file_size_mb=100,
            max_batch_delete_size=100
        )
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    def test_list_bucket_files_success(self, mock_load_config, mock_create_client):
        """Test erfolgreiches Auflisten von Dateien"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_create_client.return_value = mock_client
        
        # Mock response von Supabase
        mock_bucket.list.return_value = [
            {"name": "test1.txt", "id": "1", "updated_at": "2023-01-01T00:00:00Z"},
            {"name": "test2.txt", "id": "2", "updated_at": "2023-01-02T00:00:00Z"}
        ]
        
        # Test ausführen
        result = list_bucket_files()
        
        # Assertions
        self.assertIsInstance(result, ListFilesOutput)
        self.assertEqual(len(result.files), 2)
        self.assertEqual(result.files[0].name, "test1.txt")
        self.assertEqual(result.files[1].name, "test2.txt")
        mock_bucket.list.assert_called_once()
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    @patch('builtins.open', new_callable=mock_open)
    @patch('automation_lib.supabase_storage.supabase_storage_runner.ensure_directory_exists')
    def test_download_file_success(self, mock_ensure_dir, mock_file_open, mock_load_config, mock_create_client):
        """Test erfolgreiches Herunterladen einer Datei"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_create_client.return_value = mock_client
        
        # Mock file content
        test_content = b"test file content"
        mock_bucket.download.return_value = test_content
        
        # Test ausführen
        result = download_file("test.txt", "/local/test.txt")
        
        # Assertions
        self.assertIsInstance(result, DownloadFileOutput)
        self.assertTrue(result.success)
        self.assertEqual(result.local_path, "/local/test.txt")
        self.assertEqual(result.file_size_bytes, len(test_content))
        mock_bucket.download.assert_called_once()
        mock_file_open.assert_called_once_with("/local/test.txt", "wb")
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    def test_delete_file_success(self, mock_load_config, mock_create_client):
        """Test erfolgreiches Löschen einer Datei"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_create_client.return_value = mock_client
        
        # Mock successful delete
        mock_bucket.remove.return_value = {"message": "success"}
        
        # Test ausführen
        result = delete_file("test.txt")
        
        # Assertions
        self.assertIsInstance(result, DeleteFileOutput)
        self.assertTrue(result.success)
        self.assertEqual(result.remote_path, "test.txt")
        mock_bucket.remove.assert_called_once_with(["test.txt"])
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    def test_delete_files_success(self, mock_load_config, mock_create_client):
        """Test erfolgreiches Löschen mehrerer Dateien"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_create_client.return_value = mock_client
        
        # Mock successful batch delete
        mock_bucket.remove.return_value = {"message": "success"}
        
        # Test ausführen
        test_files = ["test1.txt", "test2.txt", "test3.txt"]
        result = delete_files(test_files)
        
        # Assertions
        self.assertIsInstance(result, DeleteFilesOutput)
        self.assertEqual(len(result.successful_deletes), 3)
        self.assertEqual(len(result.failed_deletes), 0)
        self.assertTrue(all(result.results[file] for file in test_files))
        mock_bucket.remove.assert_called_once()
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    def test_list_bucket_files_error(self, mock_load_config, mock_create_client):
        """Test Fehlerbehandlung beim Auflisten von Dateien"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_create_client.return_value = mock_client
        
        # Mock error
        mock_bucket.list.side_effect = Exception("Connection error")
        
        # Test ausführen und Exception erwarten
        with self.assertRaises(ConnectionError):
            list_bucket_files()
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    def test_download_file_error(self, mock_load_config, mock_create_client):
        """Test Fehlerbehandlung beim Herunterladen einer Datei"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_create_client.return_value = mock_client
        
        # Mock error
        mock_bucket.download.side_effect = Exception("File not found")
        
        # Test ausführen
        result = download_file("nonexistent.txt", "/local/test.txt")
        
        # Assertions
        self.assertIsInstance(result, DownloadFileOutput)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.message)
        self.assertIn("Error downloading file:", result.message or "")
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.validate_file_size')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"test file content")
    def test_upload_file_success(self, mock_file_open, mock_exists, mock_getsize, mock_validate_size, mock_load_config, mock_create_client):
        """Test erfolgreiches Hochladen einer Datei"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.storage.from_.return_value = mock_bucket
        mock_create_client.return_value = mock_client
        
        # Mock file system
        mock_exists.return_value = True
        mock_getsize.return_value = 17  # Länge von "test file content"
        mock_validate_size.return_value = True
        
        # Mock successful upload
        mock_bucket.upload.return_value = {"message": "success"}
        
        # Test ausführen
        result = upload_file("/local/test.txt", "remote/test.txt")
        
        # Assertions
        self.assertIsInstance(result, UploadFileOutput)
        self.assertTrue(result.success)
        self.assertEqual(result.remote_path, "remote/test.txt")
        self.assertEqual(result.file_size_bytes, 17)
        mock_bucket.upload.assert_called_once()
        mock_file_open.assert_called_once_with("/local/test.txt", "rb")
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    @patch('os.path.exists')
    def test_upload_file_not_exists(self, mock_exists, mock_load_config, mock_create_client):
        """Test Upload einer nicht existierenden Datei"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_exists.return_value = False
        
        # Test ausführen
        result = upload_file("/nonexistent/test.txt", "remote/test.txt")
        
        # Assertions
        self.assertIsInstance(result, UploadFileOutput)
        self.assertFalse(result.success)
        self.assertIn("Local file does not exist", result.message or "")
    
    @patch('automation_lib.supabase_storage.supabase_storage_runner.create_supabase_client')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.load_supabase_storage_config')
    @patch('automation_lib.supabase_storage.supabase_storage_runner.validate_file_size')
    @patch('os.path.getsize')
    @patch('os.path.exists')
    def test_upload_file_size_exceeded(self, mock_exists, mock_getsize, mock_validate_size, mock_load_config, mock_create_client):
        """Test Upload einer zu großen Datei"""
        # Mock setup
        mock_load_config.return_value = self.mock_config
        mock_exists.return_value = True
        mock_getsize.return_value = 1000000  # 1MB
        mock_validate_size.return_value = False  # Datei zu groß
        
        # Test ausführen
        result = upload_file("/local/large_file.txt", "remote/large_file.txt")
        
        # Assertions
        self.assertIsInstance(result, UploadFileOutput)
        self.assertFalse(result.success)
        self.assertIn("File size exceeds maximum allowed size", result.message or "")

if __name__ == '__main__':
    unittest.main()
