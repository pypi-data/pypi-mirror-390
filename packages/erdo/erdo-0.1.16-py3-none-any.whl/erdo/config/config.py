"""Configuration management for Erdo SDK."""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration manager for Erdo SDK."""

    def __init__(
        self, endpoint: Optional[str] = None, auth_token: Optional[str] = None
    ):
        """Initialize configuration.

        Args:
            endpoint: API endpoint URL. If not provided, will try environment variable or config file.
            auth_token: Authentication token. If not provided, will try environment variable or config file.
        """
        self._endpoint = endpoint
        self._auth_token = auth_token
        self._config_yaml = Path.home() / ".erdo" / "config.yaml"
        self._config_json = Path.home() / ".erdo" / "config.json"

    @property
    def endpoint(self) -> str:
        """Get the API endpoint."""
        if self._endpoint:
            return self._endpoint

        # Try environment variable
        env_endpoint = os.environ.get("ERDO_ENDPOINT")
        if env_endpoint:
            return env_endpoint

        # Try config file
        config = self._load_config_file()
        if config and "endpoint" in config:
            return config["endpoint"]

        raise ValueError(
            "No endpoint configured. Set ERDO_ENDPOINT environment variable or run 'erdo configure'"
        )

    @property
    def auth_token(self) -> str:
        """Get the authentication token."""
        if self._auth_token:
            return self._auth_token

        # Try environment variable
        env_token = os.environ.get("ERDO_AUTH_TOKEN")
        if env_token:
            return env_token

        # Try config file
        config = self._load_config_file()
        if config and "auth_token" in config:
            return config["auth_token"]

        raise ValueError(
            "No auth token configured. Set ERDO_AUTH_TOKEN environment variable or run 'erdo login'"
        )

    def _load_config_file(self) -> Optional[dict]:
        """Load configuration from file (supports both YAML and JSON)."""
        # Try YAML first (CLI default format)
        if self._config_yaml.exists():
            try:
                import yaml

                with open(self._config_yaml, "r") as f:
                    return yaml.safe_load(f)
            except Exception:
                try:
                    # Fallback to simple parsing if yaml not available
                    with open(self._config_yaml, "r") as f:
                        config = {}
                        for line in f:
                            if ": " in line:
                                key, value = line.strip().split(": ", 1)
                                config[key] = value
                        return config
                except Exception:
                    pass

        # Try JSON as fallback
        if self._config_json.exists():
            try:
                with open(self._config_json, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return None

    def save(self):
        """Save configuration to file (as JSON)."""
        self._config_json.parent.mkdir(parents=True, exist_ok=True)

        config = {}
        if self._endpoint:
            config["endpoint"] = self._endpoint
        if self._auth_token:
            config["auth_token"] = self._auth_token

        with open(self._config_json, "w") as f:
            json.dump(config, f, indent=2)

    def set_endpoint(self, endpoint: str):
        """Set the API endpoint."""
        self._endpoint = endpoint

    def set_auth_token(self, auth_token: str):
        """Set the authentication token."""
        self._auth_token = auth_token


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(endpoint: Optional[str] = None, auth_token: Optional[str] = None):
    """Set the global configuration.

    Args:
        endpoint: API endpoint URL
        auth_token: Authentication token
    """
    global _config
    _config = Config(endpoint=endpoint, auth_token=auth_token)
