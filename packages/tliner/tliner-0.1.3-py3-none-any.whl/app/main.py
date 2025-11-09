#!/usr/bin/env python3
import sys

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from .mcp import app as mcp_app
from .mcp import get_step as mcp_get_step
from .mcp import get_steps as mcp_get_steps
from .mcp import save_step as mcp_save_step
from .mcp import task_create as mcp_create_task
from .mcp import task_list as mcp_list_tasks
from .mcp import task_show as mcp_show_task
from .services import Timeline

logger.remove()
logger.add(sys.stderr, level="TRACE")  # show Trace level on std log


cli_app = typer.Typer()
console = Console()


@cli_app.command()
def serve() -> None:
    """Run Timeliner as MCP server"""
    console.print("[green]Starting Timeliner MCP server...[/green]")
    # mcp_app.run(transport="sse", host="127.0.0.1", port=9535)
    mcp_app.run()


@cli_app.command()
def task_create(title: str, user_prompt: str | None = typer.Option(None, "--prompt", "-p", help="Initial user prompt to save as first milestone")) -> None:
    """Create a new task with auto-generated ID"""
    result = mcp_create_task.fn(task_title=title, user_prompt=user_prompt or "")
    task_id = result.get("task_id")
    console.print(f"[green]✓[/green] Created task: [cyan]{task_id}[/cyan]")
    if user_prompt:
        console.print("  Initial prompt saved as milestone")


@cli_app.command()
def task_list() -> None:
    """List all tasks in the system"""
    result = mcp_list_tasks.fn()
    tasks = result.get("tasks", [])
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return

    table = Table(title="Tasks")
    table.add_column("Doc ID", style="dim", justify="right")
    table.add_column("Task ID", style="cyan")
    table.add_column("Description")
    table.add_column("Milestones", justify="right", style="green")

    for task in tasks:
        doc_id = str(task.get("doc_id", -1))
        task_id = task["task_id"]
        description = task.get("description") or "[dim]No description[/dim]"
        milestones = Timeline().get_steps_by_task_id(task_id)
        milestone_count = str(len(milestones))

        table.add_row(doc_id, task_id, description, milestone_count)

    console.print(table)


def _doc_id_to_task_id(doc_id_str: str) -> str:
    try:
        doc_id = int(doc_id_str)
    except ValueError:
        logger.warning(f"Task ID `{doc_id_str}` not found and not a valid doc_id")
        return ""
    task = Timeline().get_task_by_doc_id(doc_id)
    if not task:
        logger.warning(f"Task with doc_id `{doc_id}` not found")
        return ""
    return task.task_id


@cli_app.command()
def task_show(task_id: str) -> None:
    """Show all milestones for a task"""
    result = mcp_show_task.fn(task_id)
    milestones = result.get("milestones", [])
    # if task not found, try to found task by doc_id
    if not milestones:
        task_id = _doc_id_to_task_id(task_id)
        if task_id:
            result = mcp_show_task.fn(task_id)
            milestones = result.get("milestones", [])

    console.print(f"\n[bold cyan]Task: {task_id}[/bold cyan]")
    for m in milestones:
        console.print(f"\n[green]{m['timestamp']}[/green]")
        console.print(f"  {m['outcomes']}")
        if m.get("tags"):
            console.print(f"  Tags: {', '.join(m['tags'])}")


@cli_app.command()
def create(task_id: str, title: str, outcomes: str, tags: list[str] | None = typer.Option(None, "--tag", "-t", help="Tags for the milestone")) -> None:
    """Create a milestone for a task"""
    result = mcp_save_step.fn(task_id=task_id, title=title, outcomes=outcomes, tags=tags or [], metadata=None)
    milestone_id = result.get("milestone_id", "N/A")
    console.print(f"[green]✓[/green] Saved milestone {milestone_id} for task {task_id}")


@cli_app.command(name="list")
def list_steps(
    since: str | None = typer.Option(None, "--since", "-s", help="Filter steps since timestamp (include) (ISO format, e.g., 2025-01-01T00:00:00Z). Couple of --until"),
    until: str | None = typer.Option(None, "--until", "-u", help="Filter steps until timestamp (exclude) (ISO format, e.g., 2025-01-01T00:00:00Z). Couple of --since"),
    tasks: list[str] | None = typer.Option(None, "--task", "-t", help="Filter steps by task ID(s)"),
) -> None:
    """List all steps across all tasks with optional time and task filters"""
    result = mcp_get_steps.fn(since=since or "", until=until or "", task_ids=tasks or [])
    steps = result.get("steps", [])

    if not steps:
        console.print("[yellow]No steps found[/yellow]")
        return

    title_parts = ["All Steps"]
    if since:
        title_parts.append(f"since {since} until {until}")
    if tasks:
        title_parts.append(f"tasks: {', '.join(tasks)}")
    title = title_parts[0] + (f" ({', '.join(title_parts[1:])})" if len(title_parts) > 1 else "")
    table = Table(title=title)
    table.add_column("Doc ID", style="green")
    table.add_column("Timestamp", style="green")
    table.add_column("Task ID", style="cyan")
    table.add_column("Outcomes")
    table.add_column("Tags", style="dim")

    for m in steps:
        doc_id = str(m.get("doc_id", -1))
        timestamp = m["timestamp"]
        task_id = m["task_id"]
        outcomes = m["outcomes"][:80] + "..." if len(m["outcomes"]) > 200 else m["outcomes"]  # noqa: PLR2004
        tags = ", ".join(m.get("tags", []))

        table.add_row(doc_id, timestamp, task_id, outcomes, tags)

    console.print(table)
    console.print(f"\n[dim]Total: {len(steps)} steps[/dim]")


@cli_app.command()
def show(doc_id: int) -> None:
    """Show a specific milestone by its document ID"""
    try:
        result = mcp_get_step.fn(doc_id=doc_id)
        milestone = result.get("milestone")

        console.print(f"\n[bold cyan]ID:[/bold cyan] {doc_id}")
        console.print(f"[green]Task:[/green] {milestone['task_id']}")
        console.print(f"[green]Timestamp:[/green] {milestone['timestamp']}")
        if milestone.get("tags"):
            console.print(f"[green]Tags:[/green] {', '.join(milestone['tags'])}")
        if milestone.get("metadata"):
            console.print(f"[green]Metadata:[/green] {milestone['metadata']}")
        console.print("\n[bold]Outcomes:[/bold]")
        console.print(milestone["outcomes"])
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e!s}")
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Error retrieving milestone:[/red] {e!s}")


@cli_app.command()
def generate_id() -> None:
    """Generate a new task ID"""
    task_id = Timeline().generate_task_id()
    console.print(f"Generated task ID: [cyan]{task_id}[/cyan]")


app = cli_app

if __name__ == "__main__":
    cli_app()
