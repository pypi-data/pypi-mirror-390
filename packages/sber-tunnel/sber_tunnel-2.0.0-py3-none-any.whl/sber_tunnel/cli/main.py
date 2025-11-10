"""CLI интерфейс для sber-tunnel."""
import click
from pathlib import Path
from ..services.confluence import ConfluenceService
from ..services.file_manager import FileManager
from ..core.config import Config


@click.group()
def cli():
    """Sber-tunnel - Тунель для передачи файлов через Confluence."""
    pass


@cli.command()
def init():
    """Инициализация конфигурации sber-tunnel."""
    click.echo("=== Инициализация Sber-tunnel ===\n")

    # Сбор конфигурации
    base_url = click.prompt("Confluence base URL")
    username = click.prompt("Имя пользователя")
    password = click.prompt("Пароль", hide_input=True)

    # Опциональный сертификат
    use_cert = click.confirm("Использовать p12 сертификат?", default=False)
    cert_path = None
    cert_password = None

    if use_cert:
        cert_path = click.prompt("Путь к p12 сертификату")
        cert_password = click.prompt("Пароль сертификата", hide_input=True)

    click.echo("\nПроверка учетных данных...")

    # Проверка подключения
    try:
        confluence = ConfluenceService(
            url=base_url,
            username=username,
            password=password,
            cert_path=cert_path,
            cert_password=cert_password
        )

        click.echo("✓ Учетные данные проверены!")

        # Сохранение конфигурации
        config = Config()
        config.set('base_url', base_url)
        config.set('username', username)
        config.set('password', password)

        if cert_path:
            config.set('cert_path', cert_path)
            config.set('cert_password', cert_password)

        config.save()

        click.echo(f"\n✓ Конфигурация сохранена в {config.config_path}")
        click.echo("\nТеперь вы можете использовать:")
        click.echo("  - sber-tunnel scan -p <page_id>")
        click.echo("  - sber-tunnel upload -p <page_id> <путь/к/директории>")
        click.echo("  - sber-tunnel download -p <page_id> -d <имя-директории> <путь/для/сохранения>")

    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        return 1


@cli.command()
@click.option('-p', '--page-id', required=True, help='ID страницы Confluence')
def scan(page_id):
    """Просмотр манифеста - список загруженных директорий."""
    config = Config()
    if not config.is_configured():
        click.echo("✗ Ошибка: Не инициализировано. Запустите 'sber-tunnel init'", err=True)
        return 1

    try:
        # Создать сервис Confluence
        confluence = ConfluenceService(
            url=config.get('base_url'),
            username=config.get('username'),
            password=config.get('password'),
            cert_path=config.get('cert_path'),
            cert_password=config.get('cert_password')
        )

        # Создать менеджер файлов
        file_manager = FileManager(confluence)

        # Получить список директорий
        parents = file_manager.scan_manifest(page_id)

        if not parents:
            click.echo("Манифест пуст или не найден")
            return 0

        click.echo("\n=== Загруженные директории ===\n")
        for parent in parents:
            click.echo(f"  • {parent}")

        click.echo(f"\nВсего директорий: {len(parents)}")

    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        return 1


@cli.command()
@click.option('-p', '--page-id', required=True, help='ID страницы Confluence')
@click.option('-d', '--parent-dir', required=True, help='Имя родительской директории')
@click.argument('output_path', type=click.Path())
def download(page_id, parent_dir, output_path):
    """Скачать директорию со всем содержимым."""
    config = Config()
    if not config.is_configured():
        click.echo("✗ Ошибка: Не инициализировано. Запустите 'sber-tunnel init'", err=True)
        return 1

    try:
        output = Path(output_path).resolve()

        # Создать сервис Confluence
        confluence = ConfluenceService(
            url=config.get('base_url'),
            username=config.get('username'),
            password=config.get('password'),
            cert_path=config.get('cert_path'),
            cert_password=config.get('cert_password')
        )

        # Создать менеджер файлов
        file_manager = FileManager(confluence)

        # Скачать директорию
        success = file_manager.download_directory(page_id, parent_dir, output)

        if success:
            click.echo("\n✓ Скачивание завершено успешно")
            return 0
        else:
            click.echo("\n✗ Ошибка скачивания", err=True)
            return 1

    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        return 1


@cli.command()
@click.option('-p', '--page-id', required=True, help='ID страницы Confluence')
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def upload(page_id, directory):
    """Загрузить директорию со всем содержимым."""
    config = Config()
    if not config.is_configured():
        click.echo("✗ Ошибка: Не инициализировано. Запустите 'sber-tunnel init'", err=True)
        return 1

    try:
        dir_path = Path(directory).resolve()

        # Проверка прав на страницу
        click.echo(f"Проверка прав на страницу {page_id}...")

        # Создать сервис Confluence
        confluence = ConfluenceService(
            url=config.get('base_url'),
            username=config.get('username'),
            password=config.get('password'),
            cert_path=config.get('cert_path'),
            cert_password=config.get('cert_password')
        )

        if not confluence.check_permissions(page_id):
            click.echo("✗ Ошибка: Нет прав на добавление файлов на эту страницу", err=True)
            return 1

        click.echo("✓ Права проверены")

        # Создать менеджер файлов
        file_manager = FileManager(confluence)

        # Загрузить директорию
        success = file_manager.upload_directory(dir_path, page_id)

        if success:
            click.echo("\n✓ Загрузка завершена успешно")
            return 0
        else:
            click.echo("\n✗ Ошибка загрузки", err=True)
            return 1

    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        return 1


if __name__ == '__main__':
    cli()
