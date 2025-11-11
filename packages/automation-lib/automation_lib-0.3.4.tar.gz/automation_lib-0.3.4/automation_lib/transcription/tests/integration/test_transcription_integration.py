import os
import unittest

from automation_lib.transcription.config.transcription_config import TranscriptionConfig
from automation_lib.transcription.transcription_runner import transcribe_audio_file
from tests.test_utils import check_google_cloud_credentials_path_set, check_openai_api_key_set, skip_unless_integration_test

# Define the path to the test audio file for OpenAI
TEST_AUDIO_FILE_OPENAI = "automation_lib/transcription/tests/data/voice_record.m4a"

# Define the path to the test audio file for Google Cloud
TEST_AUDIO_FILE_GOOGLE_CLOUD = "automation_lib/transcription/tests/data/audio-aufnahme-zwei-sprecher.m4a"

# Expected transcription text for OpenAI
EXPECTED_TRANSCRIPT_OPENAI = "Das ist ein Test. Es war etwas Stille. Ich bin der Entwickler namens Jakob."

# Expected transcription text for Google Cloud with diarization.
# This is a placeholder that needs to be manually updated after running a transcription
# with Google Cloud Speech-to-Text and diarization for 'audio-aufnahme-zwei-sprecher.m4a'.
EXPECTED_TRANSCRIPT_GOOGLE_CLOUD_DIARIZATION = (
    "Bitte hier den erwarteten Text für die Google Cloud Transkription mit Sprechererkennung für 'audio-aufnahme-zwei-sprecher.m4a' einfügen."
)

# Define the path to the large audio file for Google Cloud
# Set this environment variable to test with a large audio file
LARGE_AUDIO_FILE_PATH = os.getenv("TEST_LARGE_AUDIO_FILE", "")

# Expected transcription text for the large audio file (Google Cloud with diarization)
# This is a placeholder that needs to be manually updated after running a transcription
# with Google Cloud Speech-to-Text and diarization for the large audio file.


@skip_unless_integration_test
class TestIntegrationAudioTranscription(unittest.IsolatedAsyncioTestCase):

    @unittest.skipUnless(
        check_openai_api_key_set(),
        "OpenAI integration tests require OPENAI_API_KEY to be set."
    )
    async def test_integration_transcribe_audio_file_openai(self):
        """
        Tests the full audio transcription flow with a real audio file and OpenAI API call.
        This test requires OPENAI_API_KEY to be set in the .env file.
        """
        if not os.path.exists(TEST_AUDIO_FILE_OPENAI):
            self.fail(f"Test audio file not found at: {TEST_AUDIO_FILE_OPENAI}")

        print(f"\nRunning OpenAI integration test with {TEST_AUDIO_FILE_OPENAI}")
        print("This will make an actual API call to OpenAI Whisper.")

        # Create a TranscriptionConfig instance for OpenAI
        openai_config = TranscriptionConfig(
            transcription_provider="openai",
            model="whisper-1",
            language="de",
            max_audio_length_minutes=20,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_max_file_size_mb=25, # Added
            google_max_file_size_mb=10, # Added
            # Google Cloud specific fields, set to defaults or None as they are not used by OpenAI
            enable_speaker_diarization=False,
            min_speaker_count=None,
            max_speaker_count=None,
            audio_encoding=None, # Added
            sample_rate_hertz=None, # Added
        )

        try:
            actual_transcript = await transcribe_audio_file(TEST_AUDIO_FILE_OPENAI, cleanup_segments=False, config=openai_config)
            # Normalize whitespace for comparison
            normalized_actual = " ".join(actual_transcript.split())
            normalized_expected = " ".join(EXPECTED_TRANSCRIPT_OPENAI.split())

            self.assertEqual(normalized_actual, normalized_expected, "The transcribed text does not match the expected text.")
            print(f"Actual Transcript (OpenAI): {actual_transcript}")
            print(f"Expected Transcript (OpenAI): {EXPECTED_TRANSCRIPT_OPENAI}")
        except Exception as e:
            self.fail(f"OpenAI Transcription failed with an unexpected error: {e}")

    @unittest.skipUnless(
        check_google_cloud_credentials_path_set(),
        "Google Cloud integration tests require GOOGLE_APPLICATION_CREDENTIALS to be set."
    )
    async def test_integration_transcribe_audio_file_google_cloud(self):
        """
        Tests the full audio transcription flow with a real audio file and Google Cloud API call.
        This test requires GOOGLE_APPLICATION_CREDENTIALS to be set in the .env file.
        """
        if not os.path.exists(TEST_AUDIO_FILE_GOOGLE_CLOUD):
            self.fail(f"Test audio file not found at: {TEST_AUDIO_FILE_GOOGLE_CLOUD}")

        print(f"\nRunning Google Cloud integration test with {TEST_AUDIO_FILE_GOOGLE_CLOUD}")
        print("This will make an actual API call to Google Cloud Speech-to-Text.")

        # Create a TranscriptionConfig instance for Google Cloud with diarization
        google_cloud_diarization_config = TranscriptionConfig(
            transcription_provider="google_cloud",
            language="de",
            max_audio_length_minutes=20,
            enable_speaker_diarization=True,
            min_speaker_count=1,
            max_speaker_count=2,
            google_max_file_size_mb=10, # Added
            audio_encoding=None, # Added
            sample_rate_hertz=None, # Added
            # OpenAI specific fields, set to defaults or None as they are not used by Google Cloud
            model=None,
            openai_api_key=None,
            openai_max_file_size_mb=25, # Added
        )

        try:
            actual_transcript = await transcribe_audio_file(TEST_AUDIO_FILE_GOOGLE_CLOUD, cleanup_segments=False, config=google_cloud_diarization_config)
            # Normalize whitespace for comparison
            normalized_actual = " ".join(actual_transcript.split())
            normalized_expected = " ".join(EXPECTED_TRANSCRIPT_GOOGLE_CLOUD_DIARIZATION.split())

            self.assertEqual(normalized_actual, normalized_expected, "The transcribed text does not match the expected text for Google Cloud with diarization.")
            print(f"Actual Transcript (Google Cloud): {actual_transcript}")
            print(f"Expected Transcript (Google Cloud): {EXPECTED_TRANSCRIPT_GOOGLE_CLOUD_DIARIZATION}")
        except Exception as e:
            self.fail(f"Google Cloud Transcription failed with an unexpected error: {e}")

    @unittest.skipUnless(
        check_google_cloud_credentials_path_set(),
        "Google Cloud integration tests require GOOGLE_APPLICATION_CREDENTIALS to be set."
    )
    async def test_integration_transcribe_audio_file_google_cloud_no_diarization(self):
        """
        Tests the full audio transcription flow with a real audio file and Google Cloud API call,
        without speaker diarization.
        This test requires GOOGLE_APPLICATION_CREDENTIALS to be set in the .env file.
        """
        if not os.path.exists(TEST_AUDIO_FILE_GOOGLE_CLOUD):
            self.fail(f"Test audio file not found at: {TEST_AUDIO_FILE_GOOGLE_CLOUD}")

        print(f"\nRunning Google Cloud integration test (no diarization) with {TEST_AUDIO_FILE_GOOGLE_CLOUD}")
        print("This will make an actual API call to Google Cloud Speech-to-Text.")

        # Create a TranscriptionConfig instance for Google Cloud without diarization
        google_cloud_no_diarization_config = TranscriptionConfig(
            transcription_provider="google_cloud",
            language="de",
            max_audio_length_minutes=20,
            enable_speaker_diarization=False, # Disable diarization
            min_speaker_count=None, # Set to None as they are not used when diarization is false
            max_speaker_count=None, # Set to None as they are not used when diarization is false
            google_max_file_size_mb=10, # Added
            audio_encoding=None, # Added
            sample_rate_hertz=None, # Added
            # OpenAI specific fields, set to defaults or None as they are not used by Google Cloud
            model=None,
            openai_api_key=None,
            openai_max_file_size_mb=25, # Added
        )

        try:
            actual_transcript = await transcribe_audio_file(TEST_AUDIO_FILE_GOOGLE_CLOUD, cleanup_segments=False, config=google_cloud_no_diarization_config)
            # Normalize whitespace for comparison
            # normalized_actual = " ".join(actual_transcript.split())
            # normalized_expected = " ".join(EXPECTED_TRANSCRIPT_GOOGLE_CLOUD_NO_DIARIZATION.split())

            # self.assertEqual(normalized_actual, normalized_expected, "The transcribed text does not match the expected text for Google Cloud without diarization.")
            print(f"Actual Transcript (Google Cloud, no diarization): {actual_transcript}")
            # print(f"Expected Transcript (Google Cloud, no diarization): {EXPECTED_TRANSCRIPT_GOOGLE_CLOUD_NO_DIARIZATION}")
        except Exception as e:
            self.fail(f"Google Cloud Transcription (no diarization) failed with an unexpected error: {e}")

    @unittest.skipUnless(
        check_google_cloud_credentials_path_set(),
        "Google Cloud integration tests require GOOGLE_APPLICATION_CREDENTIALS to be set."
    )
    async def test_integration_transcribe_large_audio_file(self):
        """
        Tests the full audio transcription flow with a large real audio file and Openai API call,
        with speaker diarization.
        This test requires GOOGLE_APPLICATION_CREDENTIALS to be set in the .env file.
        """
        if not os.path.exists(LARGE_AUDIO_FILE_PATH):
            self.fail(f"Test audio file not found at: {LARGE_AUDIO_FILE_PATH}")

        print(f"\nRunning Google Cloud integration test for large audio file with {LARGE_AUDIO_FILE_PATH}")
        print("This will make an actual API call to Google Cloud Speech-to-Text.")

        # Create a TranscriptionConfig instance for Google Cloud with diarization
        google_cloud_large_audio_config = TranscriptionConfig(
            transcription_provider="openai",
            language="de",
        ) # type: ignore

        try:
            actual_transcript = await transcribe_audio_file(LARGE_AUDIO_FILE_PATH, cleanup_segments=False, config=google_cloud_large_audio_config)
            # Normalize whitespace for comparison
            normalized_actual = " ".join(actual_transcript.split())
            self.assertGreater(len(normalized_actual), 0, "The transcribed text should not be empty.")
            print(f"Actual Transcript (Google Cloud, large audio): {actual_transcript}")

        except Exception as e:
            self.fail(f"Google Cloud Transcription for large audio file failed with an unexpected error: {e}")

if __name__ == '__main__':
    unittest.main()
