"""
This module contains the core ToDoWrite application class.
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict

# Forward declaration for type hints
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Concatenate,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

import jsonschema
import yaml
from jsonschema.exceptions import ValidationError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, joinedload, sessionmaker

from ..database.config import (
    StoragePreference,
    StorageType,
    determine_storage_backend,
    set_storage_preference,
)
from ..database.models import Artifact as DBArtifact
from ..database.models import Base
from ..database.models import Command as DBCommand
from ..database.models import Label as DBLabel
from ..database.models import Link as DBLink
from ..database.models import Node as DBNode
from ..storage.schema_validator import validate_database_schema
from .app_node_updater import NodeUpdater
from .types import Command, LayerType, Link, Metadata, Node, StatusType
from .utils import generate_node_id

# Type variables for generic functions
P = ParamSpec("P")
R = TypeVar("R")
F = TypeVar("F", bound=Callable[..., object])

if TYPE_CHECKING:
    from collections.abc import Generator

    from sqlalchemy.engine import Engine

    from ..storage.yaml_storage import YAMLStorage


def _validate_literal(value: str, literal_type: type[object]) -> str:
    if (
        hasattr(literal_type, "__args__")
        and literal_type.__args__
        and value not in literal_type.__args__
    ):
        raise ValueError(
            f"Invalid literal value: {value}. Expected one of "
            f"{literal_type.__args__}"
        )
    return value


class ToDoWrite:
    """The main ToDoWrite application class."""

    _SCHEMA: dict[str, Any] | None = None

    def __init__(
        self: ToDoWrite,
        db_url: str | None = None,
        auto_import: bool = True,
        storage_preference: StoragePreference | None = None,
    ) -> None:
        """Initializes the ToDoWrite application."""

        # Set storage preference if provided
        if storage_preference:
            set_storage_preference(storage_preference)

        # Determine storage backend
        self.storage_type, self.db_url = determine_storage_backend()

        # Initialize attributes with proper types
        self.engine: Engine | None = None
        self.Session: sessionmaker[Session] | None = None
        self.yaml_storage: YAMLStorage | None = None

        # Override URL if explicitly provided
        if db_url:
            self.db_url = db_url
            self.storage_type = (
                StorageType.POSTGRESQL
                if db_url.startswith("postgresql:")
                else StorageType.SQLITE
            )

        # Initialize database components only if not using YAML
        if self.storage_type != StorageType.YAML and self.db_url:
            self.engine = create_engine(self.db_url)
            self.Session = sessionmaker(bind=self.engine)
        else:
            self.engine = None
            self.Session = None

        # Load schema
        if ToDoWrite._SCHEMA is None:
            schema_path = (
                Path(__file__).parent / "schemas" / "todowrite.schema.json"
            )
            with open(schema_path) as f:
                ToDoWrite._SCHEMA = json.load(f)

        # Cache for database schema validation
        self._schema_validation_cache: tuple[bool, list[str]] | None = None

        # Session and query caching
        self._session_cache: dict[str, Session] = {}
        self._query_cache: dict[str, Any] = {}
        self._cache_ttl = 300.0  # 5 minutes cache TTL
        self._last_cache_clear = time.time()

        # Initialize YAML storage if using YAML mode
        if self.storage_type == StorageType.YAML:
            from ..storage.schema_validator import validate_yaml_files
            from ..storage.yaml_storage import YAMLStorage

            self.yaml_storage = YAMLStorage()

            # Validate YAML files schema
            try:
                is_valid, errors, file_counts = validate_yaml_files()
                if not is_valid:
                    error_msg = "YAML schema validation failed:\n" + "\n".join(
                        f"  - {error}" for error in errors
                    )
                    print(f"⚠️  {error_msg}")
                else:
                    files_checked = sum(file_counts.values())
                    print(
                        f"✅ YAML schema validation passed "
                        f"(checked {files_checked} files)"
                    )

                    # Report file counts by layer
                    if file_counts:
                        print("  Files by layer:")
                        for layer, count in file_counts.items():
                            if count > 0:
                                print(f"    {layer}: {count} files")
            except (OSError, ValueError, yaml.YAMLError) as e:
                print(f"⚠️  YAML validation error: {e}")
        else:
            self.yaml_storage = None

        # Auto-import YAML files if enabled and using database
        if auto_import and self.storage_type != StorageType.YAML:
            self._auto_import_yaml_files()

    def _clear_expired_cache(self: ToDoWrite) -> None:
        """Clear expired cache entries."""
        current_time = time.time()
        if current_time - self._last_cache_clear > self._cache_ttl:
            self._session_cache.clear()
            self._query_cache.clear()
            self._last_cache_clear = current_time

    def _clear_node_cache(self: ToDoWrite, node_id: str | None = None) -> None:
        """Clear node cache entries."""
        if node_id:
            # Clear specific node cache
            cache_key = f"node_{node_id}"
            self._query_cache.pop(cache_key, None)
        else:
            # Clear all node cache
            keys_to_remove = [
                key for key in self._query_cache if key.startswith("node_")
            ]
            for key in keys_to_remove:
                self._query_cache.pop(key, None)

    @contextmanager
    def get_session(self) -> Generator[Session | None, None, None]:
        if self.storage_type == StorageType.YAML:
            # YAML storage doesn't use sessions
            yield None
            return

        if self.Session is None:
            raise RuntimeError("Database session not initialized")

        # Clear expired cache entries
        self._clear_expired_cache()

        # Use existing session if available (simple session reuse)
        session_key = "default_session"
        if session_key in self._session_cache:
            session = self._session_cache[session_key]
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
        else:
            session = self.Session()
            try:
                self._session_cache[session_key] = session
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                # Only close when session is removed from cache
                if session_key in self._session_cache:
                    session.close()
                    self._session_cache.pop(session_key, None)

    @contextmanager
    def get_db_session(self) -> Generator[Session, None, None]:
        """Get a database session that is guaranteed to not be None."""
        if self.storage_type == StorageType.YAML:
            raise RuntimeError(
                "Database session requested but using YAML storage"
            )

        if self.Session is None:
            raise RuntimeError("Database session not initialized")

        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _validate_node_data(
        self: ToDoWrite, node_data: dict[str, Any]
    ) -> None:
        """Validates node data against the ToDoWrite schema."""
        if ToDoWrite._SCHEMA is None:
            raise ValueError("Schema not loaded. Cannot validate node data.")
        try:
            jsonschema.validate(instance=node_data, schema=ToDoWrite._SCHEMA)
        except ValidationError as e:
            raise ValueError(
                f"Node data validation failed: {e.message}"
            ) from e

    def _get_yaml_storage(self) -> YAMLStorage:
        """Get YAML storage with proper error handling."""
        if not self.yaml_storage:
            raise RuntimeError("YAML storage not initialized")
        return self.yaml_storage

    @overload
    def _execute_with_session(
        self,
        func: Callable[Concatenate[Session, P], R],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> R: ...

    @overload
    def _execute_with_session(
        self, func: Callable[..., R], *args: object, **kwargs: object
    ) -> R: ...

    def _execute_with_session(
        self, func: Callable[..., object], *args: object, **kwargs: object
    ) -> object:
        """Execute a function with a database session, handling None checks."""
        with self.get_session() as session:
            if session is None:
                raise RuntimeError("Database session not available")
            return func(session, *args, **kwargs)

    def init_database(self) -> None:
        """Creates the database and the tables."""
        if self.storage_type == StorageType.YAML:
            # For YAML storage, just ensure directories exist
            if self.yaml_storage:
                # Ensure YAML storage directories exist
                self.yaml_storage.ensure_directories()
            return

        if self.db_url and self.db_url.startswith("sqlite"):
            db_path: str = self.db_url.split("///")[1]
            if db_path and db_path != ":memory:":
                dirname: str = os.path.dirname(db_path)
                if dirname:
                    os.makedirs(dirname, exist_ok=True)
        if self.engine:
            Base.metadata.create_all(bind=self.engine)

            # Validate database schema AFTER tables are created (with caching)
            if self._schema_validation_cache is None:
                self._schema_validation_cache = validate_database_schema(
                    self.engine
                )

            is_valid, errors = self._schema_validation_cache
            if not is_valid:
                error_msg = "Database schema validation failed:\n" + "\n".join(
                    f"  - {error}" for error in errors
                )
                print(f"⚠️  {error_msg}")
            else:
                storage_name = self.storage_type.value.capitalize()
                print(f"✅ {storage_name} schema validation passed")

    def create_node(self: ToDoWrite, node_data: dict[str, Any]) -> Node:
        """Creates a new node in the storage backend."""
        self._validate_node_data(node_data)

        if self.storage_type == StorageType.YAML:
            # Convert node_data to Node and save to YAML
            yaml_storage = self._get_yaml_storage()
            node = self._dict_to_node(node_data)
            yaml_storage.save_node(node)
            return node

        with self.get_db_session() as session:
            db_node = self._create_db_node(session, node_data)
            return self._convert_db_node_to_node(db_node)

    def get_node(self: ToDoWrite, node_id: str) -> Node | None:
        """Retrieves a node from the storage backend."""
        if self.storage_type == StorageType.YAML:
            yaml_storage = self._get_yaml_storage()
            return yaml_storage.load_node(node_id)

        # Check query cache first
        cache_key = f"node_{node_id}"
        if cache_key in self._query_cache:
            cached_result = self._query_cache[cache_key]
            if cached_result is not None:
                return cast("Node", cached_result)

        with self.get_db_session() as session:
            stmt = (
                select(DBNode)
                .options(
                    joinedload(DBNode.labels),
                    joinedload(DBNode.command).joinedload(DBCommand.artifacts),
                )
                .where(DBNode.id == node_id)
            )
            db_node = session.execute(stmt).unique().scalar_one_or_none()
            if db_node:
                result = self._convert_db_node_to_node(db_node)
                # Cache the result
                self._query_cache[cache_key] = result
                return result
            else:
                # Cache negative results to avoid repeated DB hits
                self._query_cache[cache_key] = None
                return None

    def get_all_nodes(self) -> dict[str, list[Node]]:
        """Retrieves all the nodes from the storage backend."""
        if self.storage_type == StorageType.YAML:
            yaml_storage = self._get_yaml_storage()
            return yaml_storage.load_all_nodes()

        with self.get_db_session() as session:
            stmt = select(DBNode).options(
                joinedload(DBNode.labels),
                joinedload(DBNode.command).joinedload(DBCommand.artifacts),
            )
            db_nodes = session.execute(stmt).unique().scalars().all()
            # Use defaultdict for more efficient dictionary building
            from collections import defaultdict

            nodes: dict[str, list[Node]] = defaultdict(list)
            for db_node in db_nodes:
                node = self._convert_db_node_to_node(db_node)
                nodes[node.layer].append(node)
            # Convert back to regular dict for consistent return type
            return dict(nodes)

    def update_node(
        self, node_id: str, node_data: dict[str, Any]
    ) -> Node | None:
        """Updates an existing node in the storage backend."""
        # Skip validation for updates to allow partial updates
        # self._validate_node_data(node_data)

        if self.storage_type == StorageType.YAML:
            # For YAML, just save the updated node
            yaml_storage = self._get_yaml_storage()
            node = self._dict_to_node(node_data)
            yaml_storage.save_node(node)
            return node

        with self.get_db_session() as session:
            stmt = select(DBNode).where(DBNode.id == node_id)
            db_node = session.execute(stmt).scalar_one_or_none()
            if db_node:
                # Use helper methods to update different parts of the node
                updater: NodeUpdater = NodeUpdater(session)

                # Update basic node fields
                updater.update_node_fields(db_node, node_data)

                # Update relationships (links, labels, command)
                updater.update_links(node_id, node_data)
                updater.update_labels(db_node, node_data)
                updater.update_command(node_id, node_data)

                # Commit changes before refreshing to ensure they're persisted
                session.commit()

                # Refresh and return the updated node
                session.refresh(db_node)
                result = self._convert_db_node_to_node(db_node)

                # Clear cache for updated node and related nodes
                self._clear_node_cache(node_id)

                return result
            return None

    def delete_node(self: ToDoWrite, node_id: str) -> None:
        """Deletes a node from the storage backend."""
        if self.storage_type == StorageType.YAML:
            yaml_storage = self._get_yaml_storage()
            yaml_storage.delete_node(node_id)
            return

        with self.get_db_session() as session:
            stmt = select(DBNode).where(DBNode.id == node_id)
            db_node = session.execute(stmt).scalar_one_or_none()
            if db_node:
                session.delete(db_node)
                # Clear cache for deleted node
                self._clear_node_cache(node_id)

    def update_node_status(
        self: ToDoWrite, node_id: str, status: str
    ) -> Node | None:
        """Update a node's status using the default ToDoWrite instance."""
        status = cast("StatusType", status)
        node_data = {"status": status}
        return self.update_node(node_id, node_data)

    def search_nodes(self: ToDoWrite, query: str) -> dict[str, list[Node]]:
        """Search for nodes by query string."""
        query_lower = query.lower()
        results: dict[str, list[Node]] = {}

        # Use generator to avoid loading all nodes at once if using database
        if self.storage_type == StorageType.YAML:
            # For YAML, we load all nodes anyway, but optimize the search
            all_nodes = self.get_all_nodes()
            for layer, nodes in all_nodes.items():
                matching_nodes = [
                    node
                    for node in nodes
                    if (
                        query_lower in node.title.lower()
                        or query_lower in node.description.lower()
                        or query_lower in node.id.lower()
                    )
                ]
                if matching_nodes:
                    results[layer] = matching_nodes
        else:
            # For database, use a more efficient query
            with self.get_db_session() as session:
                stmt = select(DBNode).where(
                    (DBNode.title.ilike(f"%{query_lower}%"))
                    | (DBNode.description.ilike(f"%{query_lower}%"))
                    | (DBNode.id.ilike(f"%{query_lower}%"))
                )
                db_nodes = session.execute(stmt).unique().scalars().all()

                # Group by layer
                for db_node in db_nodes:
                    layer = db_node.layer
                    if layer not in results:
                        results[layer] = []
                    results[layer].append(
                        self._convert_db_node_to_node(db_node)
                    )

        return results

    def export_nodes(self: ToDoWrite, format: str = "yaml") -> str:
        """Export all nodes to a string in the specified format."""
        all_nodes = self.get_all_nodes()

        if format.lower() == "yaml":
            import yaml

            nodes_list: list[dict[str, Any]] = []
            for _layer, nodes in all_nodes.items():
                for node in nodes:
                    nodes_list.append(node.to_dict())
            return yaml.dump(nodes_list, default_flow_style=False)

        elif format.lower() == "json":
            import json

            nodes_dict = {}
            for layer, nodes in all_nodes.items():
                nodes_dict[layer] = [node.to_dict() for node in nodes]
            return json.dumps(nodes_dict, indent=2)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_nodes(self: ToDoWrite, file_path: str) -> dict[str, Any]:
        """Import nodes from a file."""
        import json
        from pathlib import Path

        import yaml

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine file format
        if path.suffix.lower() in [".yaml", ".yml"]:
            with open(path) as f:
                data = yaml.safe_load(f)
        elif path.suffix.lower() == ".json":
            with open(path) as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

        # Handle both single node and list of nodes
        if isinstance(data, dict) and "layer" in data:
            # Single node
            nodes_to_import: list[dict[str, Any]] = [data]
        elif isinstance(data, list):
            # List of nodes
            nodes_to_import = cast("list[dict[str, Any]]", data)
        else:
            raise ValueError(
                "Invalid file format: expected node object or list of nodes"
            )

        results: dict[str, Any] = {"imported": 0, "errors": [], "skipped": []}

        for node_data in nodes_to_import:
            try:
                # Generate ID if not provided
                if "id" not in node_data or not node_data["id"]:
                    layer: str = node_data.get("layer", "Node")
                    node_data["id"] = generate_node_id(layer)

                # Create the node
                self.create_node(node_data)
                results["imported"] += 1
            except (
                ValueError,
                KeyError,
                AttributeError,
                jsonschema.ValidationError,
            ) as e:
                results["errors"].append(str(e))

        return results

    def add_goal(
        self,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Goal node."""
        node_data: dict[str, Any] = {
            "id": generate_node_id("GOAL"),
            "layer": "Goal",
            "title": title,
            "description": description,
            "links": {"parents": [], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_phase(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Phase node."""
        node_data = {
            "id": generate_node_id("PH"),
            "layer": "Phase",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_step(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Step node."""
        node_data = {
            "id": generate_node_id("STP"),
            "layer": "Step",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_task(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Task node."""
        node_data = {
            "id": generate_node_id("TSK"),
            "layer": "Task",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_subtask(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new SubTask node."""
        node_data = {
            "id": generate_node_id("SUB"),
            "layer": "SubTask",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_command(
        self,
        parent_id: str,
        title: str,
        description: str,
        ac_ref: str,
        run: dict[str, Any],
        artifacts: list[str] | None = None,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Command node."""
        node_data = {
            "id": generate_node_id("CMD"),
            "layer": "Command",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
            "command": {
                "ac_ref": ac_ref,
                "run": run,
                "artifacts": artifacts or [],
            },
        }
        return self.create_node(node_data)

    def add_concept(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Concept node."""
        node_data = {
            "id": generate_node_id("CON"),
            "layer": "Concept",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_context(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Context node."""
        node_data = {
            "id": generate_node_id("CTX"),
            "layer": "Context",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_constraint(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Constraint node."""
        node_data = {
            "id": generate_node_id("CST"),
            "layer": "Constraints",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_requirement(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Requirement node."""
        node_data = {
            "id": generate_node_id("R"),
            "layer": "Requirements",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_acceptance_criteria(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Acceptance Criteria node."""
        node_data = {
            "id": generate_node_id("AC"),
            "layer": "AcceptanceCriteria",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def add_interface_contract(
        self,
        parent_id: str,
        title: str,
        description: str,
        owner: str = "system",
        labels: list[str] | None = None,
    ) -> Node:
        """Adds a new Interface Contract node."""
        node_data = {
            "id": generate_node_id("IF"),
            "layer": "InterfaceContract",
            "title": title,
            "description": description,
            "links": {"parents": [parent_id], "children": []},
            "metadata": {
                "owner": owner,
                "labels": labels or [],
                "severity": "",
                "work_type": "",
            },
        }
        return self.create_node(node_data)

    def get_node_by_id(self: ToDoWrite, node_id: str) -> Node | None:
        """Retrieves a node by its ID."""
        return self.get_node(node_id)

    def load_todos(self) -> dict[str, list[Node]]:
        """Loads all todos from the database."""
        return self.get_all_nodes()

    def get_active_items(
        self, todos: dict[str, list[Node]]
    ) -> dict[str, list[Node]]:
        """Return active items not done/rejected, grouped by layer."""
        active_items: dict[str, list[Node]] = defaultdict(list)
        for layer, nodes in todos.items():
            for node in nodes:
                if node.status not in ["done", "rejected"]:
                    active_items[layer].append(node)
        return dict(active_items)

    def _create_db_node(
        self, session: Session, node_data: dict[str, Any]
    ) -> DBNode:
        # Data validation
        required_fields: list[str] = ["id", "layer", "title", "description"]
        for field_name in required_fields:
            if field_name not in node_data:
                raise ValueError(f"Missing required field: {field_name}")

        db_node = DBNode(
            id=node_data["id"],
            layer=node_data["layer"],
            title=node_data["title"],
            description=node_data["description"],
            status=node_data.get("status", "planned"),
            progress=node_data.get("progress"),
            started_date=node_data.get("started_date"),
            completion_date=node_data.get("completion_date"),
            owner=node_data["metadata"].get("owner"),
            severity=node_data["metadata"].get("severity"),
            work_type=node_data["metadata"].get("work_type"),
            assignee=node_data["metadata"].get("assignee"),
        )
        session.add(db_node)
        session.flush()  # Flush to get the node ID for relationships

        for parent_id in node_data["links"].get("parents", []):
            if (
                parent_id is not None
            ):  # Skip None parents for flexible entry points
                link = DBLink(parent_id=parent_id, child_id=db_node.id)
                session.add(link)

        for label_text in node_data["metadata"].get("labels", []):
            label_stmt = select(DBLabel).where(DBLabel.label == label_text)
            label = session.execute(label_stmt).scalar_one_or_none()
            if not label:
                label = DBLabel(label=label_text)
                session.add(label)
            db_node.labels.append(label)

        if node_data.get("command"):
            command_data: dict[str, Any] = node_data["command"]
            db_command = DBCommand(
                node_id=db_node.id,
                ac_ref=command_data["ac_ref"],
                run=json.dumps(command_data["run"]),
            )
            session.add(db_command)
            session.flush()

            for artifact_text in command_data.get("artifacts", []):
                artifact = DBArtifact(
                    command_id=db_command.node_id, artifact=artifact_text
                )
                session.add(artifact)

        return db_node

    def _convert_db_node_to_node(self: ToDoWrite, db_node: DBNode) -> Node:
        links = Link(parents=[], children=[])
        metadata = Metadata(
            owner=str(db_node.owner or ""),
            labels=[label.label for label in db_node.labels],
            severity=str(db_node.severity or ""),
            work_type=str(db_node.work_type or ""),
            assignee=str(db_node.assignee or ""),
        )
        command = None
        if db_node.command:
            command = Command(
                ac_ref=str(db_node.command.ac_ref or ""),
                run=json.loads(db_node.command.run)
                if db_node.command.run
                else {},
                artifacts=[
                    artifact.artifact for artifact in db_node.command.artifacts
                ],
            )
        return Node(
            id=str(db_node.id),
            layer=cast(
                "LayerType", _validate_literal(str(db_node.layer), LayerType)
            ),
            title=str(db_node.title),
            description=str(db_node.description),
            status=cast(
                "StatusType",
                _validate_literal(str(db_node.status), StatusType),
            ),
            progress=db_node.progress if db_node.progress is not None else 0,
            started_date=str(db_node.started_date)
            if db_node.started_date
            else None,
            completion_date=(
                str(db_node.completion_date)
                if db_node.completion_date
                else None
            ),
            links=links,
            metadata=metadata,
            command=command,
        )

    def _dict_to_node(self: ToDoWrite, node_data: dict[str, Any]) -> Node:
        """Convert dictionary data to Node object."""
        links = Link(
            parents=node_data.get("links", {}).get("parents", []),
            children=node_data.get("links", {}).get("children", []),
        )

        metadata = Metadata(
            owner=node_data.get("metadata", {}).get("owner", ""),
            labels=node_data.get("metadata", {}).get("labels", []),
            severity=node_data.get("metadata", {}).get("severity", ""),
            work_type=node_data.get("metadata", {}).get("work_type", ""),
        )

        command = None
        if node_data.get("command"):
            command = Command(
                ac_ref=node_data["command"].get("ac_ref", ""),
                run=node_data["command"].get("run", {}),
                artifacts=node_data["command"].get("artifacts", []),
            )

        return Node(
            id=node_data["id"],
            layer=cast("LayerType", node_data["layer"]),
            title=node_data["title"],
            description=node_data["description"],
            links=links,
            metadata=metadata,
            status=cast("StatusType", node_data.get("status", "planned")),
            command=command,
        )

    def _auto_import_yaml_files(self) -> None:
        """Automatically import YAML files that are not in the database."""
        try:
            # Only attempt auto-import if database is accessible
            if self.engine:
                Base.metadata.create_all(bind=self.engine)

            # Import YAMLManager here to avoid circular imports
            from ..storage.yaml_manager import YAMLManager

            yaml_manager = YAMLManager(self)
            sync_status = yaml_manager.check_yaml_sync()

            if sync_status["yaml_only"]:
                print(
                    f"🔄 Auto-importing {len(sync_status['yaml_only'])} "
                    f"YAML files..."
                )
                results = yaml_manager.import_yaml_files(
                    force=False, dry_run=False
                )

                if results["total_imported"] > 0:
                    print(
                        f"✅ Auto-imported {results['total_imported']} files"
                    )

                if results["errors"]:
                    print(f"⚠️  {len(results['errors'])} auto-import errors")

        except (
            OSError,
            ValueError,
            yaml.YAMLError,
            AttributeError,
            KeyError,
        ) as e:
            # Log the error but don't break normal operation
            logging.warning(f"Auto-import YAML failed: {e}")
            print(f"⚠️  Auto-import of YAML files failed: {e}")


# Standalone wrapper functions for public API
def create_node(node_data: dict[str, Any]) -> Node:
    """Create a new node using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    app.init_database()
    return app.create_node(node_data)


def get_node(node_id: str) -> Node | None:
    """Get a node by ID using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    app.init_database()
    return app.get_node(node_id)


def update_node(node_id: str, node_data: dict[str, Any]) -> Node | None:
    """Update a node using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    app.init_database()
    return app.update_node(node_id, node_data)


def delete_node(node_id: str) -> None:
    """Delete a node using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    app.init_database()
    app.delete_node(node_id)


def list_nodes() -> dict[str, list[Node]]:
    """List all nodes using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    app.init_database()
    return app.get_all_nodes()


def search_nodes(query: str) -> dict[str, list[Node]]:
    """Search for nodes using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    app.init_database()
    return app.search_nodes(query)


def export_nodes(format: str = "yaml") -> str:
    """Export nodes using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    return app.export_nodes(format)


def import_nodes(file_path: str) -> dict[str, Any]:
    """Import nodes from a file using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    return app.import_nodes(file_path)


def update_node_status(node_id: str, status: str) -> Node | None:
    """Update node status using the default ToDoWrite instance."""
    app = ToDoWrite(auto_import=False)
    return app.update_node_status(node_id, status)


def link_nodes(
    db_url: str, parent_id: str, child_id: str, _: dict[str, Any] | None = None
) -> bool:
    """Link two nodes together in the database."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine(db_url)
    session = Session(engine)

    try:
        # Get both nodes
        from ..database.models import Link as DBLink
        from ..database.models import Node as DBNode

        parent_node = session.execute(
            select(DBNode).where(DBNode.id == parent_id)
        ).scalar_one_or_none()
        child_node = session.execute(
            select(DBNode).where(DBNode.id == child_id)
        ).scalar_one_or_none()

        if not parent_node or not child_node:
            return False

        # Check if link already exists
        existing_link = session.execute(
            select(DBLink).where(
                DBLink.parent_id == parent_id, DBLink.child_id == child_id
            )
        ).scalar_one_or_none()

        if existing_link:
            return True  # Link already exists

        # Create new link
        link = DBLink(parent_id=parent_id, child_id=child_id)
        session.add(link)
        session.commit()
        return True

    except Exception:
        session.rollback()
        return False
    finally:
        session.close()


def unlink_nodes(db_url: str, parent_id: str, child_id: str) -> bool:
    """Remove a link between two nodes in the database."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine(db_url)
    session = Session(engine)

    try:
        from ..database.models import Link as DBLink

        # Find and delete the link
        link = session.execute(
            select(DBLink).where(
                DBLink.parent_id == parent_id, DBLink.child_id == child_id
            )
        ).scalar_one_or_none()

        if link:
            session.delete(link)
            session.commit()
            return True
        return False

    except Exception:
        session.rollback()
        return False
    finally:
        session.close()
