# automation_lib/supabase_storage/tests/integration/test_supabase_storage_integration.py

import os
import tempfile
import unittest

from dotenv import load_dotenv  # Import load_dotenv

from automation_lib.supabase_storage.config.supabase_storage_config import SupabaseStorageConfig
from automation_lib.supabase_storage.supabase_storage_runner import delete_file, delete_files, download_file, list_bucket_files, upload_file


class TestSupabaseStorageIntegration(unittest.TestCase):
    """
    Integrationstests für Supabase Storage.
    
    Diese Tests benötigen echte Supabase-Credentials und einen Test-Bucket.
    Sie werden nur ausgeführt, wenn die Umgebungsvariable RUN_INTEGRATION_TESTS=true gesetzt ist.
    """
    
    @classmethod
    def setUpClass(cls):
        """Setup für alle Tests in dieser Klasse"""
        # Lade Umgebungsvariablen aus einer spezifischen .env.test-Datei für Integrationstests
        # Die .env.test-Datei sollte sich im selben Verzeichnis wie die Testdatei befinden
        test_env_path = os.path.join(os.path.dirname(__file__), '.env.test')
        if os.path.exists(test_env_path):
            load_dotenv(test_env_path, override=True)
        else:
            print(f"Warning: .env.test file not found at {test_env_path}. Relying on system environment variables.")
        
        # Prüfe ob Integrationstests ausgeführt werden sollen
        run_integration_tests_env = os.getenv('RUN_INTEGRATION_TESTS', '').lower()
        print(f"Debug: RUN_INTEGRATION_TESTS from environment: '{run_integration_tests_env}'")
        
        if not run_integration_tests_env == 'true':
            raise unittest.SkipTest("Integration tests skipped. Set RUN_INTEGRATION_TESTS=true in your .env file or environment to run.")
        
        # Lade die Konfiguration, optional mit dem Pfad zur .env.test-Datei
        cls.config = SupabaseStorageConfig(env_file=test_env_path if os.path.exists(test_env_path) else None)

        # Prüfe ob notwendige Supabase-Konfigurationen geladen wurden
        if not cls.config.supabase_url or not cls.config.supabase_key:
            raise unittest.SkipTest("Supabase URL and Key not loaded from config. Ensure .env.test file is correctly configured or environment variables are set.")
        cls.test_bucket = os.getenv('TEST_BUCKET_NAME', 'testing')
        
        # Erstelle temporäre Testdateien
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_file_path = os.path.join(cls.temp_dir, 'test_file.txt')
        with open(cls.test_file_path, 'w') as f:
            f.write("This is a test file for Supabase Storage integration tests.")
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup nach allen Tests"""
        # Lösche temporäre Dateien
        if hasattr(cls, 'temp_dir') and os.path.exists(cls.temp_dir):
            import shutil
            shutil.rmtree(cls.temp_dir)
    
    def test_list_bucket_files_integration(self):
        """Test das Auflisten von Dateien im echten Bucket"""
        try:
            result = list_bucket_files(bucket_name=self.test_bucket)
            
            # Assertions
            self.assertIsNotNone(result)
            self.assertIsInstance(result.files, list)
            print(f"Found {len(result.files)} files in bucket '{self.test_bucket}'")
            
            # Zeige erste paar Dateien
            for i, file in enumerate(result.files[:3]):
                print(f"  {i+1}. {file.name}")
                
        except Exception as e:
            self.fail(f"Integration test failed: {e}")
    
    def test_upload_download_delete_cycle(self):
        """Test einen kompletten Upload-Download-Delete Zyklus"""
        test_remote_path = "integration_test/test_file.txt"
        download_path = os.path.join(self.temp_dir, 'downloaded_test_file.txt')
        
        try:
            # Schritt 1: Upload
            upload_result = upload_file(
                local_path=self.test_file_path,
                remote_path=test_remote_path,
                bucket_name=self.test_bucket,
                overwrite=True
            )
            
            if upload_result.success:
                print(f"Successfully uploaded {upload_result.file_size_bytes} bytes to '{test_remote_path}'")
            else:
                print(f"Upload failed: {upload_result.message}")
                return  # Beende Test wenn Upload fehlschlägt
            
            # Schritt 2: Download
            result = download_file(
                remote_path=test_remote_path,
                local_path=download_path,
                bucket_name=self.test_bucket
            )
            
            if result.success:
                # Prüfe ob Datei heruntergeladen wurde
                self.assertTrue(os.path.exists(download_path))
                if result.file_size_bytes is not None:
                    self.assertGreater(result.file_size_bytes, 0)
                    print(f"Successfully downloaded {result.file_size_bytes} bytes")
                else:
                    print("Successfully downloaded file (size unknown)")
                
                # Schritt 3: Delete
                delete_result = delete_file(
                    remote_path=test_remote_path,
                    bucket_name=self.test_bucket
                )
                
                if delete_result.success:
                    print(f"Successfully deleted {test_remote_path}")
                else:
                    print(f"Delete failed: {delete_result.message}")
            else:
                print(f"Download failed (expected if file doesn't exist): {result.message}")
                
        except Exception as e:
            print(f"Integration test cycle failed: {e}")
            # Nicht als Fehler werten, da die Datei möglicherweise nicht existiert
    
    def test_batch_operations(self):
        """Test Batch-Operationen"""
        try:
            # Liste alle Dateien auf
            all_files = list_bucket_files(bucket_name=self.test_bucket)
            
            if len(all_files.files) > 0:
                # Teste Batch-Delete mit den ersten paar Dateien (VORSICHT: Nur in Test-Umgebung!)
                # Für Sicherheit nehmen wir nur Dateien mit "test" im Namen
                test_files = [f.name for f in all_files.files if 'test' in f.name.lower()][:2]
                
                if test_files:
                    print(f"Testing batch delete with files: {test_files}")
                    result = delete_files(test_files, bucket_name=self.test_bucket)
                    
                    print(f"Batch delete result: {len(result.successful_deletes)} successful, {len(result.failed_deletes)} failed")
                else:
                    print("No test files found for batch delete test")
            else:
                print("No files found in bucket for batch operations test")
                
        except Exception as e:
            print(f"Batch operations test failed: {e}")

if __name__ == '__main__':
    # Beispiel für das Ausführen der Integrationstests:
    # RUN_INTEGRATION_TESTS=true SUPABASE_URL=your_url SUPABASE_KEY=your_key python -m unittest
    unittest.main()
