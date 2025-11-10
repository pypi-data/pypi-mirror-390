"""Schema definitions for ToDoWrite."""

import json
from pathlib import Path

# Load the schema from the JSON file
SCHEMA_PATH = Path(__file__).parent / "todowrite.schema.json"
with open(SCHEMA_PATH) as f:
    TODOWRITE_SCHEMA = json.load(f)

__all__ = ["TODOWRITE_SCHEMA"]
