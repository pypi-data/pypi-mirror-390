"""Main sync functionality for syncing agents to the backend."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .client import SyncClient
from .extractor import (
    extract_agent_from_instance,
    extract_agents_from_file,
)


@dataclass
class SyncResult:
    """Result of a sync operation."""

    success: bool
    bot_id: Optional[str] = None
    bot_name: Optional[str] = None
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return f"✅ Successfully synced {self.bot_name} (ID: {self.bot_id})"
        else:
            return f"❌ Failed to sync {self.bot_name}: {self.error}"


class Sync:
    """Main sync class for syncing agents."""

    def __init__(
        self,
        agent: Optional[Any] = None,
        endpoint: Optional[str] = None,
        auth_token: Optional[str] = None,
    ):
        """Initialize sync and optionally sync an agent immediately.

        Args:
            agent: Optional Agent instance to sync immediately
            endpoint: API endpoint URL. If not provided, uses config.
            auth_token: Authentication token. If not provided, uses config.
        """
        self.client = SyncClient(endpoint=endpoint, auth_token=auth_token)
        self.result = None

        # If an agent is provided, sync it immediately
        if agent:
            self.result = self.sync_agent(agent)

    def sync_agent(
        self, agent: Any, source_file_path: Optional[str] = None
    ) -> SyncResult:
        """Sync a single agent to the backend.

        Args:
            agent: Agent instance to sync
            source_file_path: Optional path to the source file for better extraction

        Returns:
            SyncResult with the outcome of the sync operation
        """
        try:
            # Extract agent data
            agent_data = extract_agent_from_instance(agent, source_file_path)

            # Convert to API format
            bot_request = self._convert_to_api_format(agent_data)

            # Send to backend
            bot_id = self.client.upsert_bot(bot_request)

            return SyncResult(success=True, bot_id=bot_id, bot_name=agent.name)

        except Exception as e:
            return SyncResult(
                success=False, bot_name=getattr(agent, "name", "Unknown"), error=str(e)
            )

    @classmethod
    def from_file(
        cls,
        file_path: str,
        endpoint: Optional[str] = None,
        auth_token: Optional[str] = None,
    ) -> List[SyncResult]:
        """Sync agents from a Python file.

        Args:
            file_path: Path to the Python file containing agents
            endpoint: API endpoint URL. If not provided, uses config.
            auth_token: Authentication token. If not provided, uses config.

        Returns:
            List of SyncResult objects for each agent found
        """
        sync = cls(endpoint=endpoint, auth_token=auth_token)

        try:
            # Extract agents from file
            agent_data = extract_agents_from_file(file_path)

            # Handle single agent or list of agents
            if isinstance(agent_data, list):
                results = []
                for data in agent_data:
                    result = sync._sync_agent_data(data)
                    results.append(result)
                return results
            else:
                result = sync._sync_agent_data(agent_data)
                return [result]

        except Exception as e:
            return [
                SyncResult(
                    success=False, error=f"Failed to extract agents from file: {e}"
                )
            ]

    @classmethod
    def from_directory(
        cls,
        directory_path: str = ".",
        endpoint: Optional[str] = None,
        auth_token: Optional[str] = None,
    ) -> List[SyncResult]:
        """Sync all agents from a directory.

        Args:
            directory_path: Path to directory containing agent files (default: current directory)
            endpoint: API endpoint URL. If not provided, uses config.
            auth_token: Authentication token. If not provided, uses config.

        Returns:
            List of SyncResult objects for each agent found
        """
        results = []

        directory = Path(directory_path)

        # Check for __init__.py with agents first
        init_file = directory / "__init__.py"
        if init_file.exists():
            try:
                init_results = cls.from_file(
                    str(init_file), endpoint=endpoint, auth_token=auth_token
                )
                if init_results:
                    return init_results
            except Exception:
                pass  # Fall back to directory scan

        # Scan directory for agent files
        for py_file in directory.glob("**/*.py"):
            # Skip common non-agent files
            if any(
                skip in str(py_file)
                for skip in ["__pycache__", "test_", "_test.py", ".venv", "venv"]
            ):
                continue

            try:
                # Check if file has agents
                with open(py_file, "r") as f:
                    content = f.read()
                    if "agents = [" not in content:
                        continue

                # Try to sync agents from this file
                file_results = cls.from_file(
                    str(py_file), endpoint=endpoint, auth_token=auth_token
                )
                results.extend(file_results)

            except Exception as e:
                results.append(
                    SyncResult(success=False, error=f"Failed to process {py_file}: {e}")
                )

        return results

    def _sync_agent_data(self, agent_data: Dict[str, Any]) -> SyncResult:
        """Sync extracted agent data to the backend.

        Args:
            agent_data: Extracted agent data dictionary

        Returns:
            SyncResult with the outcome of the sync operation
        """
        try:
            # Convert to API format
            bot_request = self._convert_to_api_format(agent_data)

            # Send to backend
            bot_id = self.client.upsert_bot(bot_request)

            return SyncResult(
                success=True, bot_id=bot_id, bot_name=agent_data["bot"]["name"]
            )

        except Exception as e:
            return SyncResult(
                success=False,
                bot_name=agent_data.get("bot", {}).get("name", "Unknown"),
                error=str(e),
            )

    def _convert_to_api_format(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert extracted agent data to API format.

        Args:
            agent_data: Extracted agent data

        Returns:
            Bot request in API format
        """
        # Override source to "user" as per Go implementation
        bot_data = agent_data["bot"].copy()
        bot_data["source"] = "user"

        # Convert steps to API format
        api_steps = []
        for step_with_handlers in agent_data.get("steps", []):
            api_step = self._convert_step_to_api(step_with_handlers)
            api_steps.append(api_step)

        # Build the API request
        # Convert parameter_definitions to dicts if they're objects
        param_defs = agent_data.get("parameter_definitions", [])
        if param_defs and hasattr(param_defs[0], "to_dict"):
            param_defs = [
                pd.to_dict() if hasattr(pd, "to_dict") else pd for pd in param_defs
            ]

        bot_request = {
            "bot": bot_data,
            "steps": api_steps,
            "source": "user",
            "parameter_definitions": param_defs,
        }

        # Include action result schemas if present
        if "action_result_schemas" in agent_data:
            bot_request["action_result_schemas"] = agent_data["action_result_schemas"]

        return bot_request

    def _convert_step_to_api(
        self, step_with_handlers: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Convert StepWithHandlers to API format.

        Args:
            step_with_handlers: Step with handlers dictionary

        Returns:
            Step in API format
        """
        # Ensure parameters is not None
        step = step_with_handlers["step"].copy()
        if step.get("parameters") is None:
            step["parameters"] = {}

        # Convert result handlers
        api_handlers = []
        for handler in step_with_handlers.get("result_handlers", []):
            api_handler = handler.copy()

            # Convert nested steps in handler
            if "steps" in api_handler:
                api_handler_steps = []
                for nested_step in api_handler["steps"]:
                    api_nested = self._convert_step_to_api(nested_step)
                    api_handler_steps.append(api_nested)
                api_handler["steps"] = api_handler_steps

            api_handlers.append(api_handler)

        return {"step": step, "result_handlers": api_handlers}


# Convenience functions
def sync_agent(
    agent: Any, source_file_path: Optional[str] = None, **kwargs
) -> SyncResult:
    """Sync a single agent to the backend.

    Args:
        agent: Agent instance to sync
        source_file_path: Optional path to the source file
        **kwargs: Additional arguments (endpoint, auth_token)

    Returns:
        SyncResult with the outcome of the sync operation
    """
    sync = Sync(endpoint=kwargs.get("endpoint"), auth_token=kwargs.get("auth_token"))
    return sync.sync_agent(agent, source_file_path)


def sync_agents_from_file(file_path: str, **kwargs) -> List[SyncResult]:
    """Sync agents from a Python file.

    Args:
        file_path: Path to the Python file containing agents
        **kwargs: Additional arguments (endpoint, auth_token)

    Returns:
        List of SyncResult objects
    """
    return Sync.from_file(file_path, **kwargs)


def sync_agents_from_directory(directory_path: str = ".", **kwargs) -> List[SyncResult]:
    """Sync all agents from a directory.

    Args:
        directory_path: Path to directory containing agent files
        **kwargs: Additional arguments (endpoint, auth_token)

    Returns:
        List of SyncResult objects
    """
    return Sync.from_directory(directory_path, **kwargs)
