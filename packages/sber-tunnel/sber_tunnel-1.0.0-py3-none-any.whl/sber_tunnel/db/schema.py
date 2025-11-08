"""Database schema and operations."""
import sqlite3
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from datetime import datetime


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str):
        """Initialize database connection."""
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def disconnect(self):
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def init_schema(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()

        # Files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                path TEXT NOT NULL UNIQUE,
                size INTEGER NOT NULL,
                mtime REAL NOT NULL,
                hash TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                deleted INTEGER NOT NULL DEFAULT 0,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)

        # Directories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dirs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                local_path TEXT NOT NULL UNIQUE,
                page_id TEXT NOT NULL,
                last_sync_at REAL,
                created_at REAL NOT NULL
            )
        """)

        # Operations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                file_id TEXT,
                payload TEXT,
                state TEXT NOT NULL DEFAULT 'pending',
                created_at REAL NOT NULL,
                processed_at REAL,
                FOREIGN KEY(file_id) REFERENCES files(id)
            )
        """)

        # Config table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        self.conn.commit()

    # Files operations
    def add_file(self, file_id: str, path: str, size: int, mtime: float,
                 hash: str, version: int = 1) -> bool:
        """Add or update file record."""
        cursor = self.conn.cursor()
        now = datetime.now().timestamp()

        try:
            cursor.execute("""
                INSERT INTO files (id, path, size, mtime, hash, version, deleted, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    path = excluded.path,
                    size = excluded.size,
                    mtime = excluded.mtime,
                    hash = excluded.hash,
                    version = excluded.version,
                    updated_at = excluded.updated_at
            """, (file_id, path, size, mtime, hash, version, now, now))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding file: {e}")
            return False

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file by id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_file_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Get file by path."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE path = ?", (path,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_files(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Get all files."""
        cursor = self.conn.cursor()
        if include_deleted:
            cursor.execute("SELECT * FROM files")
        else:
            cursor.execute("SELECT * FROM files WHERE deleted = 0")
        return [dict(row) for row in cursor.fetchall()]

    def mark_file_deleted(self, file_id: str) -> bool:
        """Mark file as deleted."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE files SET deleted = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.now().timestamp(), file_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error marking file as deleted: {e}")
            return False

    # Directory operations
    def add_dir(self, local_path: str, page_id: str) -> Optional[int]:
        """Add tracked directory."""
        cursor = self.conn.cursor()
        now = datetime.now().timestamp()

        try:
            cursor.execute("""
                INSERT INTO dirs (local_path, page_id, created_at)
                VALUES (?, ?, ?)
            """, (local_path, page_id, now))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding directory: {e}")
            return None

    def get_dir(self, dir_id: int) -> Optional[Dict[str, Any]]:
        """Get directory by id."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM dirs WHERE id = ?", (dir_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_dirs(self) -> List[Dict[str, Any]]:
        """Get all tracked directories."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM dirs")
        return [dict(row) for row in cursor.fetchall()]

    def update_dir_sync_time(self, dir_id: int) -> bool:
        """Update last sync time for directory."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE dirs SET last_sync_at = ?
                WHERE id = ?
            """, (datetime.now().timestamp(), dir_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating sync time: {e}")
            return False

    # Operations
    def add_operation(self, op_type: str, file_id: Optional[str] = None,
                     payload: Optional[Dict] = None) -> Optional[int]:
        """Add operation to queue."""
        cursor = self.conn.cursor()
        now = datetime.now().timestamp()
        payload_str = json.dumps(payload) if payload else None

        try:
            cursor.execute("""
                INSERT INTO ops (type, file_id, payload, state, created_at)
                VALUES (?, ?, ?, 'pending', ?)
            """, (op_type, file_id, payload_str, now))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding operation: {e}")
            return None

    def get_pending_operations(self) -> List[Dict[str, Any]]:
        """Get all pending operations."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM ops
            WHERE state = 'pending'
            ORDER BY created_at ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def mark_operation_completed(self, op_id: int) -> bool:
        """Mark operation as completed."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE ops SET state = 'completed', processed_at = ?
                WHERE id = ?
            """, (datetime.now().timestamp(), op_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error marking operation completed: {e}")
            return False

    def mark_operation_failed(self, op_id: int) -> bool:
        """Mark operation as failed."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                UPDATE ops SET state = 'failed', processed_at = ?
                WHERE id = ?
            """, (datetime.now().timestamp(), op_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error marking operation failed: {e}")
            return False

    # Config operations
    def set_config(self, key: str, value: str) -> bool:
        """Set configuration value."""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO config (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, value))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error setting config: {e}")
            return False

    def get_config(self, key: str) -> Optional[str]:
        """Get configuration value."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None
