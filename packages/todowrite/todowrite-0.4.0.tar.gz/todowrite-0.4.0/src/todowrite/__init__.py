"""ToDoWrite: Hierarchical Task Management System

A sophisticated hierarchical task management system designed for complex
project planning and execution. Built with a 12-layer declarative framework,
it provides both a standalone CLI and a Python module for programmatic use.
"""

from __future__ import annotations

# Core version information
from .version import get_version

__version__ = get_version()
__title__ = "ToDoWrite"
__description__ = (
    "Hierarchical task management system with 12-layer "
    "declarative planning framework"
)

# Core application components (re-export from core package)
from .core import (
    TODOWRITE_SCHEMA,
    CLIError,
    Command,
    ConfigurationError,
    DatabaseError,
    InvalidNodeError,
    LayerType,
    Link,
    Metadata,
    Node,
    NodeError,
    NodeNotFoundError,
    NodeUpdater,
    ProjectManager,
    SchemaError,
    StatusType,
    StorageError,
    ToDoWrite,
    ToDoWriteError,
    TokenOptimizationError,
    YAMLError,
    create_node,
    delete_node,
    export_nodes,
    generate_node_id,
    get_node,
    import_nodes,
    link_nodes,
    list_nodes,
    search_nodes,
    unlink_nodes,
    update_node,
)

# YAML / storage helpers
from .storage import YAMLManager
from .storage import validate_database_schema as validate_schema
from .storage import validate_node_data as validate_node

__all__ = [
    "TODOWRITE_SCHEMA",
    "CLIError",
    "Command",
    "ConfigurationError",
    "DatabaseError",
    "InvalidNodeError",
    "LayerType",
    "Link",
    "Metadata",
    "Node",
    "NodeError",
    "NodeNotFoundError",
    "NodeUpdater",
    "ProjectManager",
    "SchemaError",
    "StatusType",
    "StorageError",
    "ToDoWrite",
    "ToDoWriteError",
    "TokenOptimizationError",
    "YAMLError",
    "YAMLManager",
    "__description__",
    "__title__",
    "__version__",
    "create_node",
    "delete_node",
    "export_nodes",
    "generate_node_id",
    "get_node",
    "import_nodes",
    "link_nodes",
    "list_nodes",
    "search_nodes",
    "unlink_nodes",
    "update_node",
    "validate_node",
    "validate_schema",
]


def init_project(_project_path: str = ".", _db_type: str = "postgres") -> bool:
    """Quick project initialization helper.

    Args:
        _project_path: Path to the project directory
        (default: current directory)
        _db_type: Database type to configure (``'postgres'`` or ``'sqlite'``)

    Returns:
        True if initialization was successful (placeholder implementation).
    """

    # Placeholder implementation. Project initialization helpers live in
    # ``ProjectManager`` and will be wired into this convenience helper when
    # those APIs are stabilized.
    return True
