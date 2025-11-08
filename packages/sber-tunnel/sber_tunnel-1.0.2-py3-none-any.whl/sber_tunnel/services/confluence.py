"""Confluence API service for file operations."""
import json
import hashlib
from typing import Optional, List, Dict, Any
from pathlib import Path
from atlassian import Confluence
from ..models.manifest import Manifest, FileEntry, FileChunk
from ..core.cert_handler import CertificateHandler
from ..core.utils import safe_print, get_safe_error_message


CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB
MANIFEST_FILENAME = "manifest.json"


class ConfluenceService:
    """Service for interacting with Confluence API."""

    def __init__(self, url: str, username: str, password: str,
                 cert_path: Optional[str] = None, cert_password: Optional[str] = None):
        """Initialize Confluence service.

        Args:
            url: Confluence base URL
            username: Username for authentication
            password: Password or API token
            cert_path: Path to p12 certificate (optional)
            cert_password: Password for certificate (optional)
        """
        self.url = url
        self.username = username
        self.cert_handler: Optional[CertificateHandler] = None

        # Initialize Confluence client
        if cert_path:
            # Extract p12 certificate to PEM files
            self.cert_handler = CertificateHandler()
            try:
                pem_cert_path, pem_key_path = self.cert_handler.extract_p12(
                    cert_path,
                    cert_password
                )

                # Initialize Confluence client with PEM certificate and key
                self.client = Confluence(
                    url=url,
                    username=username,
                    password=password,
                    verify_ssl=False,
                    cert=(pem_cert_path, pem_key_path)
                )
            except Exception as e:
                if self.cert_handler:
                    self.cert_handler.cleanup()
                raise ValueError(f"Failed to initialize Confluence with certificate: {e}")
        else:
            self.client = Confluence(
                url=url,
                username=username,
                password=password
            )

    def __del__(self):
        """Cleanup certificate handler on destruction."""
        if self.cert_handler:
            self.cert_handler.cleanup()

    def check_permissions(self, page_id: str) -> bool:
        """Check if user has permissions to add attachments to page.

        Args:
            page_id: Confluence page ID

        Returns:
            True if user has permissions, False otherwise
        """
        try:
            # Try to get page info
            page = self.client.get_page_by_id(page_id, expand='version')
            if not page:
                return False

            # Try to get attachments to verify permissions
            self.client.get_attachments_from_content(page_id)
            return True
        except Exception as e:
            # Handle encoding issues in error messages
            error_msg = get_safe_error_message(e)
            safe_print(f"Permission check failed: {error_msg}")
            return False

    def download_manifest(self, page_id: str) -> Optional[Manifest]:
        """Download manifest from Confluence page.

        Args:
            page_id: Confluence page ID

        Returns:
            Manifest object or None if not found
        """
        try:
            attachments = self.client.get_attachments_from_content(page_id)

            if not attachments or 'results' not in attachments:
                return None

            # Find manifest file
            manifest_attachment = None
            for att in attachments['results']:
                if att['title'] == MANIFEST_FILENAME:
                    manifest_attachment = att
                    break

            if not manifest_attachment:
                return None

            # Download manifest
            download_url = self.url + manifest_attachment['_links']['download']
            response = self.client.request(path=download_url, absolute=True)

            if response.status_code == 200:
                manifest_data = response.json()
                return Manifest(**manifest_data)

            return None
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Error downloading manifest: {error_msg}")
            return None

    def upload_manifest(self, page_id: str, manifest: Manifest) -> bool:
        """Upload manifest to Confluence page.

        Args:
            page_id: Confluence page ID
            manifest: Manifest object to upload

        Returns:
            True if successful, False otherwise
        """
        try:
            manifest_json = manifest.model_dump_json(indent=2)

            # Create temporary file
            temp_file = Path("/tmp") / MANIFEST_FILENAME
            temp_file.write_text(manifest_json)

            # Upload as attachment
            self.client.attach_file(
                filename=str(temp_file),
                name=MANIFEST_FILENAME,
                content_type="application/json",
                page_id=page_id,
                comment="Updated manifest"
            )

            # Clean up
            temp_file.unlink()
            return True
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Error uploading manifest: {error_msg}")
            return False

    def upload_file_chunk(self, page_id: str, chunk_name: str,
                         chunk_data: bytes) -> Optional[str]:
        """Upload file chunk to Confluence.

        Args:
            page_id: Confluence page ID
            chunk_name: Name for the chunk
            chunk_data: Binary data of the chunk

        Returns:
            Attachment ID if successful, None otherwise
        """
        try:
            # Create temporary file
            temp_file = Path("/tmp") / chunk_name
            temp_file.write_bytes(chunk_data)

            # Upload as attachment
            result = self.client.attach_file(
                filename=str(temp_file),
                name=chunk_name,
                page_id=page_id
            )

            # Clean up
            temp_file.unlink()

            if result and 'id' in result:
                return result['id']
            return None
        except Exception as e:
            error_msg = get_safe_error_message(e); safe_print(f"Error uploading chunk: {error_msg}")
            return None

    def download_file_chunk(self, page_id: str, chunk_name: str) -> Optional[bytes]:
        """Download file chunk from Confluence.

        Args:
            page_id: Confluence page ID
            chunk_name: Name of the chunk to download

        Returns:
            Binary data of the chunk or None if not found
        """
        try:
            attachments = self.client.get_attachments_from_content(page_id)

            if not attachments or 'results' not in attachments:
                return None

            # Find chunk
            chunk_attachment = None
            for att in attachments['results']:
                if att['title'] == chunk_name:
                    chunk_attachment = att
                    break

            if not chunk_attachment:
                return None

            # Download chunk
            download_url = self.url + chunk_attachment['_links']['download']
            response = self.client.request(path=download_url, absolute=True)

            if response.status_code == 200:
                return response.content

            return None
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Error downloading chunk: {error_msg}")
            return None

    def upload_file(self, page_id: str, file_path: Path, file_id: str) -> Optional[FileEntry]:
        """Upload file to Confluence, splitting into chunks if needed.

        Args:
            page_id: Confluence page ID
            file_path: Path to file to upload
            file_id: Unique ID for the file

        Returns:
            FileEntry object or None if failed
        """
        try:
            # Calculate file hash
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            file_hash = sha256.hexdigest()

            # Get file stats
            stat = file_path.stat()
            file_size = stat.st_size
            mtime = stat.st_mtime

            chunks = []

            # Split file into chunks if needed
            if file_size > CHUNK_SIZE:
                chunk_order = 0
                with open(file_path, 'rb') as f:
                    while True:
                        chunk_data = f.read(CHUNK_SIZE)
                        if not chunk_data:
                            break

                        # Calculate chunk hash
                        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                        chunk_name = f"{file_id}.part{chunk_order:04d}"

                        # Upload chunk
                        attachment_id = self.upload_file_chunk(page_id, chunk_name, chunk_data)

                        if not attachment_id:
                            safe_print(f"Failed to upload chunk {chunk_order}")
                            return None

                        chunks.append(FileChunk(
                            order=chunk_order,
                            checksum=chunk_hash,
                            attachment_id=attachment_id
                        ))
                        chunk_order += 1
            else:
                # Upload as single chunk
                with open(file_path, 'rb') as f:
                    chunk_data = f.read()

                chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                chunk_name = f"{file_id}.part0000"

                attachment_id = self.upload_file_chunk(page_id, chunk_name, chunk_data)

                if not attachment_id:
                    return None

                chunks.append(FileChunk(
                    order=0,
                    checksum=chunk_hash,
                    attachment_id=attachment_id
                ))

            # Create file entry
            return FileEntry(
                id=file_id,
                path=str(file_path),
                size=file_size,
                mtime=mtime,
                sha256=file_hash,
                version=1,
                chunks=chunks
            )
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Error uploading file: {error_msg}")
            return None

    def download_file(self, page_id: str, file_entry: FileEntry, output_path: Path) -> bool:
        """Download file from Confluence, assembling chunks if needed.

        Args:
            page_id: Confluence page ID
            file_entry: FileEntry object with file metadata
            output_path: Path where to save the file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Download and assemble chunks
            with open(output_path, 'wb') as out_file:
                for chunk in sorted(file_entry.chunks, key=lambda c: c.order):
                    chunk_name = f"{file_entry.id}.part{chunk.order:04d}"
                    chunk_data = self.download_file_chunk(page_id, chunk_name)

                    if not chunk_data:
                        safe_print(f"Failed to download chunk {chunk.order}")
                        return False

                    # Verify chunk checksum
                    chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                    if chunk_hash != chunk.checksum:
                        safe_print(f"Checksum mismatch for chunk {chunk.order}")
                        return False

                    out_file.write(chunk_data)

            # Verify final file hash
            sha256 = hashlib.sha256()
            with open(output_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)

            if sha256.hexdigest() != file_entry.sha256:
                safe_print("Final file checksum mismatch")
                output_path.unlink()
                return False

            # Set modification time
            import os
            os.utime(output_path, (file_entry.mtime, file_entry.mtime))

            return True
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Error downloading file: {error_msg}")
            return False

    def delete_file_chunks(self, page_id: str, file_id: str) -> bool:
        """Delete all chunks of a file from Confluence.

        Args:
            page_id: Confluence page ID
            file_id: ID of the file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            attachments = self.client.get_attachments_from_content(page_id)

            if not attachments or 'results' not in attachments:
                return True

            # Find and delete all chunks
            for att in attachments['results']:
                if att['title'].startswith(f"{file_id}.part"):
                    self.client.delete_attachment(att['id'])

            return True
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Error deleting file chunks: {error_msg}")
            return False
