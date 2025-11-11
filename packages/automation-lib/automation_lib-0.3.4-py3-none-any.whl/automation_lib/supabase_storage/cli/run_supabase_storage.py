#!/usr/bin/env python3
# automation_lib/supabase_storage/cli/run_supabase_storage.py

import argparse
import os
import sys

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from automation_lib.supabase_storage.supabase_storage_runner import delete_file, delete_files, download_file, list_bucket_files


def main():
    """
    CLI-Interface für Supabase Storage Operationen.
    """
    parser = argparse.ArgumentParser(
        description="Supabase Storage CLI - Manage files in Supabase Storage buckets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List files in default bucket
  python run_supabase_storage.py list

  # List files in specific bucket
  python run_supabase_storage.py list --bucket my-bucket

  # List files in specific path
  python run_supabase_storage.py list --path "documents/"

  # Download a file
  python run_supabase_storage.py download remote/file.txt local/file.txt

  # Download from specific bucket
  python run_supabase_storage.py download remote/file.txt local/file.txt --bucket my-bucket

  # Delete a file
  python run_supabase_storage.py delete remote/file.txt

  # Delete multiple files
  python run_supabase_storage.py delete-batch file1.txt file2.txt file3.txt

Environment Variables:
  SUPABASE_URL              - Your Supabase project URL
  SUPABASE_KEY              - Your Supabase service role key
  SUPABASE_STORAGE_DEFAULT_BUCKET_NAME - Default bucket name (optional)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List files in bucket')
    list_parser.add_argument('--bucket', '-b', help='Bucket name (uses default if not specified)')
    list_parser.add_argument('--path', '-p', default='', help='Path within bucket')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download a file from bucket')
    download_parser.add_argument('remote_path', help='Path to file in bucket')
    download_parser.add_argument('local_path', help='Local path to save file')
    download_parser.add_argument('--bucket', '-b', help='Bucket name (uses default if not specified)')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a file from bucket')
    delete_parser.add_argument('remote_path', help='Path to file in bucket')
    delete_parser.add_argument('--bucket', '-b', help='Bucket name (uses default if not specified)')
    
    # Delete batch command
    delete_batch_parser = subparsers.add_parser('delete-batch', help='Delete multiple files from bucket')
    delete_batch_parser.add_argument('remote_paths', nargs='+', help='Paths to files in bucket')
    delete_batch_parser.add_argument('--bucket', '-b', help='Bucket name (uses default if not specified)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'list':
            result = list_bucket_files(
                bucket_name=args.bucket,
                path=args.path
            )
            
            print(f"Found {len(result.files)} files:")
            for file in result.files:
                size_info = ""
                if hasattr(file, 'size') and file.size:
                    size_info = f" ({file.size} bytes)"
                
                date_info = ""
                if file.updated_at:
                    date_info = f" - Updated: {file.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"
                
                print(f"  {file.name}{size_info}{date_info}")
        
        elif args.command == 'download':
            result = download_file(
                remote_path=args.remote_path,
                local_path=args.local_path,
                bucket_name=args.bucket
            )
            
            if result.success:
                print(f"✅ Successfully downloaded '{args.remote_path}' to '{args.local_path}'")
                print(f"   File size: {result.file_size_bytes} bytes")
            else:
                print(f"❌ Download failed: {result.message}")
                return 1
        
        elif args.command == 'delete':
            result = delete_file(
                remote_path=args.remote_path,
                bucket_name=args.bucket
            )
            
            if result.success:
                print(f"✅ Successfully deleted '{args.remote_path}'")
            else:
                print(f"❌ Delete failed: {result.message}")
                return 1
        
        elif args.command == 'delete-batch':
            result = delete_files(
                remote_paths=args.remote_paths,
                bucket_name=args.bucket
            )
            
            print("Batch delete results:")
            print(f"  ✅ Successful: {len(result.successful_deletes)}")
            print(f"  ❌ Failed: {len(result.failed_deletes)}")
            
            if result.successful_deletes:
                print("  Successfully deleted:")
                for path in result.successful_deletes:
                    print(f"    - {path}")
            
            if result.failed_deletes:
                print("  Failed to delete:")
                for path in result.failed_deletes:
                    print(f"    - {path}")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
