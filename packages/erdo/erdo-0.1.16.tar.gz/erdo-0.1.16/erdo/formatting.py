"""Output formatting helpers for bot invocations.

This module provides utilities to parse and format bot invocation events
into human-readable output. Use these for displaying invocation results
in terminals, scripts, or other user-facing contexts.

Example:
    >>> from erdo import invoke
    >>> from erdo.formatting import format_invocation
    >>>
    >>> response = invoke("my_agent", messages=[...])
    >>> print(format_invocation(response))
    Bot: my agent
    Invocation ID: abc-123

    Result:
    The answer is 4

    >>> # Verbose mode shows steps
    >>> print(format_invocation(response, verbose=True))
    Bot: my agent
    Invocation ID: abc-123

    Steps:
      ✓ step1 (utils.echo)
      ✓ step2 (llm.message)

    Result:
    The answer is 4
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StepInfo:
    """Information about a single step execution."""

    key: str
    action: str
    status: str = "completed"


@dataclass
class InvocationSummary:
    """Structured summary of a bot invocation.

    This provides a clean, parsed view of the invocation events
    with key information extracted and organized.
    """

    bot_name: Optional[str] = None
    bot_key: Optional[str] = None
    invocation_id: Optional[str] = None
    steps: List[StepInfo] = field(default_factory=list)
    result: Optional[Any] = None
    error: Optional[str] = None
    success: bool = True


def parse_invocation_events(
    events: List[Dict[str, Any]],
    bot_key: Optional[str] = None,
    invocation_id: Optional[str] = None,
) -> InvocationSummary:
    """Parse raw invocation events into a structured summary.

    Args:
        events: List of event dictionaries from the backend
        bot_key: Bot key to use as fallback if not in events
        invocation_id: Invocation ID to use as fallback if not in events

    Returns:
        InvocationSummary with parsed information

    Example:
        >>> summary = parse_invocation_events(response.events, bot_key="my_agent")
        >>> print(summary.bot_name)
        'my agent'
        >>> print(summary.steps)
        [StepInfo(key='step1', action='utils.echo', status='completed')]
    """
    summary = InvocationSummary(
        bot_key=bot_key,
        invocation_id=invocation_id,
    )

    steps_seen = set()
    final_messages = []

    for event in events:
        # Events are dicts with 'payload' and 'metadata'
        payload = event.get("payload", {})
        metadata = event.get("metadata", {})

        # Extract invocation ID if not set
        if summary.invocation_id is None:
            if "invocation_id" in payload:
                summary.invocation_id = payload["invocation_id"]
            elif "invocation_id" in metadata:
                summary.invocation_id = metadata["invocation_id"]

        # Extract bot name
        if summary.bot_name is None and "bot_name" in payload:
            summary.bot_name = payload["bot_name"]

        # Track step execution
        if "action_type" in payload and "key" in payload:
            step_key = payload["key"]
            # Only add if not already present (avoid duplicates)
            if step_key not in steps_seen:
                steps_seen.add(step_key)
                summary.steps.append(
                    StepInfo(
                        key=step_key,
                        action=payload["action_type"],
                        status="completed",
                    )
                )

        # Collect user-visible text messages (final output)
        if isinstance(payload, str) and metadata.get("user_visibility") == "visible":
            if metadata.get("message_content_id"):  # It's part of a message
                final_messages.append(payload)

    # Combine final messages into result
    if final_messages:
        summary.result = "".join(final_messages)

    return summary


def format_invocation(
    response: Any,
    mode: str = "text",
    verbose: bool = False,
) -> str:
    """Format a bot invocation response for display.

    Args:
        response: InvokeResult from invoke()
        mode: Output mode - 'text' or 'json'
        verbose: Show detailed step execution (only applies to text mode)

    Returns:
        Formatted string ready to print

    Example:
        >>> from erdo import invoke
        >>> from erdo.formatting import format_invocation
        >>>
        >>> response = invoke("my_agent", messages=[...])
        >>>
        >>> # Simple text output
        >>> print(format_invocation(response))
        >>>
        >>> # Verbose text output (shows steps)
        >>> print(format_invocation(response, verbose=True))
        >>>
        >>> # JSON output
        >>> print(format_invocation(response, mode='json'))
    """
    if mode == "json":
        return _format_as_json(response)
    else:
        return _format_as_text(response, verbose)


def _format_as_json(response: Any) -> str:
    """Format response as JSON."""
    output = {
        "success": response.success,
        "invocation_id": response.invocation_id,
        "result": response.result,
        "error": response.error,
        "events": response.events,
    }
    return json.dumps(output, indent=2)


def _format_as_text(response: Any, verbose: bool = False) -> str:
    """Format response as human-readable text."""
    # Get bot key from response if available
    bot_key = getattr(response, "bot_id", None)
    invocation_id = response.invocation_id

    # Parse events to extract information
    # Handle SDK response structure: response.result may contain {'events': [...]}
    events_to_process = response.events
    if isinstance(response.result, dict) and "events" in response.result:
        events_to_process = response.result["events"]

    summary = parse_invocation_events(
        events_to_process,
        bot_key=bot_key,
        invocation_id=invocation_id,
    )

    # Build output
    lines = []

    if not response.success:
        lines.append(f"❌ Invocation failed: {response.error}")
        return "\n".join(lines)

    # Header
    lines.append(f"Bot: {summary.bot_name or summary.bot_key or 'unknown'}")
    lines.append(f"Invocation ID: {summary.invocation_id or 'N/A'}")

    # Steps (verbose mode)
    if verbose and summary.steps:
        lines.append("")
        lines.append("Steps:")
        for step in summary.steps:
            status_icon = "✓" if step.status == "completed" else "•"
            lines.append(f"  {status_icon} {step.key} ({step.action})")

    # Result
    if summary.result:
        lines.append("")
        lines.append("Result:")

        # Try to parse as JSON for pretty printing
        try:
            parsed = json.loads(summary.result)
            lines.append(json.dumps(parsed, indent=2))
        except (json.JSONDecodeError, TypeError):
            # If not JSON, print as is
            lines.append(summary.result)
    elif response.result is not None:
        lines.append("")
        lines.append("Result:")
        if isinstance(response.result, (dict, list)):
            lines.append(json.dumps(response.result, indent=2))
        else:
            lines.append(str(response.result))

    return "\n".join(lines)


# Convenience method to add to InvokeResult
def add_format_method():
    """Add format() method to InvokeResult class.

    This is called during SDK initialization to add the format()
    method to InvokeResult instances.
    """
    try:
        from .invoke.invoke import InvokeResult

        def format_method(self, mode="text", verbose=False):
            """Format this invocation result for display.

            Args:
                mode: 'text' or 'json'
                verbose: Show step details (text mode only)

            Returns:
                Formatted string

            Example:
                >>> response = invoke("my_agent", messages=[...])
                >>> print(response.format())
                >>> print(response.format(verbose=True))
            """
            return format_invocation(self, mode=mode, verbose=verbose)

        # Add method to class
        InvokeResult.format = format_method

    except ImportError:
        # InvokeResult not available, skip
        pass


# Auto-add format method on import
add_format_method()
