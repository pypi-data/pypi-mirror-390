# automation_lib/supabase_storage/schemas/supabase_storage_schemas.py

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# Input Schemas
class ListFilesInput(BaseModel):
    bucket_name: str = Field(..., description="Name des Supabase Storage Buckets")
    path: str = Field("", description="Pfad innerhalb des Buckets (optional)")
    limit: int | None = Field(None, description="Maximale Anzahl der zurückgegebenen Dateien (optional, Standard ist 100)")
    offset: int | None = Field(None, description="Offset für Paginierung (optional)")

class DownloadFileInput(BaseModel):
    bucket_name: str = Field(..., description="Name des Supabase Storage Buckets")
    remote_path: str = Field(..., description="Pfad zur Datei im Bucket")
    local_path: str = Field(..., description="Lokaler Pfad zum Speichern der Datei")

class DeleteFileInput(BaseModel):
    bucket_name: str = Field(..., description="Name des Supabase Storage Buckets")
    remote_path: str = Field(..., description="Pfad zur zu löschenden Datei im Bucket")

class DeleteFilesInput(BaseModel):
    bucket_name: str = Field(..., description="Name des Supabase Storage Buckets")
    remote_paths: list[str] = Field(..., description="Liste der Pfade zu den zu löschenden Dateien")

class UploadFileInput(BaseModel):
    bucket_name: str = Field(..., description="Name des Supabase Storage Buckets")
    local_path: str = Field(..., description="Lokaler Pfad zur hochzuladenden Datei")
    remote_path: str = Field(..., description="Zielpfad im Bucket")
    overwrite: bool = Field(False, description="Überschreiben falls Datei bereits existiert")

# Output Schemas
class FileInfo(BaseModel):
    name: str = Field(..., description="Dateiname")
    id: str | None = Field(None, description="Eindeutige ID der Datei")
    updated_at: datetime | None = Field(None, description="Zeitpunkt der letzten Änderung")
    created_at: datetime | None = Field(None, description="Erstellungszeitpunkt")
    last_accessed_at: datetime | None = Field(None, description="Letzter Zugriffszeitpunkt")
    metadata: dict[str, Any] | None = Field(None, description="Zusätzliche Metadaten")

class ListFilesOutput(BaseModel):
    files: list[FileInfo] = Field(..., description="Liste der Dateien im Bucket")
    total_count: int | None = Field(None, description="Gesamtanzahl der Dateien (falls verfügbar)")

class DownloadFileOutput(BaseModel):
    success: bool = Field(..., description="Erfolgsstatus des Downloads")
    local_path: str = Field(..., description="Lokaler Pfad der heruntergeladenen Datei")
    file_size_bytes: int | None = Field(None, description="Größe der heruntergeladenen Datei in Bytes")
    message: str | None = Field(None, description="Zusätzliche Nachricht oder Fehlerbeschreibung")

class DeleteFileOutput(BaseModel):
    success: bool = Field(..., description="Erfolgsstatus der Löschung")
    remote_path: str = Field(..., description="Pfad der gelöschten Datei")
    message: str | None = Field(None, description="Zusätzliche Nachricht oder Fehlerbeschreibung")

class DeleteFilesOutput(BaseModel):
    results: dict[str, bool] = Field(..., description="Ergebnisse der Löschvorgänge (Pfad -> Erfolgsstatus)")
    successful_deletes: list[str] = Field(..., description="Liste der erfolgreich gelöschten Dateien")
    failed_deletes: list[str] = Field(..., description="Liste der fehlgeschlagenen Löschvorgänge")
    message: str | None = Field(None, description="Zusätzliche Nachricht")

class UploadFileOutput(BaseModel):
    success: bool = Field(..., description="Erfolgsstatus des Uploads")
    remote_path: str = Field(..., description="Pfad der hochgeladenen Datei im Bucket")
    file_size_bytes: int | None = Field(None, description="Größe der hochgeladenen Datei in Bytes")
    message: str | None = Field(None, description="Zusätzliche Nachricht oder Fehlerbeschreibung")

# Configuration Schema (separate from main config)
class SupabaseStorageConfig(BaseModel):
    supabase_url: str = Field(..., description="Supabase Projekt URL")
    supabase_key: str = Field(..., description="Supabase Service Role Key")
    default_bucket_name: str = Field("files", description="Standard Bucket Name")
    download_timeout_seconds: int = Field(300, description="Timeout für Downloads in Sekunden")
    max_file_size_mb: int = Field(100, description="Maximale Dateigröße für Downloads in MB")
    max_batch_delete_size: int = Field(100, description="Maximale Anzahl Dateien für Batch-Löschung")
