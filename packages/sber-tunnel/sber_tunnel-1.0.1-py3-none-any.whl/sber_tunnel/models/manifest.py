"""Manifest model for tracking files."""
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class FileChunk(BaseModel):
    """Chunk of a file."""
    order: int
    checksum: str
    attachment_id: Optional[str] = None


class FileEntry(BaseModel):
    """File entry in manifest."""
    id: str
    path: str
    size: int
    mtime: float
    sha256: str
    version: int
    chunks: List[FileChunk] = []
    deleted: bool = False


class Manifest(BaseModel):
    """Manifest containing all tracked files."""
    version: int = 1
    last_updated: float
    files: List[FileEntry] = []

    def get_file_by_path(self, path: str) -> Optional[FileEntry]:
        """Get file entry by path."""
        for file in self.files:
            if file.path == path:
                return file
        return None

    def get_file_by_id(self, file_id: str) -> Optional[FileEntry]:
        """Get file entry by id."""
        for file in self.files:
            if file.id == file_id:
                return file
        return None
