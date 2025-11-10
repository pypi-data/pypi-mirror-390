"""Модели для st-manifest.json согласно новой спецификации."""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
import json


@dataclass
class FileChunk:
    """Чанк файла."""
    order: int
    checksum: str  # sha256


@dataclass
class FileEntry:
    """Запись о файле в манифесте."""
    id: str
    path: str  # путь внутри родительской директории
    parent: str  # имя родительской директории
    size: int
    mtime: float
    sha256: str
    version: int
    chunks: List[FileChunk]

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            'id': self.id,
            'path': self.path,
            'parent': self.parent,
            'size': self.size,
            'mtime': self.mtime,
            'sha256': self.sha256,
            'version': self.version,
            'chunks': [{'order': c.order, 'checksum': c.checksum} for c in self.chunks]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'FileEntry':
        """Создать из словаря."""
        chunks = [FileChunk(order=c['order'], checksum=c['checksum'])
                  for c in data.get('chunks', [])]
        return FileEntry(
            id=data['id'],
            path=data['path'],
            parent=data['parent'],
            size=data['size'],
            mtime=data['mtime'],
            sha256=data['sha256'],
            version=data['version'],
            chunks=chunks
        )


@dataclass
class Manifest:
    """Манифест st-manifest.json."""
    files: List[FileEntry]

    def to_json(self) -> str:
        """Преобразовать в JSON строку."""
        return json.dumps([f.to_dict() for f in self.files], indent=2, ensure_ascii=False)

    @staticmethod
    def from_json(json_str: str) -> 'Manifest':
        """Создать из JSON строки."""
        data = json.loads(json_str)
        files = [FileEntry.from_dict(f) for f in data]
        return Manifest(files=files)

    def get_file_by_path_and_parent(self, path: str, parent: str) -> Optional[FileEntry]:
        """Получить файл по пути и родительской директории."""
        for file in self.files:
            if file.path == path and file.parent == parent:
                return file
        return None

    def get_file_by_id(self, file_id: str) -> Optional[FileEntry]:
        """Получить файл по ID."""
        for file in self.files:
            if file.id == file_id:
                return file
        return None

    def get_parents(self) -> List[str]:
        """Получить список всех родительских директорий."""
        return list(set(f.parent for f in self.files))

    def get_files_by_parent(self, parent: str) -> List[FileEntry]:
        """Получить все файлы для указанной родительской директории."""
        return [f for f in self.files if f.parent == parent]

    def add_or_update_file(self, file_entry: FileEntry):
        """Добавить или обновить файл в манифесте."""
        existing = self.get_file_by_id(file_entry.id)
        if existing:
            self.files.remove(existing)
        self.files.append(file_entry)

    def remove_file(self, file_id: str):
        """Удалить файл из манифеста."""
        self.files = [f for f in self.files if f.id != file_id]
