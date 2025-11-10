"""Менеджер файлов для upload/download операций."""
import hashlib
import os
import uuid
from pathlib import Path
from typing import List, Optional
from ..models.manifest import Manifest, FileEntry, FileChunk
from ..services.confluence import ConfluenceService, CHUNK_SIZE
from ..core.utils import safe_print


class FileManager:
    """Менеджер для работы с файлами и директориями."""

    def __init__(self, confluence: ConfluenceService):
        """Инициализация менеджера файлов.

        Args:
            confluence: Сервис Confluence
        """
        self.confluence = confluence

    def _should_exclude(self, path: Path) -> bool:
        """Проверить, нужно ли исключить файл/директорию.

        Args:
            path: Путь к файлу/директории

        Returns:
            True если нужно исключить
        """
        # Исключить скрытые файлы и директории
        if any(part.startswith('.') for part in path.parts):
            return True

        # Исключить временные файлы
        if path.name.endswith('~') or path.name.startswith('~'):
            return True

        return False

    def _collect_files(self, directory: Path) -> List[Path]:
        """Собрать все файлы из директории рекурсивно.

        Args:
            directory: Путь к директории

        Returns:
            Список путей к файлам
        """
        files = []
        for item in directory.rglob('*'):
            if item.is_file() and not self._should_exclude(item):
                files.append(item)
        return files

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Вычислить SHA256 хеш файла.

        Args:
            file_path: Путь к файлу

        Returns:
            SHA256 хеш в hex формате
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _upload_file(self, file_path: Path, parent: str, base_dir: Path, page_id: str) -> Optional[FileEntry]:
        """Загрузить файл в Confluence с чанкованием.

        Args:
            file_path: Путь к файлу
            parent: Имя родительской директории
            base_dir: Базовая директория для вычисления относительного пути
            page_id: ID страницы Confluence

        Returns:
            Объект FileEntry или None если ошибка
        """
        try:
            # Вычислить относительный путь
            rel_path = str(file_path.relative_to(base_dir))

            # Вычислить хеш файла
            file_hash = self._calculate_file_hash(file_path)

            # Получить информацию о файле
            stat = file_path.stat()
            file_size = stat.st_size
            mtime = stat.st_mtime

            # Генерировать уникальный ID файла
            file_id = str(uuid.uuid4())

            chunks = []

            # Чанкование файла если >100 МБ
            if file_size > CHUNK_SIZE:
                safe_print(f"  Файл {rel_path} больше 100 МБ, чанкование...")
                chunk_order = 0
                with open(file_path, 'rb') as f:
                    while True:
                        chunk_data = f.read(CHUNK_SIZE)
                        if not chunk_data:
                            break

                        # Вычислить хеш чанка
                        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                        chunk_name = f"{file_id}.part{chunk_order:04d}"

                        # Загрузить чанк
                        if not self.confluence.upload_file_chunk(page_id, chunk_name, chunk_data):
                            safe_print(f"  Ошибка загрузки чанка {chunk_order}")
                            return None

                        chunks.append(FileChunk(order=chunk_order, checksum=chunk_hash))
                        chunk_order += 1
                        safe_print(f"    Загружен чанк {chunk_order}/{(file_size + CHUNK_SIZE - 1) // CHUNK_SIZE}")
            else:
                # Загрузить как один чанк
                with open(file_path, 'rb') as f:
                    chunk_data = f.read()

                chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                chunk_name = f"{file_id}.part0000"

                if not self.confluence.upload_file_chunk(page_id, chunk_name, chunk_data):
                    safe_print(f"  Ошибка загрузки файла {rel_path}")
                    return None

                chunks.append(FileChunk(order=0, checksum=chunk_hash))

            # Создать запись о файле
            return FileEntry(
                id=file_id,
                path=rel_path,
                parent=parent,
                size=file_size,
                mtime=mtime,
                sha256=file_hash,
                version=1,
                chunks=chunks
            )
        except Exception as e:
            safe_print(f"  Ошибка загрузки файла {file_path}: {e}")
            return None

    def upload_directory(self, directory: Path, page_id: str) -> bool:
        """Загрузить директорию со всем содержимым в Confluence.

        Args:
            directory: Путь к директории
            page_id: ID страницы Confluence

        Returns:
            True если успешно
        """
        try:
            safe_print(f"\nЗагрузка директории {directory.name}...")

            # Получить текущий манифест
            manifest = self.confluence.download_manifest(page_id)

            # Собрать все файлы
            files = self._collect_files(directory)
            safe_print(f"Найдено файлов: {len(files)}")

            parent_name = directory.name

            # Загрузить каждый файл
            for i, file_path in enumerate(files, 1):
                rel_path = str(file_path.relative_to(directory))
                safe_print(f"\n[{i}/{len(files)}] Загрузка {rel_path}...")

                file_entry = self._upload_file(file_path, parent_name, directory, page_id)
                if file_entry:
                    manifest.add_or_update_file(file_entry)
                    safe_print(f"  ✓ Загружен")
                else:
                    safe_print(f"  ✗ Ошибка")

            # Обновить манифест
            safe_print("\nОбновление манифеста...")
            if self.confluence.upload_manifest(page_id, manifest):
                safe_print("✓ Манифест обновлен")
                return True
            else:
                safe_print("✗ Ошибка обновления манифеста")
                return False

        except Exception as e:
            safe_print(f"Ошибка загрузки директории: {e}")
            return False

    def download_directory(self, page_id: str, parent_name: str, output_path: Path) -> bool:
        """Скачать директорию со всем содержимым из Confluence.

        Args:
            page_id: ID страницы Confluence
            parent_name: Имя родительской директории
            output_path: Путь для сохранения

        Returns:
            True если успешно
        """
        try:
            safe_print(f"\nСкачивание директории {parent_name}...")

            # Получить манифест
            manifest = self.confluence.download_manifest(page_id)

            # Получить файлы для указанной родительской директории
            files = manifest.get_files_by_parent(parent_name)

            if not files:
                safe_print(f"Директория {parent_name} не найдена в манифесте")
                return False

            safe_print(f"Найдено файлов: {len(files)}")

            # Создать выходную директорию
            output_path.mkdir(parents=True, exist_ok=True)

            # Скачать каждый файл
            for i, file_entry in enumerate(files, 1):
                safe_print(f"\n[{i}/{len(files)}] Скачивание {file_entry.path}...")

                file_path = output_path / file_entry.path
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Скачать и собрать чанки
                with open(file_path, 'wb') as out_file:
                    for chunk in sorted(file_entry.chunks, key=lambda c: c.order):
                        chunk_name = f"{file_entry.id}.part{chunk.order:04d}"
                        chunk_data = self.confluence.download_file_chunk(page_id, chunk_name)

                        if not chunk_data:
                            safe_print(f"  Ошибка скачивания чанка {chunk.order}")
                            return False

                        # Проверить контрольную сумму чанка
                        chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                        if chunk_hash != chunk.checksum:
                            safe_print(f"  Ошибка контрольной суммы чанка {chunk.order}")
                            return False

                        out_file.write(chunk_data)

                # Проверить финальную контрольную сумму файла
                file_hash = self._calculate_file_hash(file_path)
                if file_hash != file_entry.sha256:
                    safe_print(f"  Ошибка контрольной суммы файла")
                    file_path.unlink()
                    return False

                # Установить время модификации
                os.utime(file_path, (file_entry.mtime, file_entry.mtime))
                safe_print(f"  ✓ Скачан")

            safe_print(f"\n✓ Директория {parent_name} успешно скачана в {output_path}")
            return True

        except Exception as e:
            safe_print(f"Ошибка скачивания директории: {e}")
            return False

    def scan_manifest(self, page_id: str) -> List[str]:
        """Получить список родительских директорий из манифеста.

        Args:
            page_id: ID страницы Confluence

        Returns:
            Список имен родительских директорий
        """
        try:
            manifest = self.confluence.download_manifest(page_id)
            return manifest.get_parents()
        except Exception as e:
            safe_print(f"Ошибка чтения манифеста: {e}")
            return []
