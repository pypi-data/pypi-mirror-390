"""
Google Cloud Transcription Provider

Implementation of BaseTranscriptionProvider for Google Cloud Speech-to-Text.
"""

import os

from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment

from automation_lib.transcription.config.transcription_config import TranscriptionConfig

from .base_provider import BaseTranscriptionProvider


class GoogleCloudTranscriptionProvider(BaseTranscriptionProvider):
    """
    Provider for Google Cloud Speech-to-Text transcription.
    """
    
    def __init__(self, config: TranscriptionConfig):
        """Initialize Google Cloud transcription provider with configuration."""
        super().__init__(config)
        self.client = speech.SpeechClient()
    
    def validate_config(self) -> bool:
        """
        Validate Google Cloud configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If required configuration is missing
        """
        # Google Cloud relies on GOOGLE_APPLICATION_CREDENTIALS environment variable
        # or default credentials, so we don't need to validate specific API keys here
        return True
    
    async def transcribe_audio_segment(self, segment_path: str) -> str:
        """
        Transcribe a single audio segment using Google Cloud Speech-to-Text.
        
        Args:
            segment_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
            
        Raises:
            Exception: If transcription fails
        """
        # Store original environment variables
        original_openai_key = os.getenv("OPENAI_API_KEY")
        
        try:
            # Temporarily unset OpenAI key to prevent conflicts
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            
            return self._transcribe_with_google_cloud(segment_path)
            
        except Exception as e:
            print(f"Error transcribing segment {segment_path} with Google Cloud: {e}")
            raise
        finally:
            # Restore original environment variables
            if original_openai_key is not None:
                os.environ["OPENAI_API_KEY"] = original_openai_key
            elif "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
    
    def _transcribe_with_google_cloud(self, audio_path: str) -> str:
        """
        Internal method to transcribe an audio file using Google Cloud Speech-to-Text.
        This is adapted from the existing google_cloud_transcriber.py implementation.
        """
        # Use explicit config values if provided, otherwise try to infer with pydub or use defaults
        if self.config.audio_encoding and self.config.sample_rate_hertz:
            encoding = getattr(speech.RecognitionConfig.AudioEncoding, self.config.audio_encoding.upper())
            sample_rate_hertz = self.config.sample_rate_hertz
            print(f"Using explicit audio config: Encoding={self.config.audio_encoding}, SampleRate={self.config.sample_rate_hertz}")
        else:
            try:
                audio_segment = AudioSegment.from_file(audio_path)
                sample_rate_hertz = audio_segment.frame_rate
                # Attempt to infer encoding based on file extension or use a common default
                # Google Cloud can often infer encoding for common formats (FLAC, MP3, WAV)
                # For raw audio, LINEAR16 is common.
                # We'll set a default and let Google infer if possible, or use LINEAR16 if pydub gives no specific hint.
                # Note: Google Cloud Speech-to-Text generally prefers FLAC or LINEAR16.
                # If the file is not WAV, it's often better to let Google infer or convert.
                # For simplicity, we'll stick to LINEAR16 as a fallback if no explicit config.
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
                print(f"Inferred audio config: Encoding=LINEAR16 (default), SampleRate={sample_rate_hertz}")
            except Exception as e:
                print(f"Warning: Could not read audio file properties with pydub: {e}. Using default values.")
                sample_rate_hertz = 16000
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
                print("Using default audio config: Encoding=LINEAR16, SampleRate=16000")

        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)

        diarization_config = None
        if self.config.enable_speaker_diarization:
            diarization_config = speech.SpeakerDiarizationConfig(
                enable_speaker_diarization=True,
                min_speaker_count=self.config.min_speaker_count,
                max_speaker_count=self.config.max_speaker_count,
            )

        config_speech = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=sample_rate_hertz,
            language_code=self.config.language,
            enable_automatic_punctuation=True,
            diarization_config=diarization_config,
        )

        print(f"Starting Google Cloud transcription for: {audio_path}")
        response = self.client.recognize(config=config_speech, audio=audio)

        if len(response.results) == 0:
            raise ValueError("No transcription results returned from Google Cloud.")

        full_transcript = []
        for result in response.results:
            if result.alternatives:
                alternative = result.alternatives[0]
                if self.config.enable_speaker_diarization and alternative.words:
                    # Reconstruct transcript with speaker tags
                    speaker_transcript = []
                    current_speaker = None
                    for word_info in alternative.words:
                        if word_info.speaker_tag != current_speaker:
                            if current_speaker is not None:
                                speaker_transcript.append(f" (Speaker {current_speaker}):")
                            current_speaker = word_info.speaker_tag
                            speaker_transcript.append(f"\nSpeaker {current_speaker}: {word_info.word}")
                        else:
                            speaker_transcript.append(f" {word_info.word}")
                    if current_speaker is not None:
                        speaker_transcript.append(f" (Speaker {current_speaker}).")
                    full_transcript.append("".join(speaker_transcript))
                else:
                    full_transcript.append(alternative.transcript)
        
        print("Google Cloud Transcription complete.")
        return " ".join(full_transcript)
    
    def get_max_file_size_mb(self) -> int | None:
        """
        Get the maximum file size supported by Google Cloud Speech-to-Text.
        
        Returns:
            Maximum file size in MB
        """
        return self.config.google_max_file_size_mb or 10
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name string
        """
        return "google_cloud"
    
    def supports_language(self, language: str) -> bool:
        """
        Check if Google Cloud Speech-to-Text supports the given language.
        
        Args:
            language: Language code (e.g., 'de', 'en')
            
        Returns:
            True if language is supported (Google Cloud supports many languages)
        """
        # Google Cloud Speech-to-Text supports a wide range of languages
        # For simplicity, we return True here, but this could be enhanced
        # with a specific list of supported language codes
        return True
    
    def supports_speaker_diarization(self) -> bool:
        """
        Check if Google Cloud Speech-to-Text supports speaker diarization.
        
        Returns:
            True (Google Cloud supports speaker diarization)
        """
        return True
