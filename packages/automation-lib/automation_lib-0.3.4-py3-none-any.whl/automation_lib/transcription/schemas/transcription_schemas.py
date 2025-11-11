# automation_lib/transcription/schemas/transcription_schemas.py

from pydantic import BaseModel


# Example Pydantic models for input/output validation
class AudioTranscriptionInput(BaseModel):
    audio_path: str
    model: str = "whisper-1"
    language: str = "de"

class AudioTranscriptionOutput(BaseModel):
    text: str
    duration: float
