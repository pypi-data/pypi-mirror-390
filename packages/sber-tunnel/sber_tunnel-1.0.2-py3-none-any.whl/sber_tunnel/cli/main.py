"""Main CLI interface for sber-tunnel."""
import click
import json
from pathlib import Path
from ..services.confluence import ConfluenceService
from ..db.schema import Database
from ..core.config import Config


@click.group()
def cli():
    """Sber-tunnel - File synchronization via Confluence."""
    pass


@cli.command()
def init():
    """Initialize sber-tunnel configuration."""
    click.echo("=== Sber-tunnel Initialization ===\n")

    # Collect configuration
    base_url = click.prompt("Confluence base URL")
    username = click.prompt("Username")
    password = click.prompt("Password", hide_input=True)
    page_id = click.prompt("Page ID")

    # Optional certificate
    use_cert = click.confirm("Use p12 certificate?", default=False)
    cert_path = None
    cert_password = None

    if use_cert:
        cert_path = click.prompt("Path to p12 certificate")
        cert_password = click.prompt("Certificate password", hide_input=True)

    click.echo("\nValidating credentials...")

    # Test connection and permissions
    try:
        confluence = ConfluenceService(
            url=base_url,
            username=username,
            password=password,
            cert_path=cert_path,
            cert_password=cert_password
        )

        if not confluence.check_permissions(page_id):
            click.echo("Error: No permissions to access page or add attachments", err=True)
            return

        click.echo("Credentials validated successfully!")

        # Save configuration
        config = Config()
        config.set('base_url', base_url)
        config.set('username', username)
        config.set('password', password)
        config.set('page_id', page_id)

        if cert_path:
            config.set('cert_path', cert_path)
            config.set('cert_password', cert_password)

        config.save()

        # Initialize database
        db_path = config.get_db_path()
        with Database(db_path) as db:
            db.init_schema()

        click.echo(f"\nConfiguration saved to {config.config_path}")

        # Check if manifest exists on the page
        click.echo("\nChecking for existing files on Confluence page...")
        manifest = confluence.download_manifest(page_id)

        if manifest and manifest.files:
            click.echo(f"Found {len(manifest.files)} files on Confluence page.")
            if click.confirm("Download existing files to local directory?", default=True):
                local_dir = click.prompt("Local directory path", type=click.Path())
                local_path = Path(local_dir).resolve()

                if not local_path.exists():
                    local_path.mkdir(parents=True, exist_ok=True)

                with Database(db_path) as db:
                    dir_id = db.add_dir(str(local_path), page_id)

                    if dir_id:
                        from ..services.sync import SyncService
                        sync_service = SyncService(confluence, db)
                        click.echo(f"\nSyncing files to {local_path}...")
                        sync_service.sync_directory(dir_id, local_path, page_id)
                        click.echo("Sync completed!")

        click.echo("\nYou can now use:")
        click.echo("  - sber-tunnel add <directory>  to add a directory to sync")
        click.echo("  - sber-tunnel start            to start the sync service")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False))
@click.option('--sync', is_flag=True, default=True, help='Sync immediately after adding')
def add(directory, sync):
    """Add directory to synchronization."""
    config = Config()
    if not config.is_configured():
        click.echo("Error: Not initialized. Run 'sber-tunnel init' first.", err=True)
        return

    directory = Path(directory).resolve()

    # Add to database
    db_path = config.get_db_path()
    with Database(db_path) as db:
        page_id = config.get('page_id')
        dir_id = db.add_dir(str(directory), page_id)

        if dir_id:
            click.echo(f"Added directory: {directory}")
            click.echo(f"Directory ID: {dir_id}")

            if sync:
                click.echo("\nSyncing directory with Confluence...")
                confluence = ConfluenceService(
                    url=config.get('base_url'),
                    username=config.get('username'),
                    password=config.get('password'),
                    cert_path=config.get('cert_path'),
                    cert_password=config.get('cert_password')
                )

                from ..services.sync import SyncService
                sync_service = SyncService(confluence, db)
                success = sync_service.sync_directory(dir_id, directory, page_id)

                if success:
                    click.echo("Sync completed successfully")
                else:
                    click.echo("Sync failed", err=True)
        else:
            click.echo("Error: Failed to add directory (may already exist)", err=True)


@cli.command()
@click.option('--daemon', is_flag=True, help='Run as daemon')
def start(daemon):
    """Start sync service and web UI."""
    config = Config()
    if not config.is_configured():
        click.echo("Error: Not initialized. Run 'sber-tunnel init' first.", err=True)
        return

    click.echo("Starting sber-tunnel service...")

    # Import here to avoid circular imports
    from ..api.server import start_server

    start_server(daemon=daemon)


@cli.command()
def stop():
    """Stop sync service."""
    click.echo("Stopping sber-tunnel service...")

    # Import here
    from ..api.server import stop_server

    stop_server()


@cli.command()
def sync():
    """Manually trigger synchronization."""
    config = Config()
    if not config.is_configured():
        click.echo("Error: Not initialized. Run 'sber-tunnel init' first.", err=True)
        return

    click.echo("Starting manual synchronization...")

    from ..services.sync import SyncService

    # Get configuration
    confluence = ConfluenceService(
        url=config.get('base_url'),
        username=config.get('username'),
        password=config.get('password'),
        cert_path=config.get('cert_path'),
        cert_password=config.get('cert_password')
    )

    db_path = config.get_db_path()
    with Database(db_path) as db:
        sync_service = SyncService(confluence, db)

        # Sync all directories
        dirs = db.get_all_dirs()
        for dir_info in dirs:
            click.echo(f"\nSyncing: {dir_info['local_path']}")
            success = sync_service.sync_directory(
                dir_info['id'],
                Path(dir_info['local_path']),
                dir_info['page_id']
            )

            if success:
                click.echo("Sync completed successfully")
            else:
                click.echo("Sync failed", err=True)


@cli.command()
def status():
    """Show status of tracked directories."""
    config = Config()
    if not config.is_configured():
        click.echo("Error: Not initialized. Run 'sber-tunnel init' first.", err=True)
        return

    db_path = config.get_db_path()
    with Database(db_path) as db:
        dirs = db.get_all_dirs()

        if not dirs:
            click.echo("No directories being tracked.")
            return

        click.echo("\n=== Tracked Directories ===\n")
        for dir_info in dirs:
            click.echo(f"ID: {dir_info['id']}")
            click.echo(f"Path: {dir_info['local_path']}")
            click.echo(f"Page ID: {dir_info['page_id']}")

            if dir_info['last_sync_at']:
                from datetime import datetime
                last_sync = datetime.fromtimestamp(dir_info['last_sync_at'])
                click.echo(f"Last sync: {last_sync}")
            else:
                click.echo("Last sync: Never")

            click.echo()


if __name__ == '__main__':
    cli()
