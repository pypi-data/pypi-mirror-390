"""
Shared constants for ToDoWrite
"""

from __future__ import annotations

# Layer to directory mapping - used across multiple modules
LAYER_DIRS = {
    "Goal": "goals",
    "Concept": "concepts",
    "Context": "contexts",
    "Constraints": "constraints",
    "Requirements": "requirements",
    "AcceptanceCriteria": "acceptance_criteria",
    "InterfaceContract": "interface_contracts",
    "Phase": "phases",
    "Step": "steps",
    "Task": "tasks",
    "SubTask": "subtasks",
    "Command": "commands",  # Special case - goes in commands/ not plans/
}

# Default base paths
DEFAULT_BASE_PATH = "configs"
DEFAULT_PLANS_PATH = "configs/plans"
DEFAULT_COMMANDS_PATH = "configs/commands"
