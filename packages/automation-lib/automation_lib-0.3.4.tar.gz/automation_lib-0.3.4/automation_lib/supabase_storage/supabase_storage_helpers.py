# automation_lib/supabase_storage/supabase_storage_helpers.py

import os
from datetime import datetime
from typing import Any

from supabase import Client, create_client

from automation_lib.supabase_storage.config.supabase_storage_config import SupabaseStorageConfig
from automation_lib.supabase_storage.schemas.supabase_storage_schemas import FileInfo


def create_supabase_client(config: SupabaseStorageConfig) -> Client:
    """
    Erstellt einen Supabase Client basierend auf der Konfiguration.
    """
    if not config.supabase_url:
        raise ValueError("SUPABASE_URL ist nicht konfiguriert. Bitte setzen Sie die Umgebungsvariable.")
    
    if not config.supabase_key:
        raise ValueError("SUPABASE_KEY ist nicht konfiguriert. Bitte setzen Sie die Umgebungsvariable.")
    
    return create_client(config.supabase_url, config.supabase_key)

def validate_file_path(file_path: str) -> str:
    """
    Validiert und normalisiert einen Dateipfad für Supabase Storage.
    Verhindert Directory Traversal Angriffe.
    """
    # Entferne führende Slashes und normalisiere den Pfad
    normalized_path = os.path.normpath(file_path.lstrip('/'))
    
    # Prüfe auf Directory Traversal Versuche
    if '..' in normalized_path or normalized_path.startswith('/'):
        raise ValueError(f"Ungültiger Dateipfad: {file_path}")
    
    return normalized_path

def convert_supabase_file_to_fileinfo(file_data: dict[str, Any]) -> FileInfo:
    """
    Konvertiert Supabase Datei-Daten zu unserem FileInfo Schema.
    """
    # Supabase gibt verschiedene Felder zurück, wir mappen sie auf unser Schema
    return FileInfo(
        name=file_data.get('name', ''),
        id=file_data.get('id'),
        updated_at=parse_datetime_string(file_data.get('updated_at')),
        created_at=parse_datetime_string(file_data.get('created_at')),
        last_accessed_at=parse_datetime_string(file_data.get('last_accessed_at')),
        metadata=file_data.get('metadata', {})
    )

def parse_datetime_string(datetime_str: str | None) -> datetime | None:
    """
    Parst einen Datetime-String von Supabase zu einem Python datetime Objekt.
    """
    if not datetime_str:
        return None
    
    try:
        # Supabase verwendet ISO 8601 Format
        return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return None

def validate_file_size(file_path: str, max_size_mb: int) -> bool:
    """
    Prüft ob eine Datei die maximale Größe nicht überschreitet.
    """
    if not os.path.exists(file_path):
        return True  # Datei existiert nicht, Größenprüfung nicht relevant
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return file_size_mb <= max_size_mb

def ensure_directory_exists(file_path: str) -> None:
    """
    Stellt sicher, dass das Verzeichnis für einen Dateipfad existiert.
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def batch_list(items: list[Any], batch_size: int) -> list[list[Any]]:
    """
    Teilt eine Liste in Batches der angegebenen Größe auf.
    """
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
