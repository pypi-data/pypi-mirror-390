import unittest
from unittest.mock import MagicMock, patch

from automation_lib.transcription.config.transcription_config import TranscriptionConfig
from automation_lib.transcription.transcription_helpers import get_audio_duration, split_audio_file


class TestAudioTranscription(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Mock os.remove for cleanup
        self.patcher_os_remove = patch('os.remove')
        self.mock_os_remove = self.patcher_os_remove.start()

        # Mock builtins.open to prevent FileNotFoundError
        self.patcher_open = patch('builtins.open', MagicMock())
        self.mock_open = self.patcher_open.start()

        # Patch pydub.AudioSegment.from_file directly
        self.patcher_from_file = patch('pydub.AudioSegment.from_file')
        self.mock_from_file_func = self.patcher_from_file.start()

        # Create a mock for the AudioSegment object that from_file would return
        self.mock_audio_segment_instance = MagicMock()
        self.mock_from_file_func.return_value = self.mock_audio_segment_instance

        # Configure the mock_audio_segment_instance
        self.mock_audio_segment_instance.len = 0 # Default length, will be set per test
        self.mock_audio_segment_instance.__len__.return_value = 0 # Default __len__, will be set per test

        # Configure the mock for AudioSegment.export
        self.mock_export = MagicMock()
        self.mock_audio_segment_instance.export = self.mock_export

        # Configure __getitem__ to return a new mock with the patched export
        def getitem_side_effect(*args, **kwargs):
            sliced_mock = MagicMock()
            sliced_mock.export = self.mock_export # Assign the same mock_export
            sliced_mock.len = 1000 * 60 * 10 # Default length for sliced segments
            sliced_mock.__len__.return_value = sliced_mock.len
            return sliced_mock
        self.mock_audio_segment_instance.__getitem__.side_effect = getitem_side_effect


    def tearDown(self):
        self.patcher_os_remove.stop()
        self.patcher_open.stop()
        self.patcher_from_file.stop()

    # Test for get_audio_duration
    def test_get_audio_duration(self):
        self.mock_audio_segment_instance.len = 1000 * 60 * 30 # 30 minutes
        self.mock_audio_segment_instance.__len__.return_value = self.mock_audio_segment_instance.len
        duration = get_audio_duration("dummy.mp3")
        self.assertEqual(duration, 30.0)

    # Test for split_audio_file
    def test_split_audio_file_no_split(self):
        self.mock_audio_segment_instance.len = 1000 * 60 * 10 # 10 minutes
        self.mock_audio_segment_instance.__len__.return_value = self.mock_audio_segment_instance.len
        # Mock os.path.getsize for the file size calculation in split_audio_file
        with patch('os.path.getsize', return_value=10 * 1024 * 1024): # 10 MB
            audio_path = "test_audio_short.mp3"
            # Create a mock config with OpenAI provider and 25MB max file size
            config = TranscriptionConfig(
                transcription_provider="openai",
                openai_max_file_size_mb=25,
                model="whisper-1",
                openai_api_key="test-key",
                language="en",
                max_audio_length_minutes=20,
                google_max_file_size_mb=10,
                enable_speaker_diarization=False,
                min_speaker_count=2,
                max_speaker_count=6,
                audio_encoding=None,
                sample_rate_hertz=None
            )
            with patch('automation_lib.transcription.providers.provider_factory.TranscriptionProviderFactory.create_provider') as mock_factory:
                mock_provider = MagicMock()
                mock_provider.get_max_file_size_mb.return_value = 25
                mock_factory.return_value = mock_provider
                
                segments = split_audio_file(audio_path, config)
                self.assertEqual(len(segments), 1)
                self.assertEqual(segments[0], audio_path)
                self.assertEqual(self.mock_export.call_count, 0) # No export should happen

    def test_split_audio_file_with_split(self):
        self.mock_audio_segment_instance.len = 1000 * 60 * 30 # 30 minutes
        self.mock_audio_segment_instance.__len__.return_value = self.mock_audio_segment_instance.len
        # Mock os.path.getsize for the file size calculation in split_audio_file
        with patch('os.path.getsize', return_value=30 * 1024 * 1024): # 30 MB
            audio_path = "test_audio_long.mp3"
            # Create a mock config with OpenAI provider and 10MB max file size
            config = TranscriptionConfig(
                transcription_provider="openai",
                openai_max_file_size_mb=10,
                model="whisper-1",
                openai_api_key="test-key",
                language="en",
                max_audio_length_minutes=20,
                google_max_file_size_mb=10,
                enable_speaker_diarization=False,
                min_speaker_count=2,
                max_speaker_count=6,
                audio_encoding=None,
                sample_rate_hertz=None
            )
            with patch('automation_lib.transcription.providers.provider_factory.TranscriptionProviderFactory.create_provider') as mock_factory:
                mock_provider = MagicMock()
                mock_provider.get_max_file_size_mb.return_value = 10
                mock_factory.return_value = mock_provider
                
                segments = split_audio_file(audio_path, config)
                self.assertEqual(len(segments), 3) # 30 minutes / (calculated max duration for 10MB) = 30/10 = 3 segments
                self.assertEqual(segments[0], "test_audio_long_part1.mp3")
                self.assertEqual(segments[1], "test_audio_long_part2.mp3")
                self.assertEqual(segments[2], "test_audio_long_part3.mp3")
                # Verify export was called for each segment
                self.assertEqual(self.mock_export.call_count, 3)
    # TODO: Tests are freezing, need to investigate
    
    # # Test for transcribe_audio_segment
    # @patch('litellm.transcription')
    # async def test_transcribe_audio_segment_success(self, mock_litellm_transcription):
    #     mock_litellm_transcription.return_value = {"text": "This is a test transcript."}
    #     segment_path = "dummy_segment.mp3"
    #     with patch('builtins.open', MagicMock()):
    #         transcript = await transcribe_audio_segment(segment_path)
    #         self.assertEqual(transcript, "This is a test transcript.")
    #         mock_litellm_transcription.assert_called_once_with(
    #             model="whisper-1",
    #             audio=unittest.mock.ANY, # We can't easily mock the file object itself, so use ANY
    #             api_key=os.getenv("OPENAI_API_KEY")
    #         )

    # @patch('litellm.transcription')
    # async def test_transcribe_audio_segment_failure(self, mock_litellm_transcription):
    #     mock_litellm_transcription.side_effect = Exception("API Error")
    #     segment_path = "dummy_segment.mp3"
    #     with patch('builtins.open', MagicMock()): # This patch is local to this test
    #         with self.assertRaisesRegex(Exception, "API Error"):
    #             await transcribe_audio_segment(segment_path)

    # # Test for transcribe_audio_flow
    # @patch('automation_lib.transcription.transcription_helpers.split_audio_file')
    # @patch('automation_lib.transcription.transcription_helpers.transcribe_audio_segment')
    # async def test_transcribe_audio_file_success(self, mock_transcribe_audio_segment, mock_split_audio_file):
    #     mock_split_audio_file.return_value = ["part1.mp3", "part2.mp3"]
    #     mock_transcribe_audio_segment.side_effect = [
    #         "Transcript for part 1.",
    #         "Transcript for part 2."
    #     ]

    #     audio_path = "full_audio.mp3"
    #     full_transcript = await transcribe_audio_file(audio_path)

    #     self.assertEqual(full_transcript, "Transcript for part 1. Transcript for part 2.")
    #     mock_split_audio_file.assert_called_once_with(audio_path)
    #     self.assertEqual(mock_transcribe_audio_segment.call_count, 2)
    #     self.assertEqual(self.mock_os_remove.call_count, 2) # Ensure segment files are removed

    # @patch('automation_lib.transcription.transcription_helpers.split_audio_file')
    # @patch('automation_lib.transcription.transcription_helpers.transcribe_audio_segment')
    # async def test_transcribe_audio_file_segment_failure(self, mock_transcribe_audio_segment, mock_split_audio_file):
    #     mock_split_audio_file.return_value = ["part1.mp3", "part2.mp3"]
    #     mock_transcribe_audio_segment.side_effect = [
    #         "Transcript for part 1.",
    #         Exception("Segment API Error")
    #     ]

    #     audio_path = "full_audio.mp3"
    #     with self.assertRaisesRegex(Exception, "Segment API Error"):
    #         await transcribe_audio_file(audio_path)

    #     mock_split_audio_file.assert_called_once_with(audio_path)
    #     self.assertEqual(mock_transcribe_audio_segment.call_count, 2)
    #     # os.remove should be called for the first segment that was successfully transcribed
    #     self.assertEqual(self.mock_os_remove.call_count, 1)

if __name__ == '__main__':
    unittest.main()
