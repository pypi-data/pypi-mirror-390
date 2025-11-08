"""Synchronization service."""
import hashlib
import uuid
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from .confluence import ConfluenceService
from ..db.schema import Database
from ..models.manifest import Manifest, FileEntry


class SyncService:
    """Service for synchronizing files between local and Confluence."""

    def __init__(self, confluence: ConfluenceService, db: Database):
        """Initialize sync service.

        Args:
            confluence: Confluence service instance
            db: Database instance
        """
        self.confluence = confluence
        self.db = db

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def scan_directory(self, directory: Path) -> List[Path]:
        """Scan directory for files, excluding hidden and temp files.

        Args:
            directory: Directory to scan

        Returns:
            List of file paths
        """
        files = []
        for path in directory.rglob('*'):
            if path.is_file():
                # Skip hidden files and directories
                if any(part.startswith('.') for part in path.parts):
                    continue
                # Skip temporary files
                if path.name.endswith('~') or path.name.startswith('~'):
                    continue
                files.append(path)
        return files

    def sync_directory(self, dir_id: int, local_path: Path, page_id: str) -> bool:
        """Synchronize directory with Confluence.

        Args:
            dir_id: Directory ID in database
            local_path: Local directory path
            page_id: Confluence page ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Download current manifest from Confluence
            remote_manifest = self.confluence.download_manifest(page_id)
            if not remote_manifest:
                # Create new manifest if doesn't exist
                remote_manifest = Manifest(
                    version=1,
                    last_updated=datetime.now().timestamp(),
                    files=[]
                )

            # Scan local directory
            local_files = self.scan_directory(local_path)

            # Build local manifest
            local_file_map = {}
            for file_path in local_files:
                relative_path = file_path.relative_to(local_path)
                stat = file_path.stat()

                # Check if file changed
                db_file = self.db.get_file_by_path(str(relative_path))

                if db_file and db_file['mtime'] == stat.st_mtime and db_file['size'] == stat.st_size:
                    # File hasn't changed, use cached hash
                    file_hash = db_file['hash']
                    file_id = db_file['id']
                else:
                    # File changed or new, calculate hash
                    file_hash = self.calculate_file_hash(file_path)
                    file_id = str(uuid.uuid4())

                local_file_map[str(relative_path)] = {
                    'id': file_id,
                    'path': file_path,
                    'relative_path': str(relative_path),
                    'hash': file_hash,
                    'size': stat.st_size,
                    'mtime': stat.st_mtime
                }

            # Compare with remote manifest
            updates_needed = []
            downloads_needed = []

            # Check for files to upload
            for rel_path, local_info in local_file_map.items():
                remote_file = remote_manifest.get_file_by_path(rel_path)

                if not remote_file or remote_file.sha256 != local_info['hash']:
                    # File is new or changed, need to upload
                    updates_needed.append(local_info)

            # Check for files to download
            for remote_file in remote_manifest.files:
                if remote_file.deleted:
                    continue

                if remote_file.path not in local_file_map:
                    # File exists remotely but not locally, need to download
                    downloads_needed.append(remote_file)
                else:
                    local_info = local_file_map[remote_file.path]
                    if remote_file.sha256 != local_info['hash']:
                        # Check which version is newer (last-write-wins)
                        if remote_file.mtime > local_info['mtime']:
                            downloads_needed.append(remote_file)

            # Upload changed files
            for local_info in updates_needed:
                print(f"Uploading: {local_info['relative_path']}")

                file_entry = self.confluence.upload_file(
                    page_id=page_id,
                    file_path=local_info['path'],
                    file_id=local_info['id']
                )

                if file_entry:
                    # Update local database
                    self.db.add_file(
                        file_id=local_info['id'],
                        path=local_info['relative_path'],
                        size=local_info['size'],
                        mtime=local_info['mtime'],
                        hash=local_info['hash']
                    )

                    # Update manifest
                    existing = remote_manifest.get_file_by_path(local_info['relative_path'])
                    if existing:
                        remote_manifest.files.remove(existing)
                    remote_manifest.files.append(file_entry)
                else:
                    print(f"Failed to upload: {local_info['relative_path']}")

            # Download new/changed files
            for remote_file in downloads_needed:
                print(f"Downloading: {remote_file.path}")

                output_path = local_path / remote_file.path
                success = self.confluence.download_file(
                    page_id=page_id,
                    file_entry=remote_file,
                    output_path=output_path
                )

                if success:
                    # Update local database
                    self.db.add_file(
                        file_id=remote_file.id,
                        path=remote_file.path,
                        size=remote_file.size,
                        mtime=remote_file.mtime,
                        hash=remote_file.sha256
                    )
                else:
                    print(f"Failed to download: {remote_file.path}")

            # Check for deleted files
            for remote_file in remote_manifest.files:
                if remote_file.path not in local_file_map and not remote_file.deleted:
                    # File was deleted locally
                    print(f"Marking as deleted: {remote_file.path}")
                    remote_file.deleted = True

                    # Update database
                    self.db.mark_file_deleted(remote_file.id)

            # Upload updated manifest
            remote_manifest.last_updated = datetime.now().timestamp()
            if self.confluence.upload_manifest(page_id, remote_manifest):
                # Update sync time
                self.db.update_dir_sync_time(dir_id)
                return True
            else:
                print("Failed to upload manifest")
                return False

        except Exception as e:
            print(f"Sync error: {e}")
            import traceback
            traceback.print_exc()
            return False
