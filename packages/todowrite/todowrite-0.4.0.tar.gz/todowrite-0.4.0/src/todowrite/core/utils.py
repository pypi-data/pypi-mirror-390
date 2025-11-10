"""
Utility functions for ToDoWrite

This module contains utility functions that are used across the codebase
to avoid code duplication and provide consistent behavior.
"""

from __future__ import annotations

import uuid
from typing import TypeVar, cast

T = TypeVar("T")


def generate_node_id(prefix: str = "") -> str:
    """
    Generate a unique node ID with optional prefix.

    Args:
        prefix: Optional prefix for the node ID (e.g., "GOAL", "TASK")

    Returns:
        A unique node ID as "PREFIX-UUID" or just "UUID" if no prefix
    """
    uuid_part = uuid.uuid4().hex[:12].upper()
    return f"{prefix}-{uuid_part}" if prefix else uuid_part


def safe_get_nested(
    data: dict[str, object], *keys: str, default: object = None
) -> object:
    """
    Safely get a nested value from a dictionary using dot notation.

    Args:
        data: The dictionary to search
        *keys: Keys to traverse in order
        default: Default value if any key is not found

    Returns:
        The nested value or default value if not found (generic type)
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return cast("T", current)


def truncate_string(
    text: str, max_length: int = 100, suffix: str = "..."
) -> str:
    """
    Truncate a string to maximum length with suffix.

    Args:
        text: The string to truncate
        max_length: Maximum length of the result
        suffix: Suffix to add if truncation occurs

    Returns:
        The truncated string or original string if short enough
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
