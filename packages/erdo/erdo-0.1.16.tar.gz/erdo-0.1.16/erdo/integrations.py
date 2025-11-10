# Integration base classes for defining integration configurations in Python
"""
Integration configuration framework for defining integration configs alongside agents.

This module provides base classes for defining integration configurations in Python,
which can then be synced to the backend alongside agents.
"""

from typing import Any, Dict, Optional

from ._generated.types import IntegrationConfig, IntegrationDefinition


# Helper function to create integration configurations
def create_integration_config(**kwargs) -> IntegrationConfig:
    """Create an IntegrationConfig with the provided parameters."""
    # Extract metadata
    source = kwargs.pop("source", "python")
    file_path = kwargs.pop("file_path", None)

    # Create IntegrationDefinition with remaining parameters
    definition = IntegrationDefinition(**kwargs)

    return IntegrationConfig(definition=definition, source=source, file_path=file_path)


# Base class that acts like IntegrationConfig but handles initialization better
class IntegrationConfigClass:
    """Base class for integration configurations using auto-generated types."""

    def __init__(self, **kwargs):
        """Initialize with integration definition parameters."""
        # Extract metadata
        self._source = kwargs.pop("source", "python")
        self._file_path = kwargs.pop("file_path", None)

        # Create the definition with remaining kwargs
        self._definition = IntegrationDefinition(**kwargs)

        # Create the actual IntegrationConfig instance
        self._config = IntegrationConfig(
            definition=self._definition, source=self._source, file_path=self._file_path
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for syncing to backend."""
        return self._config.to_dict()

    @property
    def definition(self) -> IntegrationDefinition:
        """Access the underlying definition."""
        return self._definition

    @property
    def config(self) -> IntegrationConfig:
        """Access the underlying IntegrationConfig."""
        return self._config


# Helper functions for common credential schemas
def oauth_credential_schema() -> Dict[str, Any]:
    """Helper to create standard OAuth credential schema"""
    return {
        "access_token": {
            "type": "string",
            "description": "OAuth access token",
            "required": True,
            "source": "integration_credentials",
        },
        "refresh_token": {
            "type": "string",
            "description": "OAuth refresh token",
            "required": False,
            "source": "integration_credentials",
        },
    }


def database_credential_schema() -> Dict[str, Any]:
    """Helper to create standard database credential schema"""
    return {
        "host": {
            "type": "string",
            "description": "Database host",
            "required": True,
            "source": "integration_credentials",
        },
        "port": {
            "type": "string",
            "description": "Database port",
            "required": True,
            "source": "integration_credentials",
        },
        "database": {
            "type": "string",
            "description": "Database name",
            "required": True,
            "source": "integration_credentials",
        },
        "username": {
            "type": "string",
            "description": "Database username",
            "required": True,
            "source": "integration_credentials",
        },
        "password": {
            "type": "string",
            "description": "Database password",
            "required": True,
            "source": "integration_credentials",
        },
    }


def api_key_credential_schema(
    key_name: str = "api_key", header_name: Optional[str] = None
) -> Dict[str, Any]:
    """Helper to create standard API key credential schema"""
    schema = {
        key_name: {
            "type": "string",
            "description": "API Key for authentication",
            "required": True,
            "source": "integration_credentials",
        }
    }

    if header_name:
        schema[key_name]["header"] = header_name

    return schema
