"""Test evaluation helpers for erdo agent testing.

This module provides helper functions for writing clean assertions when testing agents.
Use these in regular Python scripts - no pytest needed!

Example:
    >>> from erdo import invoke
    >>> from erdo.test import text_contains, json_path_equals
    >>>
    >>> # Test in a regular Python script
    >>> response = invoke("my_agent", messages=[...], mode="replay")
    >>> assert text_contains(response.result, "expected text")
    >>> assert json_path_equals(response.result, "status", "success")
    >>>
    >>> # Or use via CLI
    >>> # ./erdo invoke my_agent --message "test" --mode replay
"""

from .evaluate import (
    has_dataset,
    json_path_equals,
    json_path_exists,
    text_contains,
    text_equals,
    text_matches,
)
from .runner import discover_tests
from .runner import main as run_tests
from .runner import run_tests_parallel

__all__ = [
    "text_contains",
    "text_equals",
    "text_matches",
    "json_path_equals",
    "json_path_exists",
    "has_dataset",
    "run_tests",
    "run_tests_parallel",
    "discover_tests",
]
