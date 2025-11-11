#!/usr/bin/env python3
# automation_lib/supabase_storage/examples/minimal_usage.py

"""
Minimal Usage Example für das Supabase Storage Modul

Dieses Beispiel zeigt die grundlegende Verwendung des Supabase Storage Moduls
für das Auflisten, Herunterladen und Löschen von Dateien.

Voraussetzungen:
- SUPABASE_URL und SUPABASE_KEY Umgebungsvariablen müssen gesetzt sein
- Ein Supabase-Projekt mit Storage-Bucket muss existieren
"""

import os
import sys
import tempfile

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from automation_lib.supabase_storage.supabase_storage_runner import download_file, list_bucket_files


def main():
    """
    Hauptfunktion mit Beispielen für alle Supabase Storage Operationen.
    """
    print("🚀 Supabase Storage Module - Minimal Usage Example")
    print("=" * 50)
    
    # Prüfe Umgebungsvariablen
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables are required.")
        print("   Please set them before running this example:")
        print("   export SUPABASE_URL='https://your-project.supabase.co'")
        print("   export SUPABASE_KEY='your-service-role-key'")
        return 1
    
    try:
        # 1. Dateien im Bucket auflisten
        print("\n📂 1. Listing files in bucket...")
        files_result = list_bucket_files()
        
        print(f"   Found {len(files_result.files)} files:")
        for i, file in enumerate(files_result.files[:5]):  # Zeige nur die ersten 5
            date_str = file.updated_at.strftime('%Y-%m-%d %H:%M') if file.updated_at else 'Unknown'
            print(f"   {i+1}. {file.name} (Updated: {date_str})")
        
        if len(files_result.files) > 5:
            print(f"   ... and {len(files_result.files) - 5} more files")
        
        # 2. Dateien in einem spezifischen Pfad auflisten
        print("\n📁 2. Listing files in specific path...")
        try:
            path_files = list_bucket_files(path="documents/")
            print(f"   Found {len(path_files.files)} files in 'documents/' path")
        except Exception as e:
            print(f"   No files found in 'documents/' path or path doesn't exist: {e}")
        
        # 3. Datei herunterladen (falls vorhanden)
        if files_result.files:
            print("\n⬇️  3. Downloading a file...")
            first_file = files_result.files[0]
            
            # Erstelle temporären Pfad für Download
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{first_file.name}") as tmp_file:
                temp_path = tmp_file.name
            
            try:
                download_result = download_file(
                    remote_path=first_file.name,
                    local_path=temp_path
                )
                
                if download_result.success:
                    print(f"   ✅ Downloaded '{first_file.name}' ({download_result.file_size_bytes} bytes)")
                    print(f"   📁 Saved to: {temp_path}")
                    
                    # Cleanup: Lösche temporäre Datei
                    os.unlink(temp_path)
                    print("   🗑️  Cleaned up temporary file")
                else:
                    print(f"   ❌ Download failed: {download_result.message}")
            except Exception as e:
                print(f"   ❌ Download error: {e}")
        else:
            print("\n⬇️  3. No files available for download example")
        
        # 4. Beispiel für Batch-Operationen
        print("\n📊 4. Batch operations example...")
        
        # Filtere Dateien mit "test" im Namen (sicherer für Demo)
        test_files = [f.name for f in files_result.files if 'test' in f.name.lower()]
        
        if test_files:
            print(f"   Found {len(test_files)} test files:")
            for file in test_files[:3]:  # Zeige nur die ersten 3
                print(f"   - {file}")
            
            # WARNUNG: Batch-Delete ist destruktiv!
            print("   ⚠️  Batch delete example skipped for safety")
            print("   ⚠️  To test batch delete, uncomment the code below and use test files only!")
            
            # Uncomment the following lines to test batch delete (USE WITH CAUTION!)
            # batch_result = delete_files(test_files[:2])  # Delete only first 2 test files
            # print(f"   Batch delete: {len(batch_result.successful_deletes)} successful, {len(batch_result.failed_deletes)} failed")
        else:
            print("   No test files found for batch operations example")
        
        
    except Exception as e:
        print(f"\n❌ Error during example execution: {e}")
        print("   Make sure your Supabase credentials are correct and the bucket exists.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
