"""Evaluation functions for agent test assertions."""

import json
import re
from typing import Any, Dict, List, Optional, Union


def text_contains(value: Any, expected: str, case_sensitive: bool = True) -> bool:
    """Check if text contains the expected substring.

    Args:
        value: The value to check (will be converted to string)
        expected: The substring to look for
        case_sensitive: Whether the match should be case-sensitive

    Returns:
        True if the text contains the expected substring

    Example:
        >>> text_contains("Hello World", "World")
        True
        >>> text_contains("Hello World", "world", case_sensitive=False)
        True
        >>> text_contains("Hello World", "Goodbye")
        False
    """
    text = str(value)
    if not case_sensitive:
        text = text.lower()
        expected = expected.lower()
    return expected in text


def text_equals(value: Any, expected: str, case_sensitive: bool = True) -> bool:
    """Check if text exactly equals the expected value.

    Args:
        value: The value to check (will be converted to string)
        expected: The exact string to match
        case_sensitive: Whether the match should be case-sensitive

    Returns:
        True if the text exactly matches

    Example:
        >>> text_equals("Hello", "Hello")
        True
        >>> text_equals("Hello", "hello", case_sensitive=False)
        True
        >>> text_equals("Hello World", "Hello")
        False
    """
    text = str(value)
    if not case_sensitive:
        text = text.lower()
        expected = expected.lower()
    return text == expected


def text_matches(value: Any, pattern: str, flags: int = 0) -> bool:
    """Check if text matches a regular expression pattern.

    Args:
        value: The value to check (will be converted to string)
        pattern: The regex pattern to match
        flags: Optional regex flags (e.g., re.IGNORECASE)

    Returns:
        True if the text matches the pattern

    Example:
        >>> text_matches("Hello 123", r"Hello \\d+")
        True
        >>> text_matches("hello world", r"^hello", re.IGNORECASE)
        True
        >>> text_matches("abc", r"\\d+")
        False
    """
    text = str(value)
    return re.search(pattern, text, flags) is not None


def json_path_equals(data: Union[Dict, str], path: str, expected: Any) -> bool:
    """Check if a JSON path in the data equals the expected value.

    Args:
        data: Dictionary or JSON string to search
        path: Dot-notation path (e.g., "user.name" or "items[0].id")
        expected: The expected value at that path

    Returns:
        True if the value at the path equals expected

    Example:
        >>> data = {"user": {"name": "Alice", "age": 30}}
        >>> json_path_equals(data, "user.name", "Alice")
        True
        >>> json_path_equals(data, "user.age", 30)
        True
        >>> json_path_equals(data, "user.name", "Bob")
        False

    Note:
        Supports simple paths like "a.b.c" and array access like "items[0]"
        For complex JSONPath queries, consider using a dedicated JSONPath library
    """
    # Convert string to dict if needed
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return False

    # Navigate the path
    value = _get_json_path_value(data, path)
    return value == expected


def json_path_exists(data: Union[Dict, str], path: str) -> bool:
    """Check if a JSON path exists in the data.

    Args:
        data: Dictionary or JSON string to search
        path: Dot-notation path (e.g., "user.name" or "items[0].id")

    Returns:
        True if the path exists (even if value is None)

    Example:
        >>> data = {"user": {"name": "Alice"}}
        >>> json_path_exists(data, "user.name")
        True
        >>> json_path_exists(data, "user.email")
        False
    """
    # Convert string to dict if needed
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return False

    try:
        _get_json_path_value(data, path)
        return True
    except (KeyError, IndexError, TypeError):
        return False


def has_dataset(
    response: Any, dataset_id: Optional[str] = None, dataset_key: Optional[str] = None
) -> bool:
    """Check if a response includes a specific dataset.

    Args:
        response: The invocation response
        dataset_id: Optional dataset ID to check for
        dataset_key: Optional dataset key to check for

    Returns:
        True if the dataset is present in the response

    Example:
        >>> # Check if any dataset is present
        >>> has_dataset(response)
        True
        >>> # Check for specific dataset by ID
        >>> has_dataset(response, dataset_id="abc-123")
        True
        >>> # Check for dataset by key
        >>> has_dataset(response, dataset_key="sales_data")
        True
    """
    # Try to extract datasets from common response formats
    datasets = []

    # Check if response has datasets attribute
    if hasattr(response, "datasets"):
        datasets = response.datasets
    # Check if response has events with dataset info
    elif hasattr(response, "events"):
        for event in response.events:
            if isinstance(event, dict):
                payload = event.get("payload", {})
                if "datasets" in payload:
                    datasets.extend(payload["datasets"])
                if "dataset" in payload:
                    datasets.append(payload["dataset"])

    # Check if specific dataset is present
    if dataset_id or dataset_key:
        for dataset in datasets:
            if isinstance(dataset, dict):
                if dataset_id and dataset.get("id") == dataset_id:
                    return True
                if dataset_key and dataset.get("key") == dataset_key:
                    return True
            elif isinstance(dataset, str):
                # Dataset might just be an ID string
                if dataset_id and dataset == dataset_id:
                    return True
        return False

    # Check if any dataset is present
    return len(datasets) > 0


def _get_json_path_value(data: Any, path: str) -> Any:
    """Navigate a JSON path and return the value.

    Supports:
        - Dot notation: "user.name"
        - Array access: "items[0]"
        - Mixed: "users[0].name"

    Raises:
        KeyError, IndexError, TypeError if path doesn't exist
    """
    if not path:
        return data

    parts = _parse_path(path)
    current = data

    for part in parts:
        if isinstance(part, int):
            # Array index
            current = current[part]
        else:
            # Object key
            current = current[part]

    return current


def _parse_path(path: str) -> List[Union[str, int]]:
    """Parse a JSON path into parts.

    Examples:
        "user.name" → ["user", "name"]
        "items[0]" → ["items", 0]
        "users[0].name" → ["users", 0, "name"]
    """
    parts: List[Union[str, int]] = []
    current = ""

    i = 0
    while i < len(path):
        char = path[i]

        if char == ".":
            if current:
                parts.append(current)
                current = ""
        elif char == "[":
            if current:
                parts.append(current)
                current = ""
            # Find closing bracket
            j = path.index("]", i)
            index = int(path[i + 1 : j])
            parts.append(index)
            i = j
        else:
            current += char

        i += 1

    if current:
        parts.append(current)

    return parts
