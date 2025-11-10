"""Main invoke functionality for running agents via the orchestrator."""

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

from erdo._generated.types import Result

from .client import InvokeClient


@dataclass
class InvokeResult:
    """Result from a bot invocation.

    Follows the executor pattern with clean separation:
    - .result: The actual bot output (text/data from messages)
    - .messages: List of message objects with role/content
    - .events: Full list of all events (for debugging/analysis)
    - .steps: Information about executed steps
    """

    success: bool
    bot_id: Optional[str] = None
    invocation_id: Optional[str] = None
    result: Optional[Result] = None  # The actual bot result (types.Result object)
    messages: List[Dict[str, Any]] = field(default_factory=list)  # Message objects
    events: List[Dict[str, Any]] = field(default_factory=list)  # All raw events
    steps: List[Dict[str, Any]] = field(default_factory=list)  # Step execution info
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            result_preview = str(self.result)[:100] if self.result else "No result"
            return f"✅ Success (ID: {self.invocation_id})\nResult: {result_preview}"
        else:
            return f"❌ Failed: {self.error}"


class Invoke:
    """Main class for invoking agents."""

    def __init__(
        self,
        agent: Optional[Any] = None,
        parameters: Optional[Dict[str, Any]] = None,
        dataset_slugs: Optional[list] = None,
        endpoint: Optional[str] = None,
        auth_token: Optional[str] = None,
        stream: bool = False,
        print_events: bool = False,
    ):
        """Initialize and optionally invoke an agent immediately.

        Args:
            agent: Optional Agent instance to invoke immediately
            parameters: Parameters to pass to the agent
            dataset_slugs: Dataset slugs to include (e.g. ["my-dataset"] or ["org.my-dataset"])
            endpoint: API endpoint URL
            auth_token: Authentication token
            stream: Whether to stream events
            print_events: Whether to print events as they arrive
        """
        self.client = InvokeClient(endpoint=endpoint, auth_token=auth_token)
        self.print_events = print_events
        self.result = None

        # If an agent is provided, invoke it immediately
        if agent:
            bot_key = getattr(agent, "key", None)
            if not bot_key:
                raise ValueError("Agent must have a 'key' attribute for invocation")

            self.result = self.invoke_by_key(
                bot_key,
                parameters=parameters,
                dataset_slugs=dataset_slugs,
                stream=stream,
            )

    def invoke_agent(
        self,
        agent: Any,
        parameters: Optional[Dict[str, Any]] = None,
        dataset_slugs: Optional[list] = None,
        stream: bool = False,
    ) -> InvokeResult:
        """Invoke an agent instance.

        Args:
            agent: Agent instance with a 'key' attribute
            parameters: Parameters to pass to the agent
            dataset_slugs: Dataset slugs to include (e.g. ["my-dataset"] or ["org.my-dataset"])
            stream: Whether to stream events

        Returns:
            InvokeResult with the outcome
        """
        bot_key = getattr(agent, "key", None)
        if not bot_key:
            raise ValueError("Agent must have a 'key' attribute for invocation")

        return self.invoke_by_key(
            bot_key, parameters=parameters, dataset_slugs=dataset_slugs, stream=stream
        )

    def invoke_by_key(
        self,
        bot_key: str,
        messages: Optional[List[Dict[str, str]]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        dataset_slugs: Optional[list] = None,
        mode: Optional[Union[str, Dict[str, Any]]] = None,
        manual_mocks: Optional[Dict[str, Dict[str, Any]]] = None,
        stream: bool = False,
        output_format: str = "events",
        verbose: bool = False,
    ) -> InvokeResult:
        """Invoke a bot by its key.

        Args:
            bot_key: Bot key (e.g., "erdo.data-analyzer")
            messages: Messages in format [{"role": "user", "content": "..."}]
            parameters: Parameters to pass to the bot
            dataset_slugs: Dataset slugs to include (e.g. ["my-dataset"] or ["org.my-dataset"])
            mode: Invocation mode - string: "live|replay|manual" OR dict: {"mode": "replay", "refresh": true}
            manual_mocks: Manual mock responses for mode="manual" (step_path -> mock response)
            stream: Whether to stream events
            output_format: Output format: "events" (raw), "text" (formatted), "json" (summary)
            verbose: Show detailed steps (only for text format)

        Returns:
            InvokeResult with the outcome
        """
        try:
            response = self.client.invoke_bot(
                bot_key,
                messages=messages,
                parameters=parameters,
                dataset_slugs=dataset_slugs,
                mode=mode,
                manual_mocks=manual_mocks,
                stream=stream,
            )

            if stream:
                # Process SSE events
                events = []
                invocation_id = None

                # Type guard: response should be SSEClient when stream=True
                if not isinstance(response, dict):
                    # For formatted output, print as we stream
                    if output_format in ["text", "json"] and not self.print_events:
                        bot_name_printed = False
                        completed_steps = set()
                        step_names = {}  # Map to track step keys
                        printed_content_ids = (
                            set()
                        )  # Track which message content we've printed

                        for event in response.events():
                            if not event:
                                continue
                            events.append(event)

                            # Extract payload and metadata
                            payload = event.get("payload", {})
                            metadata = event.get("metadata", {})
                            status = (
                                payload.get("status")
                                if isinstance(payload, dict)
                                else None
                            )

                            # Extract invocation ID and bot name from payload
                            if isinstance(payload, dict):
                                if "invocation_id" in payload and not invocation_id:
                                    invocation_id = payload["invocation_id"]
                                if "bot_name" in payload and not bot_name_printed:
                                    bot_name = payload["bot_name"]
                                    if output_format == "text":
                                        print(f"Bot: {bot_name}")
                                        print(
                                            f"Invocation ID: {invocation_id or 'N/A'}"
                                        )
                                        print()  # Empty line before steps start
                                    bot_name_printed = True

                            # Track and display step info (ONLY in verbose mode)
                            # step_info events have both key and action_type in payload
                            if (
                                verbose
                                and output_format == "text"
                                and isinstance(payload, dict)
                            ):
                                if "key" in payload and "action_type" in payload:
                                    # This is a step_info event - show "▸" here if visible
                                    step_key = payload["key"]
                                    action_type = payload["action_type"]
                                    step_names[step_key] = action_type

                                    # Show step start on step_info event if visible
                                    if metadata.get("user_visibility") == "visible":
                                        print(f"▸ {step_key} ({action_type})")

                            # Handle step finished events (check status in payload)
                            # We look for the most recent step from step_names (ONLY in verbose mode)
                            if (
                                verbose
                                and output_format == "text"
                                and status == "step finished"
                            ):
                                if metadata.get("user_visibility") == "visible":
                                    # Find the last step that we haven't marked complete yet
                                    for step_key in reversed(list(step_names.keys())):
                                        if step_key not in completed_steps:
                                            print(f"✓ {step_key}")
                                            completed_steps.add(step_key)
                                            break

                            # Print message content as it streams
                            # ONLY print if:
                            # 1. user_visibility is "visible"
                            # 2. Has message_content_id (actual message content, not fragments)
                            # 3. content_type is "text" (not "json" or other types)
                            # 4. Haven't already printed chunks for this content_id
                            if (
                                output_format == "text"
                                and isinstance(payload, str)
                                and len(payload) > 0
                                and isinstance(metadata, dict)
                                and metadata.get("user_visibility") == "visible"
                                and metadata.get(
                                    "message_content_id"
                                )  # Must be message content
                                and metadata.get("content_type")
                                == "text"  # Only plain text, not JSON
                            ):
                                content_id = metadata.get("message_content_id")
                                # If this is a full message (long) and we've already printed chunks, skip
                                if (
                                    len(payload) > 20
                                    and content_id in printed_content_ids
                                ):
                                    # This is a duplicate full message after streaming chunks
                                    pass
                                else:
                                    print(payload, end="", flush=True)
                                    printed_content_ids.add(content_id)
                    else:
                        # For raw events or print_events mode, just collect
                        for event in response.events():
                            if not event:
                                continue
                            events.append(event)

                            if self.print_events:
                                self._print_event(event)

                            # Extract invocation ID from events
                            if "invocation_id" in event:
                                invocation_id = event["invocation_id"]

                # Extract structured data from events
                result_data = self._extract_result_data(events)

                return InvokeResult(
                    success=True,
                    bot_id=bot_key,
                    invocation_id=invocation_id,
                    result=result_data["result"],
                    messages=result_data["messages"],
                    steps=result_data["steps"],
                    events=events,
                )
            else:
                # Non-streaming response - response is a dict with 'events' key
                response_dict = response if isinstance(response, dict) else {}
                # Extract the events list from the response
                events = response_dict.get("events", [])

                # Extract structured data from events
                result_data = self._extract_result_data(events)

                return InvokeResult(
                    success=True,
                    bot_id=bot_key,
                    result=result_data["result"],
                    messages=result_data["messages"],
                    steps=result_data["steps"],
                    events=events,
                )

        except Exception as e:
            return InvokeResult(success=False, bot_id=bot_key, error=str(e))

    def _extract_result_data(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract structured data from events.

        Args:
            events: List of events from the invocation

        Returns:
            Dict with:
            - result: The final Result object {status, parameters, output, message, error}
            - messages: List of message objects {role, content}
            - steps: List of step execution info {key, action, status}
        """
        messages = []
        steps = []
        steps_seen = set()
        final_result = None

        # Iterate through ALL events to collect messages and steps
        for event in events:
            if not event:
                continue

            payload = event.get("payload", {})
            metadata = event.get("metadata", {})

            # Handle None values explicitly
            if payload is None:
                payload = {}
            if metadata is None:
                metadata = {}

            # Extract step information
            if (
                isinstance(payload, dict)
                and "action_type" in payload
                and "key" in payload
            ):
                step_key = payload["key"]
                if step_key not in steps_seen:
                    steps_seen.add(step_key)
                    steps.append(
                        {
                            "key": step_key,
                            "action": payload["action_type"],
                            "status": "completed",
                        }
                    )

            # Extract messages from ANY event with output.content
            # This captures messages from all steps including sub-agents
            # ONLY collect from output.content (final complete messages)
            # NOT from streaming chunks (those have message_content_id)
            if (
                isinstance(payload, dict)
                and "output" in payload
                and metadata.get("user_visibility") == "visible"
            ):
                output = payload.get("output")
                if isinstance(output, dict) and "content" in output:
                    content_array = output["content"]
                    if isinstance(content_array, list):
                        for item in content_array:
                            if (
                                isinstance(item, dict)
                                and item.get("content_type") == "text"
                            ):
                                # Extract as assistant message (or check for role in metadata)
                                role = metadata.get("role", "assistant")
                                messages.append(
                                    {"role": role, "content": item.get("content", "")}
                                )

            # Keep track of final result (last one with status + output)
            if (
                isinstance(payload, dict)
                and "status" in payload
                and "output" in payload
            ):
                # Create Result object from the payload
                final_result = Result(
                    status=payload.get("status"),
                    parameters=payload.get("parameters"),
                    output=payload.get("output"),
                    message=payload.get("message"),
                    error=payload.get("error"),
                )

        return {
            "result": final_result,
            "messages": messages,
            "steps": steps,
        }

    def _print_event(self, event: Dict[str, Any]):
        """Print an event in a readable format."""
        event_type = event.get("type", "unknown")

        if event_type == "step_started":
            step_name = event.get("step_name", "Unknown step")
            print(f"🔄 Step started: {step_name}")
        elif event_type == "step_completed":
            step_name = event.get("step_name", "Unknown step")
            print(f"✅ Step completed: {step_name}")
        elif event_type == "llm_chunk":
            content = event.get("content", "")
            print(content, end="", flush=True)
        elif event_type == "invocation_completed":
            print("\n✨ Invocation completed")
        elif event_type == "error":
            error = event.get("error", "Unknown error")
            print(f"❌ Error: {error}")
        else:
            # Generic event printing
            print(f"📡 {event_type}: {json.dumps(event, indent=2)}")


# Convenience functions
def invoke(
    bot_key: str,
    messages: Optional[List[Dict[str, str]]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    datasets: Optional[list] = None,
    mode: Optional[Union[str, Dict[str, Any]]] = None,
    manual_mocks: Optional[Dict[str, Dict[str, Any]]] = None,
    stream: bool = False,
    output_format: str = "events",
    verbose: bool = False,
    print_events: bool = False,
    **kwargs,
) -> InvokeResult:
    """Invoke a bot with a clean API.

    Args:
        bot_key: Bot key (e.g., "erdo.data-analyzer")
        messages: Messages in format [{"role": "user", "content": "..."}]
        parameters: Parameters to pass to the bot
        datasets: Dataset slugs to include (e.g. ["my-dataset"] or ["org.my-dataset"])
        mode: Invocation mode - string: "live|replay|manual" OR dict: {"mode": "replay", "refresh": true}
        manual_mocks: Manual mock responses for mode="manual" (step_path -> mock response)
        stream: Whether to stream events
        output_format: Output format: "events" (raw), "text" (formatted), "json" (summary)
        verbose: Show detailed steps (only for text format)
        print_events: Whether to print events
        **kwargs: Additional arguments (endpoint, auth_token)

    Returns:
        InvokeResult with formatted result in response.result

    Example:
        >>> from erdo import invoke
        >>>
        >>> # Simple replay mode
        >>> response = invoke("my_agent", messages=[...], mode="replay")
        >>>
        >>> # Replay mode with refresh (bypass cache)
        >>> response = invoke("my_agent", messages=[...], mode={"mode": "replay", "refresh": True})
        >>>
        >>> # Manual mode with mocks
        >>> response = invoke("my_agent", messages=[...], mode="manual",
        ...     manual_mocks={"llm.message": {"status": "success", "output": {"content": "Mocked"}}})
    """
    # Check ERDO_REFRESH environment variable
    # If set and mode is "replay" (string), convert to dict with refresh=True
    if os.environ.get("ERDO_REFRESH") == "1" and mode == "replay":
        mode = {"mode": "replay", "refresh": True}

    return invoke_by_key(
        bot_key=bot_key,
        messages=messages,
        parameters=parameters,
        dataset_slugs=datasets,
        mode=mode,
        manual_mocks=manual_mocks,
        stream=stream,
        output_format=output_format,
        verbose=verbose,
        print_events=print_events,
        **kwargs,
    )


def invoke_agent(
    agent: Any,
    parameters: Optional[Dict[str, Any]] = None,
    dataset_slugs: Optional[list] = None,
    stream: bool = False,
    print_events: bool = False,
    **kwargs,
) -> InvokeResult:
    """Invoke an agent instance.

    Args:
        agent: Agent instance with a 'key' attribute
        parameters: Parameters to pass to the agent
        dataset_slugs: Dataset slugs to include (e.g. ["my-dataset"] or ["org.my-dataset"])
        stream: Whether to stream events
        print_events: Whether to print events
        **kwargs: Additional arguments (endpoint, auth_token)

    Returns:
        InvokeResult with the outcome
    """
    invoke = Invoke(
        endpoint=kwargs.get("endpoint"),
        auth_token=kwargs.get("auth_token"),
        print_events=print_events,
    )
    return invoke.invoke_agent(agent, parameters, dataset_slugs, stream)


def invoke_by_key(
    bot_key: str,
    messages: Optional[List[Dict[str, str]]] = None,
    parameters: Optional[Dict[str, Any]] = None,
    dataset_slugs: Optional[list] = None,
    mode: Optional[Union[str, Dict[str, Any]]] = None,
    manual_mocks: Optional[Dict[str, Dict[str, Any]]] = None,
    stream: bool = False,
    output_format: str = "events",
    verbose: bool = False,
    print_events: bool = False,
    **kwargs,
) -> InvokeResult:
    """Invoke a bot by its key.

    Args:
        bot_key: Bot key (e.g., "erdo.data-analyzer")
        messages: Messages in format [{"role": "user", "content": "..."}]
        parameters: Parameters to pass to the bot
        dataset_slugs: Dataset slugs to include (e.g. ["my-dataset"] or ["org.my-dataset"])
        mode: Invocation mode - string: "live|replay|manual" OR dict: {"mode": "replay", "refresh": true}
        manual_mocks: Manual mock responses for mode="manual" (step_path -> mock response)
        stream: Whether to stream events
        output_format: Output format: "events" (raw), "text" (formatted), "json" (summary)
        verbose: Show detailed steps (only for text format)
        print_events: Whether to print events
        **kwargs: Additional arguments (endpoint, auth_token)

    Returns:
        InvokeResult with the outcome
    """
    invoke = Invoke(
        endpoint=kwargs.get("endpoint"),
        auth_token=kwargs.get("auth_token"),
        print_events=print_events,
    )
    return invoke.invoke_by_key(
        bot_key,
        messages,
        parameters,
        dataset_slugs,
        mode,
        manual_mocks,
        stream,
        output_format,
        verbose,
    )
