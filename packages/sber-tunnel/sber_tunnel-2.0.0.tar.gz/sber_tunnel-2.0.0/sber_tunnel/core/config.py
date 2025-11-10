"""Configuration management."""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Configuration manager for sber-tunnel."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration.

        Args:
            config_dir: Optional custom config directory
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use current working directory instead of home directory
            self.config_dir = Path.cwd() / '.sber-tunnel'

        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / 'config.json'
        self._config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)

    def save(self):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value

    def is_configured(self) -> bool:
        """Check if basic configuration exists.

        Returns:
            True if configured, False otherwise
        """
        required_keys = ['base_url', 'username', 'password']
        return all(key in self._config for key in required_keys)

    def get_db_path(self) -> str:
        """Get database path.

        Returns:
            Path to database file
        """
        return str(self.config_dir / 'sber-tunnel.db')
