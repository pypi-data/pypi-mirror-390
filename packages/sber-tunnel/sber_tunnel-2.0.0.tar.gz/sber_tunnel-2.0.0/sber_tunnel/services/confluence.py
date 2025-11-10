"""Сервис для работы с Confluence API."""
import hashlib
from typing import Optional
from pathlib import Path
from atlassian import Confluence
from ..models.manifest import Manifest, FileEntry, FileChunk
from ..core.cert_handler import CertificateHandler
from ..core.utils import safe_print, get_safe_error_message


CHUNK_SIZE = 100 * 1024 * 1024  # 100 MB
MANIFEST_FILENAME = "st-manifest.json"


class ConfluenceService:
    """Сервис для работы с Confluence API."""

    def __init__(self, url: str, username: str, password: str,
                 cert_path: Optional[str] = None, cert_password: Optional[str] = None):
        """Инициализация сервиса Confluence.

        Args:
            url: Базовый URL Confluence
            username: Имя пользователя
            password: Пароль или API token
            cert_path: Путь к сертификату p12 (опционально)
            cert_password: Пароль для сертификата (опционально)
        """
        self.url = url
        self.username = username
        self.cert_handler: Optional[CertificateHandler] = None

        # Инициализация клиента Confluence
        if cert_path:
            # Извлечение сертификата p12 в PEM файлы
            self.cert_handler = CertificateHandler()
            try:
                pem_cert_path, pem_key_path = self.cert_handler.extract_p12(
                    cert_path,
                    cert_password
                )

                # Инициализация клиента с сертификатом
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
                raise ValueError(f"Не удалось инициализировать Confluence с сертификатом: {e}")
        else:
            self.client = Confluence(
                url=url,
                username=username,
                password=password
            )

    def __del__(self):
        """Очистка при удалении объекта."""
        if self.cert_handler:
            self.cert_handler.cleanup()

    def check_permissions(self, page_id: str) -> bool:
        """Проверка прав на добавление файлов на страницу.

        Args:
            page_id: ID страницы Confluence

        Returns:
            True если есть права, False иначе
        """
        try:
            page = self.client.get_page_by_id(page_id, expand='version')
            if not page:
                return False

            self.client.get_attachments_from_content(page_id)
            return True
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Ошибка проверки прав: {error_msg}")
            return False

    def download_manifest(self, page_id: str) -> Optional[Manifest]:
        """Скачать манифест со страницы Confluence.

        Args:
            page_id: ID страницы Confluence

        Returns:
            Объект Manifest или None если не найден
        """
        try:
            attachments = self.client.get_attachments_from_content(page_id)

            if not attachments or 'results' not in attachments:
                return Manifest(files=[])  # Пустой манифест если не найден

            # Найти файл манифеста
            manifest_attachment = None
            for att in attachments['results']:
                if att['title'] == MANIFEST_FILENAME:
                    manifest_attachment = att
                    break

            if not manifest_attachment:
                return Manifest(files=[])  # Пустой манифест если не найден

            # Скачать манифест
            download_url = self.url + manifest_attachment['_links']['download']
            response = self.client.request(path=download_url, absolute=True)

            if response.status_code == 200:
                return Manifest.from_json(response.text)

            return Manifest(files=[])
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Ошибка скачивания манифеста: {error_msg}")
            return Manifest(files=[])

    def upload_manifest(self, page_id: str, manifest: Manifest) -> bool:
        """Загрузить манифест на страницу Confluence.

        Args:
            page_id: ID страницы Confluence
            manifest: Объект Manifest для загрузки

        Returns:
            True если успешно, False иначе
        """
        try:
            manifest_json = manifest.to_json()

            # Создать временный файл
            temp_file = Path("/tmp") / MANIFEST_FILENAME
            temp_file.write_text(manifest_json, encoding='utf-8')

            # Загрузить как attachment
            self.client.attach_file(
                filename=str(temp_file),
                name=MANIFEST_FILENAME,
                content_type="application/json",
                page_id=page_id,
                comment="Обновлен манифест"
            )

            # Удалить временный файл
            temp_file.unlink()
            return True
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Ошибка загрузки манифеста: {error_msg}")
            return False

    def upload_file_chunk(self, page_id: str, chunk_name: str, chunk_data: bytes) -> bool:
        """Загрузить чанк файла в Confluence.

        Args:
            page_id: ID страницы Confluence
            chunk_name: Имя чанка
            chunk_data: Бинарные данные чанка

        Returns:
            True если успешно, False иначе
        """
        try:
            # Создать временный файл
            temp_file = Path("/tmp") / chunk_name
            temp_file.write_bytes(chunk_data)

            # Загрузить как attachment
            self.client.attach_file(
                filename=str(temp_file),
                name=chunk_name,
                page_id=page_id
            )

            # Удалить временный файл
            temp_file.unlink()
            return True
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Ошибка загрузки чанка: {error_msg}")
            return False

    def download_file_chunk(self, page_id: str, chunk_name: str) -> Optional[bytes]:
        """Скачать чанк файла из Confluence.

        Args:
            page_id: ID страницы Confluence
            chunk_name: Имя чанка

        Returns:
            Бинарные данные чанка или None если не найден
        """
        try:
            attachments = self.client.get_attachments_from_content(page_id)

            if not attachments or 'results' not in attachments:
                return None

            # Найти чанк
            chunk_attachment = None
            for att in attachments['results']:
                if att['title'] == chunk_name:
                    chunk_attachment = att
                    break

            if not chunk_attachment:
                return None

            # Скачать чанк
            download_url = self.url + chunk_attachment['_links']['download']
            response = self.client.request(path=download_url, absolute=True)

            if response.status_code == 200:
                return response.content

            return None
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Ошибка скачивания чанка: {error_msg}")
            return None

    def delete_file_chunks(self, page_id: str, file_id: str) -> bool:
        """Удалить все чанки файла из Confluence.

        Args:
            page_id: ID страницы Confluence
            file_id: ID файла для удаления

        Returns:
            True если успешно, False иначе
        """
        try:
            attachments = self.client.get_attachments_from_content(page_id)

            if not attachments or 'results' not in attachments:
                return True

            # Найти и удалить все чанки
            for att in attachments['results']:
                if att['title'].startswith(f"{file_id}.part"):
                    try:
                        self.client.delete_attachment(att['id'])
                    except Exception as e:
                        error_msg = get_safe_error_message(e)
                        safe_print(f"Ошибка удаления чанка {att['title']}: {error_msg}")

            return True
        except Exception as e:
            error_msg = get_safe_error_message(e)
            safe_print(f"Ошибка удаления чанков файла: {error_msg}")
            return False
