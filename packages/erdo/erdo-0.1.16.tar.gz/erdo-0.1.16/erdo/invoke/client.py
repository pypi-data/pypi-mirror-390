"""API client for invoking bots via the backend orchestrator."""

import json
from typing import Any, Dict, Generator, List, Optional, Union

import requests

from ..config import get_config


class SSEClient:
    """Client for Server-Sent Events streaming."""

    def __init__(self, response: requests.Response):
        """Initialize SSE client with a response object."""
        self.response = response
        self.response.encoding = "utf-8"

    def events(self) -> Generator[Dict[str, Any], None, None]:
        """Yield events from the SSE stream."""
        for line in self.response.iter_lines():
            if line:
                line = line.decode("utf-8") if isinstance(line, bytes) else line
                if line.startswith("data: "):
                    data = line[6:]  # Remove 'data: ' prefix
                    if data.strip():
                        try:
                            yield json.loads(data)
                        except json.JSONDecodeError:
                            # Some events might not be JSON
                            yield {"raw": data}


class InvokeClient:
    """Client for invoking bots via the Erdo backend."""

    def __init__(
        self, endpoint: Optional[str] = None, auth_token: Optional[str] = None
    ):
        """Initialize the invoke client.

        Args:
            endpoint: API endpoint URL. If not provided, uses config.
            auth_token: Authentication token. If not provided, uses config.
        """
        config = get_config()
        self.endpoint = endpoint or config.endpoint
        self.auth_token = auth_token or config.auth_token

    def invoke_bot(
        self,
        bot_identifier: str,
        messages: Optional[List[Dict[str, str]]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        dataset_slugs: Optional[list] = None,
        mode: Optional[Union[str, Dict[str, Any]]] = None,
        manual_mocks: Optional[Dict[str, Dict[str, Any]]] = None,
        stream: bool = False,
    ) -> Union[SSEClient, Dict[str, Any]]:
        """Invoke a bot via the backend orchestrator.

        Args:
            bot_identifier: Bot ID or key (e.g., "erdo.data-analyzer")
            messages: Messages in format [{"role": "user", "content": "..."}]
            parameters: Parameters to pass to the bot
            dataset_slugs: Optional dataset slugs to include
            mode: Invocation mode - string: "live|replay|manual" OR dict: {"mode": "replay", "refresh": true}
            manual_mocks: Manual mock responses for mode="manual" (step_path -> mock response)
            stream: Whether to return SSE client for streaming (default: False)

        Returns:
            SSEClient for streaming or final result dict for non-streaming

        Raises:
            requests.RequestException: If the API request fails.
        """
        url = f"{self.endpoint}/bots/{bot_identifier}/invoke"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",  # Endpoint always returns SSE
        }

        # Build invoke parameters
        invoke_params: Dict[str, Any] = {}

        # Add messages if provided
        if messages:
            invoke_params["messages"] = messages

        # Add parameters if provided
        if parameters:
            invoke_params["parameters"] = parameters

        # Add dataset slugs if provided
        if dataset_slugs:
            invoke_params["dataset_slugs"] = dataset_slugs

        # Add mode if provided (live/replay/manual)
        if mode:
            invoke_params["mode"] = mode

        # Add manual mocks if provided (for manual mode)
        if manual_mocks:
            invoke_params["manual_mocks"] = manual_mocks

        # Make the request - always stream to handle SSE
        response = requests.post(url, json=invoke_params, headers=headers, stream=True)

        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_details = response.text
                error_msg = f"{error_msg}: {error_details}"
            except Exception:
                pass
            raise requests.RequestException(error_msg)

        sse_client = SSEClient(response)

        if stream:
            # Return SSE client for streaming
            return sse_client
        else:
            # Consume all events and return final result
            events: list[Dict[str, Any]] = []
            final_result: Dict[str, Any] = {}

            for event in sse_client.events():
                events.append(event)

                # Look for completion or result events
                if "payload" in event:
                    payload = event["payload"]
                    if isinstance(payload, dict):
                        if "result" in payload:
                            final_result = payload["result"]
                        elif "invocation_id" in payload:
                            final_result["invocation_id"] = payload["invocation_id"]
                        elif "bot_name" in payload:
                            final_result["bot_name"] = payload["bot_name"]

                # Check for invocation completed
                if event.get("type") == "invocation_completed":
                    if "result" in event:
                        final_result = event["result"]
                    break

            # Return collected data
            return {
                "events": events,
                "result": final_result,
                "event_count": len(events),
            }

    def invoke_bot_from_thread(
        self,
        bot_identifier: str,
        thread_id: str,
        message: str,
        parameters: Optional[Dict[str, Any]] = None,
        stream: bool = False,
    ) -> Union[SSEClient, Dict[str, Any]]:
        """Invoke a bot from within a thread context.

        Args:
            bot_identifier: Bot ID or key
            thread_id: Thread ID to invoke from
            message: User message
            parameters: Additional parameters
            stream: Whether to return SSE client for streaming (default: False)

        Returns:
            SSEClient for streaming or final result dict
        """
        url = f"{self.endpoint}/bots/{bot_identifier}/invoke-from-thread"
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",  # Endpoint always returns SSE
        }

        invoke_params = {
            "thread_id": thread_id,
            "message": message,
            "parameters": parameters or {},
        }

        # Make the request - always stream to handle SSE
        response = requests.post(url, json=invoke_params, headers=headers, stream=True)

        if response.status_code != 200:
            error_msg = f"API request failed with status {response.status_code}"
            try:
                error_details = response.text
                error_msg = f"{error_msg}: {error_details}"
            except Exception:
                pass
            raise requests.RequestException(error_msg)

        sse_client = SSEClient(response)

        if stream:
            # Return SSE client for streaming
            return sse_client
        else:
            # Consume all events and return final result
            events: list[Dict[str, Any]] = []
            final_result: Dict[str, Any] = {}

            for event in sse_client.events():
                events.append(event)

                # Look for completion or result events
                if "payload" in event:
                    payload = event["payload"]
                    if isinstance(payload, dict):
                        if "result" in payload:
                            final_result = payload["result"]
                        elif "invocation_id" in payload:
                            final_result["invocation_id"] = payload["invocation_id"]

                # Check for invocation completed
                if event.get("type") == "invocation_completed":
                    if "result" in event:
                        final_result = event["result"]
                    break

            # Return collected data
            return {
                "events": events,
                "result": final_result,
                "event_count": len(events),
            }
