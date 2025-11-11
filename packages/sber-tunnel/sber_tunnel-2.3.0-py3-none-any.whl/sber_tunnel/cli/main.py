"""CLI интерфейс для sber-tunnel."""
import click
import warnings
from pathlib import Path
from ..services.confluence import ConfluenceService
from ..services.file_manager import FileManager
from ..core.config import Config
from ..core.utils import set_debug_mode

# Отключить все warnings
warnings.filterwarnings('ignore')


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
@click.option('--debug', is_flag=True, help='Включить отладочный вывод')
def scan(page_id, debug):
    """Просмотр манифеста - список загруженных директорий."""
    set_debug_mode(debug)

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
@click.option('--debug', is_flag=True, help='Включить отладочный вывод')
@click.argument('output_path', type=click.Path())
def download(page_id, parent_dir, output_path, debug):
    """Скачать директорию со всем содержимым."""
    set_debug_mode(debug)

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
@click.option('--debug', is_flag=True, help='Включить отладочный вывод')
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def upload(page_id, directory, debug):
    """Загрузить директорию со всем содержимым."""
    set_debug_mode(debug)

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


@cli.command()
@click.option('-p', '--page-id', required=True, help='ID страницы Confluence')
@click.option('-d', '--parent-dir', required=True, help='Имя родительской директории для удаления')
@click.option('--debug', is_flag=True, help='Включить отладочный вывод')
@click.option('--yes', '-y', is_flag=True, help='Пропустить подтверждение удаления')
def delete(page_id, parent_dir, debug, yes):
    """Удалить директорию со всеми вложениями из Confluence."""
    set_debug_mode(debug)

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

        # Получить информацию о директории
        manifest = confluence.download_manifest(page_id)
        if not manifest:
            click.echo("✗ Манифест не найден на странице", err=True)
            return 1

        files = manifest.get_files_by_parent(parent_dir)
        if not files:
            click.echo(f"✗ Директория '{parent_dir}' не найдена", err=True)
            click.echo(f"\nДоступные директории:")
            for parent in manifest.get_parents():
                click.echo(f"  • {parent}")
            return 1

        # Показать информацию и запросить подтверждение
        total_size = sum(f.size for f in files)
        total_chunks = sum(len(f.chunks) for f in files)

        click.echo(f"\n⚠️  ВНИМАНИЕ: Будет удалено:")
        click.echo(f"  • Директория: {parent_dir}")
        click.echo(f"  • Файлов: {len(files)}")
        click.echo(f"  • Общий размер: {total_size / 1024 / 1024:.2f} МБ")
        click.echo(f"  • Всего чанков (attachments): {total_chunks}")

        if not yes:
            if not click.confirm("\nПродолжить удаление?"):
                click.echo("Удаление отменено")
                return 0

        # Удалить директорию
        success = file_manager.delete_directory(page_id, parent_dir)

        if success:
            click.echo("\n✓ Удаление завершено успешно")
            return 0
        else:
            click.echo("\n✗ Ошибка удаления", err=True)
            return 1

    except Exception as e:
        click.echo(f"✗ Ошибка: {e}", err=True)
        return 1


if __name__ == '__main__':
    cli()
