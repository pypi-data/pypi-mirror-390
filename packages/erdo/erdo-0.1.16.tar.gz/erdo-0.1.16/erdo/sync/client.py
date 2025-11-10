"""API client for syncing agents to the backend."""

import json
from typing import Any, Dict, Optional

import requests

from ..config import get_config
from .extractor import TemplateStringEncoder


class SyncClient:
    """Client for syncing agents to the Erdo backend."""

    def __init__(
        self, endpoint: Optional[str] = None, auth_token: Optional[str] = None
    ):
        """Initialize the sync client.

        Args:
            endpoint: API endpoint URL. If not provided, uses config.
            auth_token: Authentication token. If not provided, uses config.
        """
        config = get_config()
        self.endpoint = endpoint or config.endpoint
        self.auth_token = auth_token or config.auth_token

    def upsert_bot(self, bot_request: Dict[str, Any]) -> str:
        """Upsert a bot to the backend.

        Args:
            bot_request: The bot request data containing bot info, steps, etc.

        Returns:
            The bot ID of the upserted bot.

        Raises:
            requests.RequestException: If the API request fails.
            ValueError: If the response is invalid.
        """
        url = f"{self.endpoint}/bot/upsert"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

        # Use custom encoder to handle special types
        json_data = json.dumps(bot_request, cls=TemplateStringEncoder)
        response = requests.post(url, data=json_data, headers=headers)

        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_details = response.text
                error_msg = f"{error_msg}: {error_details}"
            except Exception:
                pass
            raise requests.RequestException(error_msg)

        try:
            result = response.json()
            return result.get("bot_id", "")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode response: {e}")

    def sync_test(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync a test to the backend.

        Args:
            test_data: The test data to sync.

        Returns:
            The response from the API.

        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"{self.endpoint}/test/sync"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
        }

        response = requests.post(url, json=test_data, headers=headers)

        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_details = response.text
                error_msg = f"{error_msg}: {error_details}"
            except Exception:
                pass
            raise requests.RequestException(error_msg)

        return response.json()
