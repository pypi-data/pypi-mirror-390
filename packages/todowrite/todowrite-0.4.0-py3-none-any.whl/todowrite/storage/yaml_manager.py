"""
YAML Import/Export Manager for ToDoWrite

This module handles importing YAML to database and exporting database content to YAML.
It supports the database-first approach with YAML as fallback.
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import jsonschema
import yaml
from sqlalchemy.exc import SQLAlchemyError

from ..core.constants import (
    DEFAULT_BASE_PATH,
    DEFAULT_COMMANDS_PATH,
    DEFAULT_PLANS_PATH,
    LAYER_DIRS,
)

if TYPE_CHECKING:
    from ..app import ToDoWrite
    from ..types import Node


class YAMLManager:
    """Manages YAML import/export operations for ToDoWrite."""

    def __init__(
        self: YAMLManager, todowrite_app: ToDoWrite | None = None
    ) -> None:
        """Initialize YAML Manager."""
        if todowrite_app is None:
            # Lazy import to avoid circular dependency
            from ..core import ToDoWrite

            self.app = ToDoWrite()
        else:
            self.app = todowrite_app
        self.yaml_base_path = Path(DEFAULT_BASE_PATH)
        self.plans_path = Path(DEFAULT_PLANS_PATH)
        self.commands_path = Path(DEFAULT_COMMANDS_PATH)
        self.layer_dirs = LAYER_DIRS

        # Cache for file system operations
        self._file_cache: dict[str, list[Path]] = {}
        self._cache_timestamp: float = 0
        self._cache_ttl: float = 60.0  # 1 minute cache

    def get_yaml_files(self) -> dict[str, list[Path]]:
        """Discover all YAML files in the configs directory with caching."""
        current_time = time.time()

        # Return cached results if still valid
        if (
            current_time - self._cache_timestamp < self._cache_ttl
            and self._file_cache
        ):
            return self._file_cache.copy()

        # Cache is invalid or empty, scan filesystem
        yaml_files = {}

        # Scan plans directory
        if self.plans_path.exists():
            for layer, dir_name in self.layer_dirs.items():
                if layer == "Command":
                    continue  # Commands are handled separately

                layer_path = self.plans_path / dir_name
                if layer_path.exists():
                    files = list(layer_path.glob("*.yaml")) + list(
                        layer_path.glob("*.yml")
                    )
                    if files:
                        yaml_files[layer] = files

        # Scan commands directory
        if self.commands_path.exists():
            command_files = list(self.commands_path.glob("*.yaml")) + list(
                self.commands_path.glob("*.yml")
            )
            if command_files:
                yaml_files["Command"] = command_files

        # Update cache
        self._file_cache = yaml_files.copy()
        self._cache_timestamp = current_time

        return cast("dict[str, list[Path]]", yaml_files)

    def load_yaml_file(
        self: YAMLManager, file_path: Path
    ) -> dict[str, Any] | None:
        """Load and validate a single YAML file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data: Any = yaml.safe_load(f)

            if not isinstance(data, dict):
                print(f"Warning: {file_path} is not a valid YAML object")
                return None

            # Basic validation
            required_fields = ["id", "layer", "title", "description"]
            for field in required_fields:
                if field not in data:
                    print(
                        f"Warning: {file_path} missing required field: {field}"
                    )
                    return None

            # Ensure metadata exists
            if "metadata" not in data:
                data["metadata"] = {"owner": "imported", "labels": []}

            # Ensure links exist
            if "links" not in data:
                data["links"] = {"parents": [], "children": []}

            return cast("dict[str, Any]", data)

        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {file_path}: {e}")
            return None
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except (PermissionError, OSError) as e:
            print(f"Unexpected error loading {file_path}: {e}")
            return None

    def get_existing_node_ids(self) -> set[str]:
        """Get all existing node IDs from the database."""
        try:
            with self.app.get_db_session() as session:
                from sqlalchemy import select

                from ..database.models import Node as DBNode

                stmt = select(DBNode.id)
                existing_ids = session.execute(stmt).scalars().all()
                return set(existing_ids)
        except SQLAlchemyError as e:
            print(f"Error querying database: {e}")
            return set()

    def import_yaml_files(
        self, force: bool = False, dry_run: bool = False
    ) -> dict[str, Any]:
        """Import YAML files to database."""
        results: dict[str, Any] = {
            "imported": [],
            "skipped": [],
            "errors": [],
            "total_files": 0,
            "total_imported": 0,
        }

        yaml_files = self.get_yaml_files()
        existing_ids: set[str] = (
            self.get_existing_node_ids() if not force else set()
        )

        print(f"🔍 Found YAML files in {len(yaml_files)} layers")

        for layer, files in yaml_files.items():
            print(f"\n📁 Processing {layer} layer ({len(files)} files)")

            for file_path in files:
                results["total_files"] += 1

                # Load YAML data
                yaml_data = self.load_yaml_file(file_path)
                if not yaml_data:
                    results["errors"].append(f"Failed to load {file_path}")
                    continue

                # Type assertion after None check
                yaml_data_dict: dict[str, Any] = yaml_data
                node_id = yaml_data_dict.get("id")

                # Check if node already exists
                if not force and node_id in existing_ids:
                    results["skipped"].append(f"{node_id} (already exists)")
                    print(f"  ⏭️  Skipped {node_id} (already exists)")
                    continue

                if dry_run:
                    results["imported"].append(f"{node_id} (DRY RUN)")
                    print(f"  🔍 Would import {node_id}")
                    continue

                # Import to database
                try:
                    if force and node_id and node_id in existing_ids:
                        # Update existing node
                        updated_node = self.app.update_node(
                            node_id, yaml_data_dict
                        )
                        if updated_node:
                            results["imported"].append(f"{node_id} (updated)")
                            results["total_imported"] += 1
                            print(f"  ✅ Updated {node_id}")
                        else:
                            results["errors"].append(
                                f"Failed to update {node_id}"
                            )
                            print(f"  ❌ Failed to update {node_id}")
                    else:
                        # Create new node
                        new_node = self.app.create_node(yaml_data_dict)
                        results["imported"].append(f"{new_node.id} (new)")
                        results["total_imported"] += 1
                        print(f"  ✅ Imported {new_node.id}")

                except (
                    ValueError,
                    KeyError,
                    AttributeError,
                    jsonschema.ValidationError,
                ) as e:
                    error_msg = f"Error importing {node_id}: {e}"
                    results["errors"].append(error_msg)
                    print(f"  ❌ {error_msg}")

        return results

    def export_to_yaml(
        self, output_dir: Path | None = None, backup_existing: bool = True
    ) -> dict[str, Any]:
        """Export database content to YAML files."""
        results: dict[str, Any] = {
            "exported": [],
            "errors": [],
            "total_nodes": 0,
            "total_exported": 0,
        }

        if output_dir is None:
            output_dir = self.yaml_base_path

        output_dir = Path(output_dir)

        # Backup existing files if requested
        if backup_existing and output_dir.exists():
            backup_dir = output_dir.parent / f"{output_dir.name}_backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.copytree(output_dir, backup_dir)
            print(f"📦 Created backup at {backup_dir}")

        # Create output directories
        plans_dir = output_dir / "plans"
        commands_dir = output_dir / "commands"

        try:
            # Get all nodes from database
            all_nodes = self.app.get_all_nodes()

            for layer, nodes in all_nodes.items():
                results["total_nodes"] += len(nodes)
                print(f"\n📁 Exporting {layer} layer ({len(nodes)} nodes)")

                # Determine output directory
                if layer == "Command":
                    layer_dir = commands_dir
                else:
                    dir_name = self.layer_dirs.get(layer)
                    if not dir_name:
                        results["errors"].append(f"Unknown layer: {layer}")
                        continue
                    layer_dir = plans_dir / dir_name

                # Create directory
                layer_dir.mkdir(parents=True, exist_ok=True)

                for node in nodes:
                    try:
                        # Convert node to YAML format
                        yaml_data = self.node_to_yaml(node)

                        # Write to file
                        file_path = layer_dir / f"{node.id}.yaml"
                        with open(file_path, "w", encoding="utf-8") as f:
                            yaml.dump(
                                yaml_data,
                                f,
                                default_flow_style=False,
                                sort_keys=False,
                            )

                        results["exported"].append(str(file_path))
                        results["total_exported"] += 1
                        print(f"  ✅ Exported {node.id}")

                    except (
                        OSError,
                        PermissionError,
                        yaml.YAMLError,
                        AttributeError,
                    ) as e:
                        error_msg = f"Error exporting {node.id}: {e}"
                        results["errors"].append(error_msg)
                        print(f"  ❌ {error_msg}")

        except (SQLAlchemyError, AttributeError, KeyError) as e:
            error_msg = f"Error accessing database: {e}"
            results["errors"].append(error_msg)
            print(f"❌ {error_msg}")

        return results

    def node_to_yaml(self: YAMLManager, node: Node) -> dict[str, Any]:
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

    def check_yaml_sync(self) -> dict[str, Any]:
        """Check synchronization status between YAML files and database."""
        results: dict[str, Any] = {
            "yaml_only": [],
            "database_only": [],
            "both": [],
            "conflicts": [],
        }

        # Get YAML node IDs
        yaml_files = self.get_yaml_files()
        yaml_ids: set[str] = set()
        for files in yaml_files.values():
            for file_path in files:
                yaml_data = self.load_yaml_file(file_path)
                if yaml_data and "id" in yaml_data:
                    yaml_ids.add(cast("str", yaml_data["id"]))

        # Get database node IDs
        db_ids = self.get_existing_node_ids()

        # Compare
        results["yaml_only"] = list(yaml_ids - db_ids)
        results["database_only"] = list(db_ids - yaml_ids)
        results["both"] = list(yaml_ids & db_ids)

        return results

    def auto_import_on_startup(self) -> None:
        """Automatically import YAML files that are not in the database."""
        print("🚀 Auto-importing YAML files on startup...")

        sync_status = self.check_yaml_sync()

        if not sync_status["yaml_only"]:
            print("✅ All YAML files are already in the database")
            return

        print(
            f"📥 Found {len(sync_status['yaml_only'])} YAML files not in database"
        )

        # Import only the missing files
        results = self.import_yaml_files(force=False, dry_run=False)

        print(
            f"✅ Auto-import completed: {results['total_imported']} files imported"
        )
        if results["errors"]:
            print(
                f"⚠️  {len(results['errors'])} errors occurred during auto-import"
            )
