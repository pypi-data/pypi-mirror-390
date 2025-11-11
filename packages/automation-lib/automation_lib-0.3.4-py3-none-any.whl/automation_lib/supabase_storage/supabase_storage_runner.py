# automation_lib/supabase_storage/supabase_storage_runner.py

import os

from prefect import task
from storage3.types import ListBucketFilesOptions

from automation_lib.supabase_storage.config.supabase_storage_config import SupabaseStorageConfig
from automation_lib.supabase_storage.schemas.supabase_storage_schemas import (
    DeleteFileOutput,
    DeleteFilesOutput,
    DownloadFileOutput,
    ListFilesOutput,
    UploadFileOutput,
)
from automation_lib.supabase_storage.supabase_storage_helpers import (
    batch_list,
    convert_supabase_file_to_fileinfo,
    create_supabase_client,
    ensure_directory_exists,
    validate_file_path,
    validate_file_size,
)


@task
def list_bucket_files(
    bucket_name: str | None = None,
    path: str = "",
    limit: int | None = None,
    offset: int | None = None,
    config: SupabaseStorageConfig | None = None
) -> ListFilesOutput:
    """
    Listet Dateien in einem Supabase Storage Bucket auf.
    
    Args:
        bucket_name: Name des Buckets (optional, verwendet default_bucket_name aus config)
        path: Pfad innerhalb des Buckets (optional)
        limit: Maximale Anzahl der zurückgegebenen Dateien (optional, Standard ist 1000)
        offset: Offset für Paginierung (optional)
        config: Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        ListFilesOutput mit Liste der Dateien
    """
    if config is None:
        config = SupabaseStorageConfig()
    
    if bucket_name is None:
        bucket_name = config.default_bucket_name
    
    print(f"Listing files in bucket '{bucket_name}' at path '{path}'")
    
    try:
        client = create_supabase_client(config)
        bucket = client.storage.from_(bucket_name)
        
        # Validiere und normalisiere den Pfad
        normalized_path = validate_file_path(path) if path else ""
        
        # Liste Dateien auf
        options: ListBucketFilesOptions = {}
        if limit is not None:
            options['limit'] = limit
        else:
            options['limit'] = config.default_list_limit # Verwende das konfigurierte Standard-Limit
        if offset is not None:
            options['offset'] = offset
        
        response = bucket.list(path=normalized_path, options=options)
        
        # Konvertiere zu unserem Schema
        files = [convert_supabase_file_to_fileinfo(file_data) for file_data in response]
        
        print(f"Found {len(files)} files")
        return ListFilesOutput(files=files, total_count=len(files))
        
    except Exception as e:
        print(f"Error listing files: {e}")
        raise

@task
def download_file(
    remote_path: str,
    local_path: str,
    bucket_name: str | None = None,
    config: SupabaseStorageConfig | None = None
) -> DownloadFileOutput:
    """
    Lädt eine Datei aus einem Supabase Storage Bucket herunter.
    
    Args:
        remote_path: Pfad zur Datei im Bucket
        local_path: Lokaler Pfad zum Speichern der Datei
        bucket_name: Name des Buckets (optional, verwendet default_bucket_name aus config)
        config: Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        DownloadFileOutput mit Erfolgsstatus und Details
    """
    if config is None:
        config = SupabaseStorageConfig()
    
    if bucket_name is None:
        bucket_name = config.default_bucket_name
    
    print(f"Downloading '{remote_path}' from bucket '{bucket_name}' to '{local_path}'")
    
    try:
        client = create_supabase_client(config)
        bucket = client.storage.from_(bucket_name)
        
        # Validiere Pfade
        normalized_remote_path = validate_file_path(remote_path)
        
        # Stelle sicher, dass das lokale Verzeichnis existiert
        ensure_directory_exists(local_path)
        
        # Lade Datei herunter
        response = bucket.download(normalized_remote_path)
        
        # Schreibe Datei lokal
        with open(local_path, "wb") as f:
            f.write(response)
        
        # Ermittle Dateigröße
        file_size = len(response)
        
        print(f"Successfully downloaded {file_size} bytes to '{local_path}'")
        return DownloadFileOutput(
            success=True,
            local_path=local_path,
            file_size_bytes=file_size,
            message=f"File downloaded successfully ({file_size} bytes)"
        )
        
    except Exception as e:
        error_msg = f"Error downloading file: {e}"
        print(error_msg)
        return DownloadFileOutput(
            success=False,
            local_path=local_path,
            file_size_bytes=None,
            message=error_msg
        )

@task
def upload_file(
    local_path: str,
    remote_path: str,
    bucket_name: str | None = None,
    overwrite: bool = False,
    config: SupabaseStorageConfig | None = None
) -> UploadFileOutput:
    """
    Lädt eine lokale Datei in einen Supabase Storage Bucket hoch.
    
    Args:
        local_path: Lokaler Pfad zur hochzuladenden Datei
        remote_path: Zielpfad im Bucket
        bucket_name: Name des Buckets (optional, verwendet default_bucket_name aus config)
        overwrite: Überschreiben falls Datei bereits existiert
        config: Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        UploadFileOutput mit Erfolgsstatus und Details
    """
    if config is None:
        config = SupabaseStorageConfig()
    
    if bucket_name is None:
        bucket_name = config.default_bucket_name
    
    print(f"Uploading '{local_path}' to bucket '{bucket_name}' at '{remote_path}'")
    
    try:
        # Prüfe ob lokale Datei existiert
        if not os.path.exists(local_path):
            error_msg = f"Local file does not exist: {local_path}"
            print(error_msg)
            return UploadFileOutput(
                success=False,
                remote_path=remote_path,
                file_size_bytes=None,
                message=error_msg
            )
        
        # Ermittle Dateigröße
        file_size = os.path.getsize(local_path)
        
        # Validiere Dateigröße
        if not validate_file_size(local_path, config.max_file_size_mb):
            error_msg = f"File size exceeds maximum allowed size of {config.max_file_size_mb} MB"
            print(error_msg)
            return UploadFileOutput(
                success=False,
                remote_path=remote_path,
                file_size_bytes=file_size,
                message=error_msg
            )
        
        client = create_supabase_client(config)
        bucket = client.storage.from_(bucket_name)
        
        # Validiere und normalisiere den Remote-Pfad
        normalized_remote_path = validate_file_path(remote_path)
        
        # Lese Datei
        with open(local_path, "rb") as f:
            file_data = f.read()
        
        # Lade Datei hoch
        if overwrite:
            # Verwende upsert für Überschreiben
            bucket.upload(
                path=normalized_remote_path,
                file=file_data,
                file_options={"upsert": "true"}
            )
        else:
            # Normaler Upload ohne Überschreiben
            bucket.upload(
                path=normalized_remote_path,
                file=file_data
            )
        
        print(f"Successfully uploaded {file_size} bytes to '{remote_path}'")
        return UploadFileOutput(
            success=True,
            remote_path=remote_path,
            file_size_bytes=file_size,
            message=f"File uploaded successfully ({file_size} bytes)"
        )
        
    except Exception as e:
        error_msg = f"Error uploading file: {e}"
        print(error_msg)
        return UploadFileOutput(
            success=False,
            remote_path=remote_path,
            file_size_bytes=None,
            message=error_msg
        )

@task
def delete_file(
    remote_path: str,
    bucket_name: str | None = None,
    config: SupabaseStorageConfig | None = None
) -> DeleteFileOutput:
    """
    Löscht eine Datei aus einem Supabase Storage Bucket.
    
    Args:
        remote_path: Pfad zur zu löschenden Datei im Bucket
        bucket_name: Name des Buckets (optional, verwendet default_bucket_name aus config)
        config: Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        DeleteFileOutput mit Erfolgsstatus
    """
    if config is None:
        config = SupabaseStorageConfig()
    
    if bucket_name is None:
        bucket_name = config.default_bucket_name
    
    print(f"Deleting '{remote_path}' from bucket '{bucket_name}'")
    
    try:
        client = create_supabase_client(config)
        bucket = client.storage.from_(bucket_name)
        
        # Validiere Pfad
        normalized_remote_path = validate_file_path(remote_path)
        
        # Lösche Datei
        bucket.remove([normalized_remote_path])
        
        print(f"Successfully deleted '{remote_path}'")
        return DeleteFileOutput(
            success=True,
            remote_path=remote_path,
            message="File deleted successfully"
        )
        
    except Exception as e:
        error_msg = f"Error deleting file: {e}"
        print(error_msg)
        return DeleteFileOutput(
            success=False,
            remote_path=remote_path,
            message=error_msg
        )

@task
def delete_files(
    remote_paths: list[str],
    bucket_name: str | None = None,
    config: SupabaseStorageConfig | None = None
) -> DeleteFilesOutput:
    """
    Löscht mehrere Dateien aus einem Supabase Storage Bucket.
    
    Args:
        remote_paths: Liste der Pfade zu den zu löschenden Dateien
        bucket_name: Name des Buckets (optional, verwendet default_bucket_name aus config)
        config: Konfiguration (optional, wird automatisch geladen)
    
    Returns:
        DeleteFilesOutput mit Ergebnissen für jede Datei
    """
    if config is None:
        config = SupabaseStorageConfig()
    
    if bucket_name is None:
        bucket_name = config.default_bucket_name
    
    print(f"Deleting {len(remote_paths)} files from bucket '{bucket_name}'")
    
    results = {}
    successful_deletes = []
    failed_deletes = []
    
    try:
        client = create_supabase_client(config)
        bucket = client.storage.from_(bucket_name)
        
        # Teile in Batches auf, falls zu viele Dateien
        batches = batch_list(remote_paths, config.max_batch_delete_size)
        
        for batch in batches:
            try:
                # Validiere alle Pfade im Batch
                normalized_paths = [validate_file_path(path) for path in batch]
                
                # Lösche Batch
                bucket.remove(normalized_paths)
                
                # Markiere alle als erfolgreich (Supabase gibt nicht immer detaillierte Ergebnisse zurück)
                for path in batch:
                    results[path] = True
                    successful_deletes.append(path)
                    
            except Exception as e:
                print(f"Error deleting batch: {e}")
                # Markiere alle im Batch als fehlgeschlagen
                for path in batch:
                    results[path] = False
                    failed_deletes.append(path)
        
        message = f"Deleted {len(successful_deletes)} files successfully, {len(failed_deletes)} failed"
        print(message)
        
        return DeleteFilesOutput(
            results=results,
            successful_deletes=successful_deletes,
            failed_deletes=failed_deletes,
            message=message
        )
        
    except Exception as e:
        error_msg = f"Error in batch delete operation: {e}"
        print(error_msg)
        
        # Markiere alle als fehlgeschlagen
        results = dict.fromkeys(remote_paths, False)
        
        return DeleteFilesOutput(
            results=results,
            successful_deletes=[],
            failed_deletes=remote_paths,
            message=error_msg
        )

if __name__ == "__main__":
    # Beispiel-Nutzung
    print("Supabase Storage Module - Example Usage")
    
    # Beispiel: Dateien auflisten
    try:
        files_result = list_bucket_files()
        print(f"Found {len(files_result.files)} files")
        for file in files_result.files[:5]:  # Zeige nur die ersten 5
            print(f"  - {file.name}")
    except Exception as e:
        print(f"Error listing files: {e}")
        print("Make sure SUPABASE_URL and SUPABASE_KEY environment variables are set")
