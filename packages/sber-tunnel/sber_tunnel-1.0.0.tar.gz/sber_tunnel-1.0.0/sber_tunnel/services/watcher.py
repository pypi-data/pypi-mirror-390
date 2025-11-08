"""File watcher service for monitoring directory changes."""
import time
from pathlib import Path
from typing import List, Dict, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from ..db.schema import Database


class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system events."""

    def __init__(self, db: Database, watched_dir: str, on_change: Callable = None):
        """Initialize handler.

        Args:
            db: Database instance
            watched_dir: Directory being watched
            on_change: Optional callback when changes occur
        """
        self.db = db
        self.watched_dir = Path(watched_dir)
        self.on_change = on_change

    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored.

        Args:
            path: File path

        Returns:
            True if should be ignored
        """
        # Ignore hidden files and directories
        if any(part.startswith('.') for part in path.parts):
            return True

        # Ignore temporary files
        if path.name.endswith('~') or path.name.startswith('~'):
            return True

        return False

    def _add_operation(self, op_type: str, file_path: Path):
        """Add operation to database.

        Args:
            op_type: Operation type (create, modify, delete)
            file_path: Path to file
        """
        if self._should_ignore(file_path):
            return

        relative_path = str(file_path.relative_to(self.watched_dir))

        # Get or create file record
        db_file = self.db.get_file_by_path(relative_path)

        if db_file:
            file_id = db_file['id']
        else:
            # Create placeholder file record
            import uuid
            file_id = str(uuid.uuid4())

        # Add operation
        self.db.add_operation(
            op_type=op_type,
            file_id=file_id,
            payload={'path': relative_path}
        )

        if self.on_change:
            self.on_change(op_type, relative_path)

    def on_created(self, event: FileSystemEvent):
        """Handle file creation.

        Args:
            event: File system event
        """
        if not event.is_directory:
            self._add_operation('create', Path(event.src_path))

    def on_modified(self, event: FileSystemEvent):
        """Handle file modification.

        Args:
            event: File system event
        """
        if not event.is_directory:
            self._add_operation('modify', Path(event.src_path))

    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion.

        Args:
            event: File system event
        """
        if not event.is_directory:
            self._add_operation('delete', Path(event.src_path))


class FileWatcher:
    """Service for watching file system changes."""

    def __init__(self, db: Database):
        """Initialize file watcher.

        Args:
            db: Database instance
        """
        self.db = db
        self.observers: Dict[str, Observer] = {}

    def start_watching(self, directory: str, on_change: Callable = None):
        """Start watching a directory.

        Args:
            directory: Directory to watch
            on_change: Optional callback when changes occur
        """
        if directory in self.observers:
            print(f"Already watching: {directory}")
            return

        event_handler = FileChangeHandler(self.db, directory, on_change)
        observer = Observer()
        observer.schedule(event_handler, directory, recursive=True)
        observer.start()

        self.observers[directory] = observer
        print(f"Started watching: {directory}")

    def stop_watching(self, directory: str):
        """Stop watching a directory.

        Args:
            directory: Directory to stop watching
        """
        if directory not in self.observers:
            return

        observer = self.observers[directory]
        observer.stop()
        observer.join()

        del self.observers[directory]
        print(f"Stopped watching: {directory}")

    def stop_all(self):
        """Stop watching all directories."""
        for directory in list(self.observers.keys()):
            self.stop_watching(directory)
