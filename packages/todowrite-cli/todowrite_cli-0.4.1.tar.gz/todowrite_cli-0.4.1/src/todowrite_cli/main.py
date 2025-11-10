"""Main CLI entry point for ToDoWrite."""

import getpass
import os
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any, cast

import click
import jsonschema
from rich.console import Console
from rich.table import Table

from .version import __version__

# Import from the todowrite library
try:
    from todowrite import (
        YAMLManager,
        create_node,
        delete_node,
        get_node,
        list_nodes,
        search_nodes,
        update_node,
        validate_node,
        validate_schema,
    )
    from todowrite.core import Node, ToDoWrite, generate_node_id
    from todowrite.storage import get_schema_compliance_report
except ImportError:
    click.echo(
        "Error: todowrite library not found. Please install it first: "
        "pip install todowrite",
    )
    sys.exit(1)


console = Console()


def get_current_username() -> str:
    """Get the current username from environment or system."""
    try:
        # Try environment variables first
        username = (
            os.environ.get("USER")
            or os.environ.get("USERNAME")
            or os.environ.get("LOGNAME")
        )
        if username:
            return username

        # Fallback to system calls
        try:
            return getpass.getuser()
        except OSError:
            # Final fallback - try a system call
            import pwd

            return pwd.getpwuid(os.getuid()).pw_name
    except Exception:
        # Ultimate fallback
        return "system"


def capitalize_status(status: str) -> str:
    """Capitalize status for display (e.g., 'in_progress' -> 'In Progress')."""
    status_mapping = {
        "planned": "Planned",
        "in_progress": "In Progress",
        "completed": "Completed",
        "blocked": "Blocked",
        "cancelled": "Cancelled",
    }
    return status_mapping.get(status, status.title())


def get_app(
    database_path: str | None = None,
    _yaml_base_path: str | None = None,
) -> ToDoWrite:
    """Get or create ToDoWrite application instance."""
    if database_path:
        # Convert file path to SQLite URL
        if not database_path.startswith(("sqlite:///", "postgresql://")):
            db_url = f"sqlite:///{database_path}"
        else:
            db_url = database_path
        app = ToDoWrite(db_url)
    else:
        # Try to get from config file or use default
        config_path = Path.home() / ".todowrite" / "config.yaml"
        if config_path.exists():
            import yaml

            with open(config_path) as f:
                config = yaml.safe_load(f)
            db_path = config.get("database", {}).get(
                "default_path", "./todowrite.db"
            )
            if not db_path.startswith(("sqlite:///", "postgresql://")):
                db_url = f"sqlite:///{db_path}"
            else:
                db_url = db_path
            app = ToDoWrite(db_url)
        else:
            app = ToDoWrite("sqlite:///./todowrite.db")

    with suppress(Exception):
        app.init_database()
    return app


@click.group()
@click.version_option(version=__version__)
@click.option(
    "--storage-preference",
    type=click.Choice(["auto", "postgresql_only", "sqlite_only", "yaml_only"]),
    default="auto",
    help="Override default storage preference",
)
@click.pass_context
def cli(ctx: click.Context, storage_preference: str) -> None:
    """A CLI for the ToDoWrite application."""
    ctx.ensure_object(dict)
    ctx.obj["storage_preference"] = storage_preference


@cli.command()
@click.option(
    "--database-path",
    "-d",
    default=None,
    help="Database file path (default: ./todowrite.db)",
)
@click.option(
    "--yaml-path",
    "-y",
    default=None,
    help="YAML configuration path (default: ./configs)",
)
def init(database_path: str | None, yaml_path: str | None) -> None:
    """Initialize the database."""
    app = get_app(database_path, yaml_path)

    try:
        app.init_database()
        console.print("[green]✓[/green] Database initialized successfully!")
        if database_path:
            console.print(f"Database path: {database_path}")
        if yaml_path:
            console.print(f"YAML path: {yaml_path}")
    except (OSError, ValueError, RuntimeError) as e:
        console.print(f"[red]✗[/red] Error initializing database: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--layer",
    "-l",
    help=(
        "Layer type (case-insensitive: goal, concept, context, constraints, "
        "requirements, acceptancecriteria, interfacecontract, phase, step, "
        "task, subtask, command)"
    ),
    required=True,
)
@click.option(
    "--title",
    "-t",
    required=True,
    help="Title of the node",
)
@click.option(
    "--description",
    "-d",
    help="Description of the node",
)
@click.option(
    "--owner",
    help="Owner of the node",
)
@click.option(
    "--labels",
    help="Comma-separated labels",
)
@click.option(
    "--severity",
    help="Severity level (case-insensitive: low, med, medium, high, critical)",
)
@click.option(
    "--work-type",
    help="Type of work",
)
@click.option(
    "--ac-ref",
    help="Acceptance criteria reference (for Commands)",
)
@click.option(
    "--run-shell",
    help="Shell command to run (for Commands)",
)
@click.option(
    "--artifacts",
    help="Comma-separated artifact paths (for Commands)",
)
@click.pass_context
def create(
    _: click.Context,
    layer: str,
    title: str,
    description: str,
    owner: str | None,
    labels: str | None,
    severity: str | None,
    work_type: str | None,
    ac_ref: str | None,
    run_shell: str | None,
    artifacts: str | None,
) -> None:
    """Creates a new node."""
    # Convert layer input to proper case (case-insensitive)
    layer_mapping = {
        "goal": "Goal",
        "concept": "Concept",
        "context": "Context",
        "constraints": "Constraints",
        "requirements": "Requirements",
        "acceptancecriteria": "AcceptanceCriteria",
        "acceptance_criteria": "AcceptanceCriteria",
        "acceptance-criteria": "AcceptanceCriteria",
        "interfacecontract": "InterfaceContract",
        "interface_contract": "InterfaceContract",
        "interface-contract": "InterfaceContract",
        "phase": "Phase",
        "step": "Step",
        "task": "Task",
        "subtask": "SubTask",
        "sub_task": "SubTask",
        "sub-task": "SubTask",
        "command": "Command",
    }

    # Normalize layer input
    layer_normalized = layer_mapping.get(layer.lower())
    if not layer_normalized:
        valid_options = ", ".join(sorted(layer_mapping.keys()))
        console.print(
            f"[red]✗[/red] Invalid layer: '{layer}'. "
            f"Valid options: {valid_options}"
        )
        sys.exit(1)

    layer = layer_normalized

    # Map layer types to schema prefixes
    layer_prefixes = {
        "Goal": "GOAL",
        "Concept": "CON",
        "Context": "CTX",
        "Constraints": "CST",
        "Requirements": "R",
        "AcceptanceCriteria": "AC",
        "InterfaceContract": "IF",
        "Phase": "PH",
        "Step": "STP",
        "Task": "TSK",
        "SubTask": "SUB",
        "Command": "CMD",
    }

    # Build node data
    prefix = layer_prefixes.get(layer, layer[:3].upper())
    node_data: dict[str, Any] = {
        "id": generate_node_id(prefix),
        "layer": layer,
        "title": title,
        "description": description or "",
        "links": {"parents": [], "children": []},
        "metadata": {},
    }

    # Add metadata
    metadata = cast("dict[str, Any]", node_data["metadata"])
    # Set owner to provided owner or current user
    metadata["owner"] = owner or get_current_username()
    if labels:
        metadata["labels"] = [label.strip() for label in labels.split(",")]
    if severity:
        # Convert severity input to proper case (case-insensitive)
        severity_mapping = {
            "low": "low",
            "medium": "medium",
            "med": "medium",
            "high": "high",
            "critical": "critical",
        }

        severity_normalized = severity_mapping.get(severity.lower())
        if not severity_normalized:
            valid_severities = ", ".join(sorted(severity_mapping.keys()))
            error_msg = (
                f"[red]✗[/red] Invalid severity: '{severity}'. "
                f"Valid options: {valid_severities}"
            )
            console.print(error_msg)
            sys.exit(1)

        metadata["severity"] = severity_normalized

    if work_type:
        # Convert work_type input to proper case (case-insensitive)
        work_type_mapping = {
            "architecture": "architecture",
            "spec": "spec",
            "interface": "interface",
            "validation": "validation",
            "implementation": "implementation",
            "development": "implementation",
            "docs": "docs",
            "operations": "ops",
            "ops": "ops",
            "refactor": "refactor",
            "chore": "chore",
            "test": "test",
        }

        work_type_normalized = work_type_mapping.get(work_type.lower())
        if not work_type_normalized:
            valid_work_types = ", ".join(sorted(work_type_mapping.keys()))
            error_msg = (
                f"[red]✗[/red] Invalid work_type: '{work_type}'. "
                f"Valid options: {valid_work_types}"
            )
            console.print(error_msg)
            sys.exit(1)

        metadata["work_type"] = work_type_normalized

    # Add command-specific data
    if layer == "Command":
        node_data["command"] = {}
        command = cast("dict[str, Any]", node_data["command"])
        if ac_ref:
            command["ac_ref"] = ac_ref
        command["run"] = {}
        if run_shell:
            command["run"]["shell"] = run_shell
        if artifacts:
            command["artifacts"] = [
                artifact.strip() for artifact in artifacts.split(",")
            ]

    try:
        # Validate data before creating
        validate_node(node_data)
        node = create_node(node_data)
        console.print(
            f"[green]✓[/green] Created {layer}: {node.title} (ID: {node.id})"
        )
    except (
        ValueError,
        KeyError,
        AttributeError,
        jsonschema.ValidationError,
        RuntimeError,
    ) as e:
        console.print(f"[red]✗[/red] Error creating node: {e}")
        sys.exit(1)


@cli.command()
@click.argument("node_id")
@click.pass_context
def get(_: click.Context, node_id: str) -> None:
    """Gets a node by its ID."""
    try:
        node = cast("Any", get_node(node_id))
        if node:
            table = Table(title=f"Node: {node.id}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("ID", node.id)
            table.add_row("Layer", node.layer)
            table.add_row("Title", node.title)
            table.add_row("Description", node.description)
            table.add_row("Status", capitalize_status(node.status))
            table.add_row(
                "Progress",
                f"{node.progress}%" if node.progress is not None else "0%",
            )

            if hasattr(node, "owner") and node.owner:
                table.add_row("Owner", node.owner)
            if hasattr(node, "severity") and node.severity:
                table.add_row("Severity", node.severity)
            if hasattr(node, "work_type") and node.work_type:
                table.add_row("Work Type", node.work_type)

            console.print(table)
        else:
            console.print(f"[red]✗[/red] Node with ID '{node_id}' not found")
            sys.exit(1)
    except (ValueError, KeyError, RuntimeError) as e:
        console.print(f"[red]✗[/red] Error getting node: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--layer",
    "-l",
    help="Filter by layer (Goal, Task, Concept, Command)",
)
@click.option(
    "--owner",
    "-o",
    help="Filter by owner",
)
@click.option(
    "--status",
    "-s",
    help="Filter by status",
)
@click.pass_context
def list_command(
    _: click.Context,
    layer: str | None,
    owner: str | None,
    status: str | None,
) -> None:
    """Lists all the nodes."""

    try:
        nodes = list_nodes()

        if layer:
            nodes = {k: v for k, v in nodes.items() if k == layer}

        all_nodes: list[tuple[str, Node]] = []
        for layer_name, layer_nodes in nodes.items():
            for node in layer_nodes:
                all_nodes.append((layer_name, node))

        if not all_nodes:
            console.print("[yellow]No nodes found[/yellow]")
            return

        table = Table(title="All Nodes")
        table.add_column("Layer", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Title", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Progress", style="blue")
        table.add_column("Owner", style="red")

        for layer_name, node in all_nodes:
            # Apply filters
            if owner and (
                hasattr(node, "metadata") and node.metadata.owner != owner
            ):
                continue
            if status and node.status != status:
                continue

            # Get owner from metadata with proper fallback
            owner_val = get_current_username()  # Default to current user
            if hasattr(node, "metadata") and node.metadata:
                owner_val = (
                    getattr(node.metadata, "owner", "")
                    or get_current_username()
                )

            table.add_row(
                layer_name,
                node.id,
                node.title,
                capitalize_status(node.status),
                f"{node.progress or 0}%",
                owner_val,
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Error listing nodes: {e}")
        sys.exit(1)


@cli.group()
def status() -> None:
    """Status management commands for tracking task progress."""


@status.command()
@click.argument("node_id")
@click.pass_context
def show(_: click.Context, node_id: str) -> None:
    """Show detailed status information about a node."""
    app = get_app()

    try:
        node = app.get_node(node_id)
        if not node:
            console.print(f"[red]✗[/red] Node with ID '{node_id}' not found")
            sys.exit(1)

        table = Table(title=f"Node Status: {node.title}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("ID", node.id)
        table.add_row("Layer", node.layer)
        table.add_row("Title", node.title)
        table.add_row("Description", node.description)
        table.add_row("Status", capitalize_status(node.status))
        table.add_row(
            "Progress",
            f"{node.progress}%" if node.progress is not None else "0%",
        )
        table.add_row("Owner", node.metadata.owner or get_current_username())
        table.add_row("Severity", (node.metadata.severity or "low").title())
        table.add_row(
            "Work Type", (node.metadata.work_type or "chore").title()
        )

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Error showing node status: {e}")
        sys.exit(1)


@status.command()
@click.argument("node_id")
@click.pass_context
def complete(_: click.Context, node_id: str) -> None:
    """Mark a node as completed."""
    app = get_app()

    try:
        node = app.get_node(node_id)
        if not node:
            console.print(f"[red]✗[/red] Node with ID '{node_id}' not found")
            sys.exit(1)

        if node.status == "completed":
            console.print(
                f"[yellow]Node {node_id} is already completed[/yellow]"
            )
            return

        update_data = {
            "status": "completed",
            "progress": 100,
            "completion_date": "2024-01-01",  # Default date
        }

        updated_node = app.update_node(node_id, update_data)
        if updated_node:
            console.print(
                f"[green]✓[/green] Completed {node_id}: {updated_node.title}"
            )
        else:
            console.print(
                f"[green]✓[/green] Completed {node_id}: Unknown title"
            )
    except Exception as e:
        console.print(f"[red]✗[/red] Error completing node: {e}")
        sys.exit(1)


@status.command()
@click.option(
    "--layer",
    "-l",
    help="Filter by layer type",
)
@click.option(
    "--owner",
    "-o",
    help="Filter by owner",
)
@click.option(
    "--status",
    "-s",
    help="Filter by status",
)
@click.pass_context
def global_status(
    _: click.Context,
    layer: str | None,
    owner: str | None,
    status: str | None,
) -> None:
    """Show status information for all nodes."""
    try:
        nodes = list_nodes()

        if layer:
            # Case-insensitive layer filtering
            layer_mapping = {
                "goal": "Goal",
                "concept": "Concept",
                "context": "Context",
                "constraints": "Constraints",
                "requirements": "Requirements",
                "acceptancecriteria": "AcceptanceCriteria",
                "interfacecontract": "InterfaceContract",
                "phase": "Phase",
                "step": "Step",
                "task": "Task",
                "subtask": "SubTask",
                "command": "Command",
            }
            normalized_layer = layer_mapping.get(layer.lower(), layer.title())
            nodes = {k: v for k, v in nodes.items() if k == normalized_layer}

        all_nodes: list[tuple[str, Node]] = []
        for layer_name, layer_nodes in nodes.items():
            for node in layer_nodes:
                # Apply additional filters
                if owner and (
                    not hasattr(node, "metadata")
                    or not node.metadata
                    or not hasattr(node.metadata, "owner")
                    or node.metadata.owner.lower() != owner.lower()
                ):
                    continue
                if status and node.status.lower() != status.lower():
                    continue
                all_nodes.append((layer_name, node))

        if not all_nodes:
            console.print("[yellow]No nodes found matching criteria[/yellow]")
            return

        table = Table(title="Global Status Overview")
        table.add_column("Layer", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Title", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Progress", style="blue")
        table.add_column("Owner", style="red")
        table.add_column("Severity", style="white")
        table.add_column("Work Type", style="cyan")

        for layer_name, node in all_nodes:
            # Get owner from metadata with proper fallback
            owner_val = get_current_username()
            if hasattr(node, "metadata") and node.metadata:
                owner_val = (
                    getattr(node.metadata, "owner", "")
                    or get_current_username()
                )

            # Get severity from metadata
            severity_val = "low"  # Default severity
            if hasattr(node, "metadata") and node.metadata:
                severity_val = getattr(node.metadata, "severity", "") or "low"

            # Get work_type from metadata
            work_type_val = "chore"  # Default work type
            if hasattr(node, "metadata") and node.metadata:
                work_type_val = (
                    getattr(node.metadata, "work_type", "") or "chore"
                )

            # Capitalize work_type for display
            work_type_display = work_type_val.title()

            # Capitalize severity for display
            severity_display = severity_val.title()

            # Truncate long titles for table display
            title_display = (
                node.title[:30] + "..." if len(node.title) > 30 else node.title
            )
            id_display = node.id[:12] + "…" if len(node.id) > 12 else node.id

            table.add_row(
                layer_name,
                id_display,
                title_display,
                capitalize_status(node.status),
                f"{node.progress}%" if node.progress is not None else "0%",
                owner_val[:20] + "…" if len(owner_val) > 20 else owner_val,
                severity_display,
                work_type_display,
            )

        console.print(table)

        # Summary statistics
        total_nodes = len(all_nodes)
        completed_nodes = len(
            [n for _, n in all_nodes if n.status == "completed"]
        )
        in_progress_nodes = len(
            [n for _, n in all_nodes if n.status == "in_progress"]
        )

        console.print("\n[bold]Summary:[/bold]")
        console.print(f"Total nodes: {total_nodes}")
        if total_nodes > 0:
            percentage = completed_nodes / total_nodes * 100
            console.print(f"Completed: {completed_nodes} ({percentage:.1f}%)")
        else:
            console.print("Completed: 0")
        if total_nodes > 0:
            percentage = in_progress_nodes / total_nodes * 100
            console.print(
                f"In Progress: {in_progress_nodes} ({percentage:.1f}%)"
            )
        else:
            console.print("In Progress: 0")

    except Exception as e:
        console.print(f"[red]✗[/red] Error showing global status: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--yaml-path",
    "-y",
    default="./configs",
    help="Path to YAML files directory",
)
@click.pass_context
def import_yaml(_: click.Context, yaml_path: str) -> None:
    """Import YAML files from configs/ directory to database."""
    app = get_app()

    try:
        # Create a custom YAMLManager that uses the specified path
        yaml_manager = YAMLManager(app)

        # Override the paths if custom path provided
        if yaml_path != "./configs":
            from pathlib import Path

            custom_path = Path(yaml_path)
            yaml_manager.yaml_base_path = custom_path
            yaml_manager.plans_path = custom_path / "plans"
            yaml_manager.commands_path = custom_path / "commands"

        results = yaml_manager.import_yaml_files()

        console.print("[green]✓[/green] Import completed:")
        console.print(f"  Files processed: {results['total_files']}")
        console.print(f"  Nodes imported: {results['total_imported']}")
        console.print(f"  Errors: {len(results['errors'])}")

        if results["errors"]:
            console.print("[red]Errors encountered:[/red]")
            for error in results["errors"]:
                console.print(f"  {error}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error importing YAML: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    "-o",
    default="./exported",
    help="Output directory for YAML files",
)
@click.pass_context
def export_yaml(_: click.Context, output: str) -> None:
    """Export database content to YAML files."""
    app = get_app()

    try:
        yaml_manager = YAMLManager(app)
        results = yaml_manager.export_to_yaml(Path(output))

        console.print("[green]✓[/green] Export completed:")
        console.print(f"  Nodes exported: {results['total_nodes']}")
        console.print(f"  Files created: {results['total_exported']}")
        console.print(f"  Errors: {len(results['errors'])}")

        if results["errors"]:
            console.print("[red]Errors encountered:[/red]")
            for error in results["errors"]:
                console.print(f"  {error}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error exporting YAML: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def sync_status(_: click.Context) -> None:
    """Check synchronization status between YAML files and database."""
    app = get_app()

    try:
        yaml_manager = YAMLManager(app)
        sync_status = yaml_manager.check_yaml_sync()

        table = Table(title="YAML Database Sync Status")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="magenta")

        table.add_row("Database only", str(len(sync_status["database_only"])))
        table.add_row("YAML only", str(len(sync_status["yaml_only"])))
        table.add_row("Both", str(len(sync_status["both"])))

        console.print(table)

        if sync_status["database_only"]:
            console.print("[yellow]Database only nodes:[/yellow]")
            for node_id in sync_status["database_only"][:10]:  # Show first 10
                console.print(f"  {node_id}")
            if len(sync_status["database_only"]) > 10:
                console.print(
                    f"  ... and {len(sync_status['database_only']) - 10} more"
                )

        if sync_status["yaml_only"]:
            console.print("[yellow]YAML only nodes:[/yellow]")
            for node_id in sync_status["yaml_only"][:10]:  # Show first 10
                console.print(f"  {node_id}")
            if len(sync_status["yaml_only"]) > 10:
                console.print(
                    f"  ... and {len(sync_status['yaml_only']) - 10} more"
                )
    except Exception as e:
        console.print(f"[red]✗[/red] Error checking sync status: {e}")
        sys.exit(1)


@cli.command()
@click.pass_context
def db_status(_: click.Context) -> None:
    """Show storage configuration and status."""
    app = get_app()

    try:
        # Show database info
        table = Table(title="Database Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")

        # Show schema validation
        schema_valid = validate_schema(app.engine)
        table.add_row("Schema Valid", "✓" if schema_valid else "✗")

        # Show node counts
        nodes = list_nodes()
        total_nodes = sum(len(layer_nodes) for layer_nodes in nodes.values())
        table.add_row("Total Nodes", str(total_nodes))

        console.print(table)

        # Show schema compliance
        try:
            # Create a temporary app for storage type
            temp_app = ToDoWrite()
            compliance_report: Any = get_schema_compliance_report(
                (
                    temp_app.storage_type.value
                    if hasattr(temp_app.storage_type, "value")
                    else str(temp_app.storage_type)
                ),
                engine=temp_app.engine,
            )
            # Handle different report structures gracefully
            if compliance_report and isinstance(compliance_report, dict):
                if compliance_report.get("is_compliant", False):
                    console.print("[green]✓[/green] Schema is compliant")
                else:
                    console.print(
                        "[yellow]⚠️[/yellow] Schema compliance issues found:"
                    )
                    if compliance_report.get("errors"):
                        for error in compliance_report["errors"]:
                            console.print(f"  • {error}")
                    if compliance_report.get("warnings"):
                        for warning in compliance_report["warnings"]:
                            console.print(f"  • {warning}")
            else:
                console.print(
                    "[yellow]Schema compliance check returned "
                    "unexpected format[/yellow]"
                )
        except Exception as e:
            console.print(
                f"[yellow]⚠️ Schema compliance check failed: {e}[/yellow]"
            )
            console.print(
                "[dim]This is not critical - core functionality still "
                "works[/dim]"
            )
    except Exception as e:
        console.print(f"[red]✗[/red] Error getting database status: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument("node_id")
@click.pass_context
def delete(_: click.Context, node_id: str) -> None:
    """Delete a node by its ID."""
    try:
        node = cast("Any", get_node(node_id))
        if not node:
            console.print(f"[red]✗[/red] Node with ID '{node_id}' not found")
            sys.exit(1)

        delete_node(node_id)
        console.print(f"[green]✓[/green] Deleted {node_id}: {node.title}")
    except Exception as e:
        console.print(f"[red]✗[/red] Error deleting node: {e}")
        sys.exit(1)


@cli.command()
@click.argument("node_id")
@click.option("--title", help="Update title")
@click.option("--description", help="Update description")
@click.option("--owner", help="Update owner")
@click.option(
    "--severity",
    help="Update severity (case-insensitive: low, medium, med, high, "
    "critical)",
)
@click.option(
    "--work-type",
    help="Update work type (case-insensitive: architecture, spec, interface, "
    "validation, implementation, docs, ops, refactor, chore, test)",
)
@click.option(
    "--status",
    help="Update status (case-insensitive: planned, in_progress, completed, "
    "blocked, cancelled)",
)
@click.option(
    "--progress",
    type=click.IntRange(0, 100),
    help="Update progress percentage",
)
@click.option("--labels", help="Comma-separated labels")
# Command-specific options
@click.option(
    "--ac-ref", help="Update acceptance criteria reference (for Commands)"
)
@click.option("--run-shell", help="Update shell command (for Commands)")
@click.option(
    "--artifacts", help="Comma-separated artifact paths (for Commands)"
)
@click.pass_context
def update(
    _: click.Context,
    node_id: str,
    title: str | None,
    description: str | None,
    owner: str | None,
    severity: str | None,
    work_type: str | None,
    status: str | None,
    progress: int | None,
    labels: str | None,
    ac_ref: str | None,
    run_shell: str | None,
    artifacts: str | None,
) -> None:
    """Update a node's properties."""
    try:
        node = cast("Any", get_node(node_id))
        if not node:
            console.print(f"[red]✗[/red] Node with ID '{node_id}' not found")
            sys.exit(1)

        # Build update data
        update_data: dict[str, Any] = {}
        if title is not None:
            update_data["title"] = title
        if description is not None:
            update_data["description"] = description
        if owner is not None:
            update_data["metadata"] = update_data.get("metadata", {})
            update_data["metadata"]["owner"] = owner
        if severity is not None:
            # Convert severity input to proper case (case-insensitive)
            severity_mapping = {
                "low": "low",
                "medium": "medium",
                "med": "medium",
                "high": "high",
                "critical": "critical",
            }

            severity_normalized = severity_mapping.get(severity.lower())
            if not severity_normalized:
                valid_severities = ", ".join(sorted(severity_mapping.keys()))
                console.print(
                    f"[red]✗[/red] Invalid severity: '{severity}'. "
                    f"Valid options: {valid_severities}",
                )
                sys.exit(1)

            update_data["metadata"] = update_data.get("metadata", {})
            update_data["metadata"]["severity"] = severity_normalized

        if work_type is not None:
            # Convert work_type input to proper case (case-insensitive)
            work_type_mapping = {
                "architecture": "architecture",
                "spec": "spec",
                "interface": "interface",
                "validation": "validation",
                "implementation": "implementation",
                "development": "implementation",
                "docs": "docs",
                "operations": "ops",
                "ops": "ops",
                "refactor": "refactor",
                "chore": "chore",
                "test": "test",
            }

            work_type_normalized = work_type_mapping.get(work_type.lower())
            if not work_type_normalized:
                valid_work_types = ", ".join(sorted(work_type_mapping.keys()))
                console.print(
                    f"[red]✗[/red] Invalid work_type: '{work_type}'. "
                    f"Valid options: {valid_work_types}",
                )
                sys.exit(1)

            update_data["metadata"] = update_data.get("metadata", {})
            update_data["metadata"]["work_type"] = work_type_normalized
        if status is not None:
            # Convert status input to proper case (case-insensitive)
            status_mapping = {
                "planned": "planned",
                "inprogress": "in_progress",
                "in_progress": "in_progress",
                "completed": "completed",
                "blocked": "blocked",
                "cancelled": "cancelled",
            }

            status_normalized = status_mapping.get(status.lower())
            if not status_normalized:
                valid_statuses = ", ".join(sorted(status_mapping.keys()))
                console.print(
                    f"[red]✗[/red] Invalid status: '{status}'. "
                    f"Valid options: {valid_statuses}",
                )
                sys.exit(1)

            update_data["status"] = status_normalized
        if progress is not None:
            update_data["progress"] = progress
        if labels is not None:
            update_data["metadata"] = update_data.get("metadata", {})
            update_data["metadata"]["labels"] = [
                label.strip() for label in labels.split(",")
            ]

        # Command-specific updates
        if node.layer == "Command" and (
            ac_ref is not None
            or run_shell is not None
            or artifacts is not None
        ):
            update_data["command"] = update_data.get("command", {})
            if ac_ref is not None:
                update_data["command"]["ac_ref"] = ac_ref
            if run_shell is not None:
                update_data["command"]["run"] = {"shell": run_shell}
            if artifacts is not None:
                update_data["command"]["artifacts"] = [
                    artifact.strip() for artifact in artifacts.split(",")
                ]

        if not update_data:
            console.print("[yellow]⚠️[/yellow] No fields to update")
            return

        updated_node = update_node(node_id, update_data)
        if updated_node:
            console.print(
                f"[green]✓[/green] Updated {node_id}: "
                f"{getattr(updated_node, 'title', 'Unknown')}",
            )

            if status is not None:
                console.print(
                    f"  Status: {getattr(updated_node, 'status', 'Unknown')}"
                )
            if progress is not None:
                console.print(
                    f"  Progress: {getattr(updated_node, 'progress', 0)}%"
                )
        if owner is not None and updated_node:
            # Get owner from metadata
            owner_val = getattr(updated_node, "owner", None)
            if (
                not owner_val
                and hasattr(updated_node, "metadata")
                and getattr(updated_node, "metadata", None)
            ):
                owner_val = getattr(updated_node.metadata, "owner", None)
            owner_val = owner_val or "N/A"
            console.print(f"  Owner: {owner_val}")

    except Exception as e:
        console.print(f"[red]✗[/red] Error updating node: {e}")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.pass_context
def search(_: click.Context, query: str) -> None:
    """Search for nodes by query string."""
    try:
        results = search_nodes(query)

        if not results:
            console.print(f"[yellow]No results found for '{query}'[/yellow]")
            return

        table = Table(title=f"Search Results for: {query}")
        table.add_column("Layer", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Title", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Progress", style="blue")
        table.add_column("Owner", style="red")

        for layer_name, nodes in results.items():
            for node in nodes:
                # Get owner from metadata with proper fallback
                owner_val = get_current_username()  # Default to current user
                if hasattr(node, "metadata") and node.metadata:
                    owner_val = (
                        getattr(node.metadata, "owner", "")
                        or get_current_username()
                    )

                table.add_row(
                    layer_name,
                    node.id,
                    node.title,
                    capitalize_status(node.status),
                    f"{node.progress or 0}%",
                    owner_val,
                )

        console.print(table)
    except Exception as e:
        console.print(f"[red]✗[/red] Error searching nodes: {e}")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
