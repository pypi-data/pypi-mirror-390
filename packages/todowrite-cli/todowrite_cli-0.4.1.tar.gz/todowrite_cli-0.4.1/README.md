# ToDoWrite CLI

A command-line interface for managing complex software projects with Goals, Tasks, Concepts, and Commands.

## Prerequisites

You must first install the todowrite library:
```bash
pip install todowrite
```

## Installation

```bash
pip install todowrite-cli
```

For PostgreSQL support:
```bash
pip install 'todowrite-cli[postgres]'
```

## Quick Start

### Initialize a project

```bash
todowrite init
```

### Create a Goal

```bash
todowrite create --layer goal --title "Implement User Authentication" --description "Create secure user authentication system"
```

### Create a Task

```bash
todowrite create --layer task --title "Design Database Schema" --description "Design and implement database schema for users"
```

### Create a Concept

```bash
todowrite create --layer concept --title "OAuth2 Flow" --description "OAuth2 authentication flow implementation"
```

### Create a Command

```bash
todowrite create --layer command --title "Build Project" --description "Build the entire project"
```

### Link Nodes

```bash
# Use the update command to add parent-child relationships
todowrite update --id "TSK-001" --add-parent "GOAL-001"
```

### Update Progress

```bash
todowrite update --id "TSK-001" --status in_progress --progress 50
```

### View Project Status

```bash
todowrite list
todowrite get --id "GOAL-001"
```

### Import/Export YAML

```bash
todowrite import-yaml
todowrite export-yaml
```

## Commands

### Project Management
- `init` - Initialize a new project
- `create` - Create new nodes (goals, tasks, concepts, commands)
- `get` - Get a specific node by ID
- `list` - List all nodes with their status
- `status show` - Show detailed information about a specific node

### Status Management
- `status update` - Update node status and progress
- `status complete` - Mark a node as completed
- `status list` - List all nodes with their status

### Import/Export
- `import-yaml` - Import nodes from YAML files
- `export-yaml` - Export nodes to YAML files
- `sync-status` - Check synchronization status between YAML files and database

### Database Management
- `db-status` - Show storage configuration and status

## Configuration

Configuration is stored in `~/.todowrite/config.yaml`:

```yaml
database:
  default_path: "./todowrite.db"
  storage: "sqlite"  # or "postgresql"

yaml:
  base_path: "./configs"

ui:
  colors: true
  table_format: "fancy_grid"
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/dderyldowney/todowrite.git
cd todowrite/cli_package
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
