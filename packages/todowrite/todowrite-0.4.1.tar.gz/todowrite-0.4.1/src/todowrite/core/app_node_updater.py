"""
Node Updater Helper Methods for ToDoWrite

This module contains helper methods to simplify the complex update_node method
by breaking it down into smaller, focused operations.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from sqlalchemy import delete, select

from ..database.models import Artifact, Command, Label, Link, Node

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class NodeUpdater:
    """Helper class to handle complex node update operations."""

    def __init__(self, session: Session) -> None:
        """Initialize with database session."""
        self.session = session

    def update_node_fields(
        self, db_node: Node, node_data: dict[str, Any]
    ) -> None:
        """Update basic node fields from node_data."""
        db_node.layer = node_data.get("layer", db_node.layer)
        db_node.title = node_data.get("title", db_node.title)
        db_node.description = node_data.get("description", db_node.description)
        db_node.status = node_data.get("status", db_node.status)
        db_node.progress = node_data.get("progress", db_node.progress)
        db_node.started_date = node_data.get(
            "started_date", db_node.started_date
        )
        db_node.completion_date = node_data.get(
            "completion_date", db_node.completion_date
        )

        # Update metadata fields
        metadata = node_data.get("metadata", {})
        db_node.owner = metadata.get("owner", db_node.owner)
        db_node.severity = metadata.get("severity", db_node.severity)
        db_node.work_type = metadata.get("work_type", db_node.work_type)
        db_node.assignee = metadata.get("assignee", db_node.assignee)

    def update_links(self, node_id: str, node_data: dict[str, Any]) -> None:
        """Update parent/child links for a node."""
        # Batch fetch both parent and child links in a single query
        parent_stmt = select(Link).where(Link.child_id == node_id)
        child_stmt = select(Link).where(Link.parent_id == node_id)

        parent_result = self.session.execute(parent_stmt).scalars().all()
        child_result = self.session.execute(child_stmt).scalars().all()

        existing_parent_links = {link.parent_id for link in parent_result}
        existing_child_links = {link.child_id for link in child_result}

        # Get new link IDs
        new_parent_ids = set(node_data.get("links", {}).get("parents", []))
        new_child_ids = set(node_data.get("links", {}).get("children", []))

        # Update parent links
        self._update_parent_links(
            node_id, new_parent_ids, existing_parent_links
        )

        # Update child links
        self._update_child_links(node_id, new_child_ids, existing_child_links)

    def _update_parent_links(
        self,
        node_id: str,
        new_parent_ids: set[str],
        existing_parent_links: set[str],
    ) -> None:
        """Update parent links for a node."""
        parents_to_add = new_parent_ids - existing_parent_links
        parents_to_remove = existing_parent_links - new_parent_ids

        for parent_id in parents_to_add:
            link = Link(parent_id=parent_id, child_id=node_id)
            self.session.add(link)

        for parent_id in parents_to_remove:
            delete_stmt = delete(Link).where(
                Link.parent_id == parent_id, Link.child_id == node_id
            )
            self.session.execute(delete_stmt)

    def _update_child_links(
        self,
        node_id: str,
        new_child_ids: set[str],
        existing_child_links: set[str],
    ) -> None:
        """Update child links for a node."""
        children_to_add = new_child_ids - existing_child_links
        children_to_remove = existing_child_links - new_child_ids

        for child_id in children_to_add:
            link = Link(parent_id=node_id, child_id=child_id)
            self.session.add(link)

        for child_id in children_to_remove:
            delete_stmt = delete(Link).where(
                Link.parent_id == node_id, Link.child_id == child_id
            )
            self.session.execute(delete_stmt)

    def update_labels(self, db_node: Node, node_data: dict[str, Any]) -> None:
        """Update labels for a node."""
        new_label_texts = set(node_data.get("metadata", {}).get("labels", []))

        # Get existing label texts for comparison
        existing_label_texts = {label.label for label in db_node.labels}

        # Clear all existing labels
        db_node.labels.clear()

        # Find labels that need to be updated (both existing and new)
        all_label_texts = new_label_texts.union(existing_label_texts)

        # Batch fetch all existing labels in a single query
        if all_label_texts:
            label_stmt = select(Label).where(Label.label.in_(all_label_texts))
            existing_labels = {
                label.label: label
                for label in self.session.execute(label_stmt).scalars().all()
            }

            # Update or create labels as needed
            for label_text in new_label_texts:
                if label_text in existing_labels:
                    db_node.labels.append(existing_labels[label_text])
                else:
                    new_label = Label(label=label_text)
                    self.session.add(new_label)
                    db_node.labels.append(new_label)

    def update_command(self, node_id: str, node_data: dict[str, Any]) -> None:
        """Update command information for a node."""
        if node_data.get("command"):
            self._update_existing_command(node_id, node_data["command"])
        else:
            self._delete_command_and_artifacts(node_id)

    def _update_existing_command(
        self, node_id: str, command_data: dict[str, Any]
    ) -> None:
        """Update an existing command for a node."""
        cmd_stmt = select(Command).where(Command.node_id == node_id)
        db_command = self.session.execute(cmd_stmt).scalar_one_or_none()

        if not db_command:
            db_command = Command(node_id=node_id)
            self.session.add(db_command)

        # Update command fields
        db_command.ac_ref = command_data.get("ac_ref", db_command.ac_ref)
        db_command.run = json.dumps(command_data.get("run", db_command.run))

        # Update artifacts
        self._update_command_artifacts(
            node_id, command_data.get("artifacts", [])
        )

    def _update_command_artifacts(
        self, node_id: str, artifacts: list[str]
    ) -> None:
        """Update artifacts for a command."""
        # Clear existing artifacts
        delete_artifacts_stmt = delete(Artifact).where(
            Artifact.command_id == node_id
        )
        self.session.execute(delete_artifacts_stmt)

        # Add new artifacts
        for artifact_text in artifacts:
            artifact = Artifact(command_id=node_id, artifact=artifact_text)
            self.session.add(artifact)

    def _delete_command_and_artifacts(self, node_id: str) -> None:
        """Delete command and its associated artifacts."""
        # Delete artifacts first (foreign key constraint)
        delete_artifacts_stmt = delete(Artifact).where(
            Artifact.command_id == node_id
        )
        self.session.execute(delete_artifacts_stmt)

        # Delete command
        delete_cmd_stmt = delete(Command).where(Command.node_id == node_id)
        self.session.execute(delete_cmd_stmt)
