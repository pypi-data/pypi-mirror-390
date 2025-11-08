"""Tests for configuration management."""
import pytest
import tempfile
import os
from pathlib import Path
from sber_tunnel.core.config import Config


def test_config_in_current_directory():
    """Test that config is created in current directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Create config
            config = Config()

            # Verify config directory is in current directory
            expected_dir = (Path(tmpdir) / '.sber-tunnel').resolve()
            assert config.config_dir.resolve() == expected_dir
            assert config.config_dir.exists()

            # Verify config file path
            expected_config = (expected_dir / 'config.json').resolve()
            assert config.config_path.resolve() == expected_config

        finally:
            os.chdir(original_cwd)


def test_config_custom_directory():
    """Test that custom config directory works."""
    with tempfile.TemporaryDirectory() as tmpdir:
        custom_dir = Path(tmpdir) / 'custom_config'

        # Create config with custom directory
        config = Config(config_dir=custom_dir)

        # Verify custom directory is used
        assert config.config_dir == custom_dir
        assert config.config_dir.exists()


def test_config_save_and_load():
    """Test saving and loading configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            # Create and save config
            config1 = Config()
            config1.set('test_key', 'test_value')
            config1.set('page_id', '123456')
            config1.save()

            # Load config in new instance
            config2 = Config()
            assert config2.get('test_key') == 'test_value'
            assert config2.get('page_id') == '123456'

        finally:
            os.chdir(original_cwd)


def test_config_db_path():
    """Test database path is in config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            config = Config()
            db_path = Path(config.get_db_path()).resolve()

            # Verify db path is in config directory
            expected_db = (Path(tmpdir) / '.sber-tunnel' / 'sber-tunnel.db').resolve()
            assert db_path == expected_db

        finally:
            os.chdir(original_cwd)


def test_config_is_configured():
    """Test is_configured method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)

            config = Config()

            # Not configured initially
            assert not config.is_configured()

            # Set required keys
            config.set('base_url', 'https://example.com')
            config.set('username', 'user')
            config.set('password', 'pass')
            config.set('page_id', '123')

            # Now configured
            assert config.is_configured()

        finally:
            os.chdir(original_cwd)


def test_multiple_projects_different_configs():
    """Test that different directories have different configs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create two project directories
        project1 = Path(tmpdir) / 'project1'
        project2 = Path(tmpdir) / 'project2'
        project1.mkdir()
        project2.mkdir()

        original_cwd = os.getcwd()
        try:
            # Configure project 1
            os.chdir(project1)
            config1 = Config()
            config1.set('project_name', 'project1')
            config1.save()

            # Configure project 2
            os.chdir(project2)
            config2 = Config()
            config2.set('project_name', 'project2')
            config2.save()

            # Verify they're different
            os.chdir(project1)
            config1_reload = Config()
            assert config1_reload.get('project_name') == 'project1'

            os.chdir(project2)
            config2_reload = Config()
            assert config2_reload.get('project_name') == 'project2'

        finally:
            os.chdir(original_cwd)
