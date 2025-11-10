"""
Type definitions for ToDoWrite package.

This module contains shared type definitions to avoid circular imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# pyright: reportUnknownVariableType=none


LayerType = Literal[
    "Goal",
    "Concept",
    "Context",
    "Constraints",
    "Requirements",
    "AcceptanceCriteria",
    "InterfaceContract",
    "Phase",
    "Step",
    "Task",
    "SubTask",
    "Command",
]

StatusType = Literal[
    "planned", "in_progress", "completed", "blocked", "cancelled"
]


@dataclass
class Metadata:
    """Metadata for a node."""

    owner: str = ""
    labels: list[str] = field(default_factory=list)
    severity: str = "low"
    work_type: str = "chore"
    assignee: str = ""


@dataclass
class Link:
    """Link between nodes."""

    parents: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)


@dataclass
class Command:
    """Command definition."""

    ac_ref: str = ""
    run: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)


@dataclass
class Label:
    """Represents a label for categorization and tagging."""

    name: str = ""
    description: str = ""


@dataclass
class Node:
    """Represents a node in the ToDoWrite system."""

    id: str
    layer: LayerType
    title: str
    description: str = ""
    status: StatusType = "planned"
    progress: int = 0
    started_date: str | None = None
    completion_date: str | None = None
    links: Link = field(default_factory=Link)
    metadata: Metadata = field(default_factory=Metadata)
    command: Command | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary representation."""
        result: dict[str, Any] = {
            "id": self.id,
            "layer": self.layer,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "links": {
                "parents": self.links.parents,
                "children": self.links.children,
            },
            "metadata": {
                "owner": self.metadata.owner,
                "labels": self.metadata.labels,
                "severity": self.metadata.severity,
                "work_type": self.metadata.work_type,
                "assignee": self.metadata.assignee,
            },
        }

        # Add optional status tracking fields
        if self.progress is not None:
            result["progress"] = self.progress
        if self.started_date is not None:
            result["started_date"] = str(self.started_date)
        if self.completion_date is not None:
            result["completion_date"] = str(self.completion_date)
        if self.metadata.assignee:
            result["assignee"] = self.metadata.assignee

        if self.command:
            result["command"] = {
                "ac_ref": self.command.ac_ref,
                "run": self.command.run,
                "artifacts": self.command.artifacts,
            }

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Node:
        """Create node from dictionary representation."""
        links_data = data.get("links", {})
        metadata_data = data.get("metadata", {})
        command_data = data.get("command")

        links = Link(
            parents=links_data.get("parents", []),
            children=links_data.get("children", []),
        )

        metadata = Metadata(
            owner=metadata_data.get("owner", "system"),
            labels=metadata_data.get("labels", []),
            severity=metadata_data.get("severity", ""),
            work_type=metadata_data.get("work_type", ""),
            assignee=metadata_data.get("assignee", ""),
        )

        command = None
        if command_data:
            command = Command(
                ac_ref=command_data.get("ac_ref", ""),
                run=command_data.get("run", {}),
                artifacts=command_data.get("artifacts", []),
            )

        return cls(
            id=data["id"],
            layer=data["layer"],
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "planned"),
            progress=data.get("progress", 0),
            started_date=data.get("started_date"),
            completion_date=data.get("completion_date"),
            links=links,
            metadata=metadata,
            command=command,
        )
