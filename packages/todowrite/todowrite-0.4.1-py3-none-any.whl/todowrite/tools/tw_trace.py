#!/usr/bin/env python3
"""
ToDoWrite Traceability Builder (tw_trace.py)
Builds forward/backward traceability matrix and dependency graph
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


class TraceabilityBuilder:
    """Builds traceability matrix and dependency graph for ToDoWrite framework"""

    def __init__(self) -> None:
        self.nodes: dict[str, dict[str, Any]] = {}
        self.forward_links: dict[str, set[str]] = defaultdict(set)
        self.backward_links: dict[str, set[str]] = defaultdict(set)
        self.orphaned_nodes: set[str] = set()
        self.circular_deps: list[list[str]] = []

    def _find_yaml_files(self) -> list[Path]:
        """Find all YAML files in configs/plans/* and configs/commands/* directories"""
        yaml_files: list[Path] = []

        # Plans directory (layers 1-11)
        plans_dir = Path("configs/plans")
        if plans_dir.exists():
            for subdir in plans_dir.iterdir():
                if subdir.is_dir():
                    yaml_files.extend(subdir.glob("*.yaml"))

        # Commands directory (layer 12)
        commands_dir = Path("configs/commands")
        if commands_dir.exists():
            yaml_files.extend(commands_dir.glob("*.yaml"))

        return sorted(yaml_files)

    def _load_yaml_file(self, file_path: Path) -> tuple[dict[str, Any], bool]:
        """Load and parse YAML file, return (data, success)"""
        try:
            with open(file_path) as f:
                data = yaml.safe_load(f)
            return data, True
        except yaml.YAMLError as e:
            print(f"ERROR: Invalid YAML in {file_path}: {e}")
            return {}, False
        except Exception as e:
            print(f"ERROR: Failed to read {file_path}: {e}")
            return {}, False

    def load_all_nodes(self) -> bool:
        """Load all nodes from YAML files"""
        yaml_files = self._find_yaml_files()

        if not yaml_files:
            print("No YAML files found in configs/plans/ or configs/commands/")
            return False

        print(f"Loading {len(yaml_files)} YAML files...")

        for file_path in yaml_files:
            data, success = self._load_yaml_file(file_path)
            if not success:
                continue

            if not data or "id" not in data:
                print(f"WARNING: Invalid node structure in {file_path}")
                continue

            node_id = data["id"]
            self.nodes[node_id] = {
                "id": node_id,
                "layer": data.get("layer", "Unknown"),
                "title": data.get("title", ""),
                "file_path": str(file_path),
                "parents": data.get("links", {}).get("parents", []),
                "children": data.get("links", {}).get("children", []),
            }

        print(f"Loaded {len(self.nodes)} nodes")
        return True

    def build_links(self) -> None:
        """Build forward and backward link mappings"""
        print("Building link mappings...")

        for node_id, node_data in self.nodes.items():
            # Forward links (this node -> its children)
            for child_id in node_data["children"]:
                self.forward_links[node_id].add(child_id)

            # Backward links (this node <- its parents)
            for parent_id in node_data["parents"]:
                self.backward_links[node_id].add(parent_id)

        # Verify bidirectional consistency
        inconsistencies: list[str] = []
        for node_id, children in self.forward_links.items():
            for child_id in children:
                if node_id not in self.backward_links.get(child_id, set()):
                    inconsistencies.append(
                        f"{node_id} -> {child_id} (missing backward link)"
                    )

        for node_id, parents in self.backward_links.items():
            for parent_id in parents:
                if node_id not in self.forward_links.get(parent_id, set()):
                    inconsistencies.append(
                        f"{parent_id} -> {node_id} (missing forward link)"
                    )

        if inconsistencies:
            print("WARNING: Link inconsistencies found:")
            for inconsistency in inconsistencies[:10]:  # Show first 10
                print(f"  {inconsistency}")
            if len(inconsistencies) > 10:
                print(f"  ... and {len(inconsistencies) - 10} more")

    def find_orphaned_nodes(self) -> None:
        """Find nodes with no parents or children"""
        print("Identifying orphaned nodes...")

        for node_id, node_data in self.nodes.items():
            has_parents = bool(node_data["parents"])
            has_children = bool(node_data["children"])

            # Goal nodes can have no parents, Command nodes can have no children
            layer = node_data["layer"]
            if (
                (layer == "Goal" and not has_children)
                or (layer == "Command" and not has_parents)
                or (not has_parents and not has_children)
            ):
                self.orphaned_nodes.add(node_id)

    def detect_circular_dependencies(self) -> None:
        """Detect circular dependencies using DFS"""
        print("Checking for circular dependencies...")

        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node_id: str, path: list[str]) -> bool:
            if node_id in rec_stack:
                # Found cycle
                cycle_start = path.index(node_id)
                cycle = [*path[cycle_start:], node_id]
                self.circular_deps.append(cycle)
                return True

            if node_id in visited:
                return False

            visited.add(node_id)
            rec_stack.add(node_id)

            for child_id in self.forward_links.get(node_id, []):
                if dfs(child_id, [*path, node_id]):
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id, [])

    def export_trace_csv(self) -> None:
        """Export traceability matrix to trace/trace.csv"""
        trace_dir = Path("trace")
        trace_dir.mkdir(exist_ok=True)

        csv_file = trace_dir / "trace.csv"
        print(f"Exporting traceability matrix to {csv_file}...")

        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(
                [
                    "source_id",
                    "source_layer",
                    "source_title",
                    "target_id",
                    "target_layer",
                    "target_title",
                    "relationship",
                    "depth",
                ]
            )

            # Forward relationships (parent -> child)
            for source_id, children in self.forward_links.items():
                source_node = self.nodes.get(source_id, {})
                for target_id in children:
                    target_node = self.nodes.get(target_id, {})
                    writer.writerow(
                        [
                            source_id,
                            source_node.get("layer", ""),
                            source_node.get("title", ""),
                            target_id,
                            target_node.get("layer", ""),
                            target_node.get("title", ""),
                            "parent_of",
                            1,
                        ]
                    )

            # Backward relationships (child -> parent)
            for target_id, parents in self.backward_links.items():
                target_node = self.nodes.get(target_id, {})
                for source_id in parents:
                    source_node = self.nodes.get(source_id, {})
                    writer.writerow(
                        [
                            target_id,
                            target_node.get("layer", ""),
                            target_node.get("title", ""),
                            source_id,
                            source_node.get("layer", ""),
                            source_node.get("title", ""),
                            "child_of",
                            1,
                        ]
                    )

    def export_graph_json(self) -> None:
        """Export dependency graph to trace/graph.json"""
        trace_dir = Path("trace")
        trace_dir.mkdir(exist_ok=True)

        graph_file = trace_dir / "graph.json"
        print(f"Exporting dependency graph to {graph_file}...")

        # Build node list
        nodes: list[dict[str, Any]] = []
        for node_id, node_data in self.nodes.items():
            nodes.append(
                {
                    "id": node_id,
                    "label": node_data["title"],
                    "layer": node_data["layer"],
                    "file_path": node_data["file_path"],
                    "is_orphaned": node_id in self.orphaned_nodes,
                }
            )

        # Build edge list
        edges: list[dict[str, Any]] = []
        for source_id, children in self.forward_links.items():
            for target_id in children:
                edges.append(
                    {
                        "source": source_id,
                        "target": target_id,
                        "type": "parent_child",
                    }
                )

        # Graph data structure
        graph: dict[str, Any] = {
            "metadata": {
                "total_nodes": len(self.nodes),
                "total_edges": len(edges),
                "orphaned_nodes": len(self.orphaned_nodes),
                "circular_dependencies": len(self.circular_deps),
                "layers": list(
                    {node["layer"] for node in self.nodes.values()}
                ),
            },
            "nodes": nodes,
            "edges": edges,
            "issues": {
                "orphaned_nodes": list(self.orphaned_nodes),
                "circular_dependencies": [
                    list(cycle) for cycle in self.circular_deps
                ],
            },
        }

        with open(graph_file, "w") as f:
            json.dump(graph, f, indent=2)

    def generate_summary(self) -> None:
        """Generate traceability analysis summary"""
        print("=" * 60)
        print("TRACEABILITY ANALYSIS SUMMARY")
        print("=" * 60)

        # Node statistics
        layer_counts: dict[str, int] = defaultdict(int)
        for node_data in self.nodes.values():
            layer_counts[node_data["layer"]] += 1

        print(f"Total nodes: {len(self.nodes)}")
        print("\nNodes by layer:")
        for layer, count in sorted(layer_counts.items()):
            print(f"  {layer}: {count}")

        # Link statistics
        total_forward_links = sum(
            len(children) for children in self.forward_links.values()
        )
        total_backward_links = sum(
            len(parents) for parents in self.backward_links.values()
        )

        print(f"\nTotal forward links: {total_forward_links}")
        print(f"Total backward links: {total_backward_links}")

        # Issues
        print(f"\nOrphaned nodes: {len(self.orphaned_nodes)}")
        if self.orphaned_nodes:
            print("  " + ", ".join(list(self.orphaned_nodes)[:5]))
            if len(self.orphaned_nodes) > 5:
                print(f"  ... and {len(self.orphaned_nodes) - 5} more")

        print(f"Circular dependencies: {len(self.circular_deps)}")
        if self.circular_deps:
            for i, cycle in enumerate(self.circular_deps[:3]):
                print(f"  Cycle {i + 1}: {' -> '.join(cycle)}")
            if len(self.circular_deps) > 3:
                print(f"  ... and {len(self.circular_deps) - 3} more")

        # Overall status
        has_issues = bool(self.orphaned_nodes or self.circular_deps)
        status = "ISSUES FOUND" if has_issues else "HEALTHY"
        print(f"\nTraceability Status: {status}")
        print("=" * 60)

    def build_all(self) -> bool:
        """Build complete traceability analysis"""
        if not self.load_all_nodes():
            return False

        self.build_links()
        self.find_orphaned_nodes()
        self.detect_circular_dependencies()
        self.export_trace_csv()
        self.export_graph_json()

        return True


def main() -> None:
    """Main entry point for tw_trace.py"""
    parser = argparse.ArgumentParser(
        description="Build ToDoWrite traceability matrix and dependency graph"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Show summary report only"
    )
    parser.add_argument(
        "--ignore-issues",
        action="store_true",
        help="Ignore traceability issues and don't exit with error code",
    )

    args = parser.parse_args()

    # Initialize builder
    builder = TraceabilityBuilder()

    # Build traceability analysis
    success = builder.build_all()

    if not success:
        sys.exit(1)

    # Generate summary
    print()
    builder.generate_summary()

    # Exit based on whether issues were found
    has_issues = bool(builder.orphaned_nodes or builder.circular_deps)
    if args.ignore_issues:
        # Exit with 0 even if issues found
        sys.exit(0)
    else:
        # Exit with 1 if issues found, 0 if no issues
        sys.exit(1 if has_issues else 0)


if __name__ == "__main__":
    main()
