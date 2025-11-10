"""
YAML Storage Backend for ToDoWrite

This module provides a YAML-based storage backend that mimics the database interface
when database connections are not available. It serves as the last resort fallback.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml

from ..core.constants import DEFAULT_BASE_PATH, LAYER_DIRS
from ..core.exceptions import InvalidNodeError, YAMLError
from ..core.types import Command, Link, Metadata, Node
from .schema_validator import validate_node_data


class YAMLStorage:
    """YAML-based storage backend for ToDoWrite when databases are unavailable."""

    def __init__(
        self: YAMLStorage, base_path: Path | str | None = None
    ) -> None:
        """Initialize YAML storage."""
        self.base_path = (
            Path(base_path) if base_path else Path(DEFAULT_BASE_PATH)
        )
        self.plans_path = self.base_path / "plans"
        self.commands_path = self.base_path / "commands"
        self.layer_dirs = LAYER_DIRS

        # Create directories if they don't exist
        self.ensure_directories()

    def ensure_directories(self) -> None:
        """Ensure all necessary directories exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.plans_path.mkdir(parents=True, exist_ok=True)
        self.commands_path.mkdir(parents=True, exist_ok=True)

        for layer, dir_name in self.layer_dirs.items():
            if layer == "Command":
                continue  # Commands go in commands/ directory
            layer_dir = self.plans_path / dir_name
            layer_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self: YAMLStorage, node_id: str, layer: str) -> Path:
        """Get the file path for a node."""
        if layer == "Command":
            return self.commands_path / f"{node_id}.yaml"
        else:
            dir_name = self.layer_dirs.get(layer)
            if not dir_name:
                raise ValueError(f"Unknown layer: {layer}")
            return self.plans_path / dir_name / f"{node_id}.yaml"

    def _node_to_yaml(self: YAMLStorage, node: Node) -> dict[str, Any]:
        """Convert a Node object to YAML-compatible dictionary."""
        yaml_data: dict[str, Any] = {
            "id": node.id,
            "layer": node.layer,
            "title": node.title,
            "description": node.description,
            "metadata": {
                "owner": node.metadata.owner,
                "labels": list(node.metadata.labels),
            },
        }

        # Add optional metadata fields if they exist
        if node.metadata.severity:
            yaml_data["metadata"]["severity"] = node.metadata.severity
        if node.metadata.work_type:
            yaml_data["metadata"]["work_type"] = node.metadata.work_type

        # Add status if not default
        if node.status != "planned":
            yaml_data["status"] = node.status

        # Add links
        yaml_data["links"] = {
            "parents": node.links.parents,
            "children": node.links.children,
        }

        # Add command if exists
        if node.command:
            yaml_data["command"] = {
                "ac_ref": node.command.ac_ref,
                "run": node.command.run,
                "artifacts": node.command.artifacts,
            }

        return yaml_data

    def _yaml_to_node(self: YAMLStorage, yaml_data: dict[str, Any]) -> Node:
        """Convert YAML data to Node object."""
        links = Link(
            parents=yaml_data.get("links", {}).get("parents", []),
            children=yaml_data.get("links", {}).get("children", []),
        )

        metadata = Metadata(
            owner=yaml_data.get("metadata", {}).get("owner", ""),
            labels=yaml_data.get("metadata", {}).get("labels", []),
            severity=yaml_data.get("metadata", {}).get("severity", ""),
            work_type=yaml_data.get("metadata", {}).get("work_type", ""),
        )

        command = None
        if yaml_data.get("command"):
            command = Command(
                ac_ref=yaml_data["command"].get("ac_ref", ""),
                run=yaml_data["command"].get("run", {}),
                artifacts=yaml_data["command"].get("artifacts", []),
            )

        return Node(
            id=yaml_data["id"],
            layer=yaml_data["layer"],
            title=yaml_data["title"],
            description=yaml_data["description"],
            links=links,
            metadata=metadata,
            status=yaml_data.get("status", "planned"),
            command=command,
        )

    def load_node(self: YAMLStorage, node_id: str) -> Node | None:
        """Load a node by ID from YAML files."""
        # Search through all directories to find the node
        for layer_dir_name in self.layer_dirs.values():
            if layer_dir_name == "commands":
                file_path = self.commands_path / f"{node_id}.yaml"
            else:
                file_path = (
                    self.plans_path / layer_dir_name / f"{node_id}.yaml"
                )

            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        yaml_data = yaml.safe_load(f)
                    return self._yaml_to_node(yaml_data)
                except (yaml.YAMLError, OSError, PermissionError) as e:
                    raise YAMLError(
                        f"Failed to load YAML file: {e}", str(file_path)
                    ) from e

        return None

    def save_node(self: YAMLStorage, node_data: dict[str, Any] | Node) -> Node:
        """Save a node to YAML file."""
        # Handle both dict and Node objects
        if isinstance(node_data, dict):
            node_dict = node_data
            node = Node.from_dict(node_dict)
        else:
            node_dict = node_data.to_dict()
            node = node_data

        # Validate against schema
        is_valid, errors = validate_node_data(node_dict)
        if not is_valid:
            error_msg = "Node validation failed:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise InvalidNodeError(
                error_msg, {"node_id": node.id, "errors": errors}
            )

        file_path = self._get_file_path(node.id, node.layer)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        yaml_data = self._node_to_yaml(node)

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

        return node

    def update_node(
        self, node_id: str, node_data: dict[str, Any] | Node
    ) -> Node | None:
        """Update an existing node."""
        # Check if node exists
        if not self.node_exists(node_id):
            return None

        # Handle both dict and Node objects
        if isinstance(node_data, dict):
            # Ensure the ID matches
            node_data["id"] = node_id
            node_dict = node_data
            node = Node.from_dict(node_dict)
        else:
            # Update the node's ID to match
            updated_node_data = node_data.to_dict()
            updated_node_data["id"] = node_id
            node = Node.from_dict(updated_node_data)
            node_dict = updated_node_data

        # Validate against schema
        is_valid, errors = validate_node_data(node_dict)
        if not is_valid:
            error_msg = "Node validation failed:\n" + "\n".join(
                f"  - {error}" for error in errors
            )
            raise InvalidNodeError(
                error_msg, {"node_id": node.id, "errors": errors}
            )

        file_path = self._get_file_path(node.id, node.layer)

        yaml_data = self._node_to_yaml(node)

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)

        return node

    def delete_node(self: YAMLStorage, node_id: str) -> bool:
        """Delete a node from YAML files."""
        # Search through all directories to find and delete the node
        for layer_dir_name in self.layer_dirs.values():
            if layer_dir_name == "commands":
                file_path = self.commands_path / f"{node_id}.yaml"
            else:
                file_path = (
                    self.plans_path / layer_dir_name / f"{node_id}.yaml"
                )

            if file_path.exists():
                try:
                    file_path.unlink()
                    return True
                except (OSError, PermissionError) as e:
                    print(f"Error deleting {file_path}: {e}")

        return False

    def load_all_nodes(self) -> dict[str, list[Node]]:
        """Load all nodes from YAML files."""
        nodes: dict[str, list[Node]] = {}

        # Load from plans directory
        if self.plans_path.exists():
            for layer, dir_name in self.layer_dirs.items():
                if layer == "Command":
                    continue  # Commands are handled separately

                layer_path = self.plans_path / dir_name
                if layer_path.exists():
                    layer_nodes: list[Node] = []
                    invalid_nodes: list[tuple[Path, list[str]]] = []
                    for yaml_file in layer_path.glob("*.yaml"):
                        try:
                            with open(yaml_file, encoding="utf-8") as f:
                                yaml_data = yaml.safe_load(f)

                            # Validate the node data
                            if isinstance(yaml_data, dict):
                                yaml_data_dict = cast(
                                    "dict[str, Any]", yaml_data
                                )
                                is_valid, errors = validate_node_data(
                                    yaml_data_dict
                                )
                                if is_valid:
                                    node = self._yaml_to_node(yaml_data_dict)
                                    layer_nodes.append(node)
                                else:
                                    invalid_nodes.append((yaml_file, errors))
                            elif isinstance(yaml_data, list):
                                # Handle multi-node files
                                valid_yaml_nodes: list[dict[str, Any]] = []
                                for item in cast("list[Any]", yaml_data):
                                    if isinstance(item, dict):
                                        item_dict = cast(
                                            "dict[str, Any]", item
                                        )
                                        is_valid, errors = validate_node_data(
                                            item_dict
                                        )
                                        if is_valid:
                                            valid_yaml_nodes.append(item_dict)
                                        else:
                                            invalid_nodes.append(
                                                (yaml_file, errors)
                                            )
                                for valid_item in valid_yaml_nodes:
                                    node = self._yaml_to_node(valid_item)
                                    layer_nodes.append(node)
                            else:
                                invalid_nodes.append(
                                    (yaml_file, ["Invalid YAML structure"])
                                )

                        except (
                            yaml.YAMLError,
                            OSError,
                            PermissionError,
                            ValueError,
                        ) as e:
                            print(f"Error loading {yaml_file}: {e}")
                            invalid_nodes.append((yaml_file, [str(e)]))

                    # Report validation errors
                    for file_path, errors in invalid_nodes:
                        print(f"⚠️  Validation errors in {file_path}:")
                        for error in errors:
                            print(f"    - {error}")

                    if layer_nodes:
                        nodes[layer] = layer_nodes

        # Load commands
        if self.commands_path.exists():
            command_nodes: list[Node] = []
            invalid_command_nodes: list[tuple[Path, list[str]]] = []
            for yaml_file in self.commands_path.glob("*.yaml"):
                try:
                    with open(yaml_file, encoding="utf-8") as f:
                        yaml_data = yaml.safe_load(f)

                    # Validate the node data
                    if isinstance(yaml_data, dict):
                        yaml_data_dict = cast("dict[str, Any]", yaml_data)
                        is_valid, errors = validate_node_data(yaml_data_dict)
                        if is_valid:
                            node = self._yaml_to_node(yaml_data_dict)
                            command_nodes.append(node)
                        else:
                            invalid_command_nodes.append((yaml_file, errors))
                    elif isinstance(yaml_data, list):
                        # Handle multi-node files
                        valid_command_nodes: list[dict[str, Any]] = []
                        for item in cast("list[Any]", yaml_data):
                            if isinstance(item, dict):
                                item_dict = cast("dict[str, Any]", item)
                                is_valid, errors = validate_node_data(
                                    item_dict
                                )
                                if is_valid:
                                    valid_command_nodes.append(item_dict)
                                else:
                                    invalid_command_nodes.append(
                                        (yaml_file, errors)
                                    )
                        for valid_item in valid_command_nodes:
                            node = self._yaml_to_node(valid_item)
                            command_nodes.append(node)
                    else:
                        invalid_command_nodes.append(
                            (yaml_file, ["Invalid YAML structure"])
                        )

                except (
                    yaml.YAMLError,
                    OSError,
                    PermissionError,
                    ValueError,
                ) as e:
                    print(f"Error loading {yaml_file}: {e}")
                    invalid_command_nodes.append((yaml_file, [str(e)]))

            # Report validation errors
            for file_path, errors in invalid_command_nodes:
                print(f"⚠️  Validation errors in {file_path}:")
                for error in errors:
                    print(f"    - {error}")

            if command_nodes:
                nodes["Command"] = command_nodes

        return nodes

    def node_exists(self: YAMLStorage, node_id: str) -> bool:
        """Check if a node exists in YAML files."""
        return self.load_node(node_id) is not None

    def update_node_links(
        self, node_id: str, parents: list[str], children: list[str]
    ) -> bool:
        """Update node links in YAML file."""
        node = self.load_node(node_id)
        if not node:
            return False

        node.links.parents = parents
        node.links.children = children
        self.save_node(node)
        return True

    def get_nodes_by_layer(self: YAMLStorage, layer: str) -> list[Node]:
        """Get all nodes for a specific layer."""
        all_nodes = self.load_all_nodes()
        return all_nodes.get(layer, [])

    def count_nodes(self) -> int:
        """Count total number of nodes."""
        all_nodes = self.load_all_nodes()
        return sum(len(layer_nodes) for layer_nodes in all_nodes.values())
