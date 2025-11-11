from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment  # Import AudioSegment

from automation_lib.transcription.config.transcription_config import TranscriptionConfig


def transcribe_with_google_cloud(audio_path: str, config: TranscriptionConfig) -> str:
    """
    Transcribes an audio file using Google Cloud Speech-to-Text.
    Credentials are picked up from GOOGLE_APPLICATION_CREDENTIALS.
    Audio properties (encoding, sample rate) are read dynamically.
    """
    client = speech.SpeechClient()

    # Use explicit config values if provided, otherwise try to infer with pydub or use defaults
    if config.audio_encoding and config.sample_rate_hertz:
        encoding = getattr(speech.RecognitionConfig.AudioEncoding, config.audio_encoding.upper())
        sample_rate_hertz = config.sample_rate_hertz
        print(f"Using explicit audio config: Encoding={config.audio_encoding}, SampleRate={config.sample_rate_hertz}")
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
    if config.enable_speaker_diarization:
        diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=config.min_speaker_count,
            max_speaker_count=config.max_speaker_count,
        )

    config_speech = speech.RecognitionConfig(
        encoding=encoding,
        sample_rate_hertz=sample_rate_hertz,
        language_code=config.language,
        enable_automatic_punctuation=True,
        diarization_config=diarization_config,
    )

    print(f"Starting Google Cloud transcription for: {audio_path}")
    response = client.recognize(config=config_speech, audio=audio)

    if len(response.results) == 0:
        raise ValueError("No transcription results returned from Google Cloud.")

    full_transcript = []
    for result in response.results:
        if result.alternatives:
            alternative = result.alternatives[0]
            if config.enable_speaker_diarization and alternative.words:
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
