# ToDoWrite

A Python library for managing complex software projects with Goals, Tasks, Concepts, and Commands.

## Installation

```bash
pip install todowrite
```

For PostgreSQL support:
```bash
pip install 'todowrite[postgres]'
```

## Quick Start

### Basic Usage

```python
from todowrite import ToDoWrite

# Initialize the application
app = ToDoWrite("sqlite:///myproject.db")
app.init_database()

# Create a goal
goal_data = {
    "id": "GOAL-001",
    "layer": "Goal",
    "title": "Implement User Authentication",
    "description": "Create secure user authentication system",
    "metadata": {
        "owner": "developer1",
        "labels": ["security", "auth"],
        "severity": "high",
        "work_type": "implementation"
    }
}
goal = app.create_node(goal_data)

# Create a task
task_data = {
    "id": "TSK-001",
    "layer": "Task",
    "title": "Design Database Schema",
    "description": "Design and implement database schema for users",
    "metadata": {
        "owner": "developer1",
        "labels": ["database"],
        "severity": "medium",
        "work_type": "design"
    }
}
task = app.create_node(task_data)

# Link task to goal
app.link_nodes("GOAL-001", "TSK-001")

# Update progress (progress field is now properly preserved)
app.update_node("TSK-001", {"status": "in_progress", "progress": 50})
```

### Using Different Storage Backends

#### SQLite
```python
app = ToDoWrite("sqlite:///project.db")
app.init_database()
```

#### PostgreSQL
```python
app = ToDoWrite("postgresql://user:password@localhost/projectdb")
app.init_database()
```

#### YAML Storage
```python
app = ToDoWrite("sqlite:///project.db", yaml_base_path="./configs")
app.init_database()
```

### Node Types

#### Goals
```python
goal_data = {
    "id": "GOAL-001",
    "layer": "Goal",
    "title": "Project Goal",
    "description": "High-level project objective",
    "metadata": {
        "owner": "project_manager",
        "labels": ["strategic"],
        "severity": "high",
        "work_type": "planning"
    }
}
```

#### Tasks
```python
task_data = {
    "id": "TSK-001",
    "layer": "Task",
    "title": "Implementation Task",
    "description": "Detailed implementation work",
    "metadata": {
        "owner": "developer",
        "labels": ["implementation"],
        "severity": "medium",
        "work_type": "development"
    }
}
```

#### Concepts
```python
concept_data = {
    "id": "CON-001",
    "layer": "Concept",
    "title": "Design Pattern",
    "description": "Architectural concept or pattern",
    "metadata": {
        "owner": "architect",
        "labels": ["architecture"],
        "severity": "low",
        "work_type": "research"
    }
}
```

#### Commands
```python
command_data = {
    "id": "CMD-001",
    "layer": "Command",
    "title": "Build Command",
    "description": "Automated build process",
    "command": {
        "ac_ref": "AC-001",
        "run": {
            "shell": "make build",
            "workdir": "/project",
            "env": {"TARGET": "production"}
        },
        "artifacts": ["dist/", "build.log"]
    },
    "metadata": {
        "owner": "ci",
        "labels": ["automation"],
        "severity": "critical",
        "work_type": "automation"
    }
}
```

### Advanced Operations

#### Complex Hierarchies
```python
# Create a multi-level hierarchy
goal = app.create_node({
    "id": "GOAL-001",
    "layer": "Goal",
    "title": "Main Project Goal"
})

concept1 = app.create_node({
    "id": "CON-001",
    "layer": "Concept",
    "title": "Architecture Concept"
})

concept2 = app.create_node({
    "id": "CON-002",
    "layer": "Concept",
    "title": "Security Concept"
})

task1 = app.create_node({
    "id": "TSK-001",
    "layer": "Task",
    "title": "Implementation Task 1"
})

task2 = app.create_node({
    "id": "TSK-002",
    "layer": "Task",
    "title": "Implementation Task 2"
})

# Link everything together
app.link_nodes("GOAL-001", "CON-001")
app.link_nodes("GOAL-001", "CON-002")
app.link_nodes("GOAL-001", "TSK-001")
app.link_nodes("GOAL-001", "TSK-002")
```

#### Batch Operations
```python
# Create multiple nodes
nodes_data = [
    {"id": "GOAL-001", "layer": "Goal", "title": "Goal 1"},
    {"id": "GOAL-002", "layer": "Goal", "title": "Goal 2"},
    {"id": "TSK-001", "layer": "Task", "title": "Task 1"},
    {"id": "TSK-002", "layer": "Task", "title": "Task 2"}
]

for node_data in nodes_data:
    app.create_node(node_data)

# Get all goals
goals = app.get_nodes("Goal")
```

#### Querying and Filtering
```python
# Get nodes by status
incomplete_tasks = app.get_nodes("Task", {"status": "in_progress"})

# Get nodes by owner
developer_tasks = app.get_nodes("Task", {"owner": "developer1"})

# Get nodes by label
critical_nodes = app.get_nodes_by_label("critical")

# Get node with links
node_with_links = app.get_node_with_links("GOAL-001")
```

### YAML Integration

```python
# Export nodes to JSON/YAML
from todowrite import export_nodes, import_nodes

# Export to file
exported_nodes = export_nodes(db_url, "export.json")

# Import from file
import_results = import_nodes(db_url, "export.json")
print(f"Imported: {import_results['imported']}, Errors: {import_results['errors']}")

# YAML Manager for advanced operations
from todowrite.storage import YAMLManager

yaml_manager = YAMLManager("project.yaml")
yaml_manager.write_yaml({"nodes": {}})
data = yaml_manager.read_yaml()
```

### Validation

```python
# Validate node data
from todowrite.storage import validate_node_data

try:
    validate_node_data(node_data)
    print("Node data is valid")
except Exception as e:
    print(f"Invalid node data: {e}")

# Validate database schema
from todowrite.storage import validate_database_schema

schema_valid = validate_database_schema(db_url)
```

### Custom Metadata

```python
# Add custom metadata fields
node_data = {
    "id": "GOAL-001",
    "layer": "Goal",
    "title": "Custom Goal",
    "metadata": {
        "owner": "developer",
        "labels": ["custom"],
        "severity": "medium",
        "work_type": "implementation",
        "custom_field": "custom_value",
        "another_field": 42
    }
}
```

## API Reference

### Core Classes

- `ToDoWrite` - Main application class
- `Node` - Represents a goal, task, concept, or command
- `LayerType` - Enum for node layers (Goal, Task, Concept, Command)
- `StatusType` - Enum for node status (planned, in_progress, completed, blocked)

### Core Methods

- `init_database()` - Initialize database schema
- `create_node(data)` - Create a new node
- `get_node(id)` - Get a specific node
- `get_nodes(layer, filters)` - Get nodes by layer and filters
- `update_node(id, data)` - Update an existing node
- `delete_node(id)` - Delete a node
- `link_nodes(parent_id, child_id)` - Create parent-child relationship
- `get_node_with_links(id)` - Get node with all its relationships

### Storage Classes

- `YAMLManager` - YAML import/export operations
- `YAMLStorage` - YAML storage backend
- Validators for data integrity

## Development

### Setup Development Environment

```bash
git clone https://github.com/dderyldowney/todowrite.git
cd todowrite/lib_package
pip install -e .[dev]
```

### Run Tests

```bash
pytest tests/
```

### Run Linters

```bash
black .
isort .
flake8 .
pyright .
```

### Pre-commit Hooks

```bash
pre-commit install
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
