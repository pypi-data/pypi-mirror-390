"""Tests for database module."""
import pytest
import tempfile
import os
from pathlib import Path
from sber_tunnel.db.schema import Database


def test_database_init():
    """Test database initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")

        with Database(db_path) as db:
            db.init_schema()

            # Test adding file
            success = db.add_file(
                file_id="test-1",
                path="test.txt",
                size=100,
                mtime=123456.0,
                hash="abc123"
            )
            assert success

            # Test getting file
            file_data = db.get_file("test-1")
            assert file_data is not None
            assert file_data['path'] == "test.txt"
            assert file_data['size'] == 100


def test_directory_operations():
    """Test directory operations."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")

        with Database(db_path) as db:
            db.init_schema()

            # Test adding directory
            dir_id = db.add_dir("/test/dir", "page-123")
            assert dir_id is not None

            # Test getting directory
            dir_data = db.get_dir(dir_id)
            assert dir_data is not None
            assert dir_data['local_path'] == "/test/dir"
            assert dir_data['page_id'] == "page-123"


def test_operations_queue():
    """Test operations queue."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")

        with Database(db_path) as db:
            db.init_schema()

            # Add operation
            op_id = db.add_operation("create", "file-1", {"path": "test.txt"})
            assert op_id is not None

            # Get pending operations
            ops = db.get_pending_operations()
            assert len(ops) == 1
            assert ops[0]['type'] == "create"
            assert ops[0]['state'] == "pending"

            # Mark as completed
            success = db.mark_operation_completed(op_id)
            assert success

            # Check no more pending
            ops = db.get_pending_operations()
            assert len(ops) == 0
