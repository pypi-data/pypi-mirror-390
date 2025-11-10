"""
Custom exceptions for ToDoWrite

This module defines custom exception classes for consistent error handling
throughout the ToDoWrite codebase.
"""

from __future__ import annotations

from typing import Any


class ToDoWriteError(Exception):
    """Base exception class for all ToDoWrite errors."""

    pass


class NodeError(ToDoWriteError):
    """Base exception for node-related errors."""

    pass


class NodeNotFoundError(NodeError):
    """Raised when a node is not found."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        super().__init__(f"Node not found: {node_id}")


class InvalidNodeError(NodeError):
    """Raised when node data is invalid."""

    def __init__(
        self, message: str, details: dict[str, Any] | None = None
    ) -> None:
        self.details = details or {}
        super().__init__(message)


class StorageError(ToDoWriteError):
    """Base exception for storage-related errors."""

    pass


class DatabaseError(StorageError):
    """Raised for database-related errors."""

    def __init__(
        self, message: str, original_exception: Exception | None = None
    ) -> None:
        self.original_exception = original_exception
        super().__init__(f"Database error: {message}")


class YAMLError(StorageError):
    """Raised for YAML-related errors."""

    def __init__(self, message: str, file_path: str | None = None) -> None:
        self.file_path = file_path
        msg = f"YAML error: {message}"
        if file_path:
            msg += f" (file: {file_path})"
        super().__init__(msg)


class SchemaError(ToDoWriteError):
    """Raised for schema validation errors."""

    def __init__(
        self, message: str, validation_errors: list[str] | None = None
    ) -> None:
        self.validation_errors = validation_errors or []
        msg = f"Schema error: {message}"
        if self.validation_errors:
            msg += f" ({len(self.validation_errors)} errors)"
        super().__init__(msg)


class ConfigurationError(ToDoWriteError):
    """Raised for configuration-related errors."""

    pass


class CLIError(ToDoWriteError):
    """Raised for CLI-related errors."""

    pass


class TokenOptimizationError(ToDoWriteError):
    """Raised for token optimization errors."""

    pass
