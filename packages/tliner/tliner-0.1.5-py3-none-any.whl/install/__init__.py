#!/usr/bin/env python3
"""Standalone installer for timeliner Claude Code integration.

Usage:
    uvx --from tliner tliner-install --work-folder docs/timeline
    python -m install --work-folder docs/timeline
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.prompt import Confirm

    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def print_msg(text: str) -> None:
    """Print with Rich if available, else strip markup and print plain."""
    if HAS_RICH:
        console.print(text)
    else:
        clean = re.sub(r"\[.*?\]", "", text)
        print(clean)  # noqa: T201


def confirm(msg: str, default: bool = False) -> bool:  # noqa: FBT001, FBT002
    """Prompt yes/no with Rich or plain input."""
    if HAS_RICH:
        return Confirm.ask(msg, default=default)

    prompt = f"{msg} [{'Y/n' if default else 'y/N'}]: "
    response = input(prompt).strip().lower()
    if not response:
        return default
    return response in ("y", "yes")


def detect_claude_setup(cwd: Path) -> tuple[bool, str]:
    """Returns (has_setup, reason)."""
    if (cwd / ".claude").is_dir():
        return True, ".claude/ directory exists"
    if (cwd / "CLAUDE.md").is_file():
        return True, "CLAUDE.md file exists"
    return False, "No .claude/ or CLAUDE.md found. Re-run tliner installer from the exisitng Claude project."


def ensure_claude_dir(cwd: Path) -> Path:
    """Create .claude/commands/ if missing."""
    claude_dir = cwd / ".claude"
    claude_dir.mkdir(exist_ok=True)
    commands_dir = claude_dir / "commands"
    commands_dir.mkdir(exist_ok=True)
    return claude_dir


def validate_and_create_work_folder(base_path: Path, work_folder: str) -> Path:
    """Validate work_folder path and create it with .tliner marker."""
    work_path = (base_path / work_folder).resolve()

    if not work_path.is_relative_to(base_path.resolve()):
        print_msg("[red]Invalid work folder: path escapes project directory[/red]")
        raise SystemExit(1)

    work_path.mkdir(parents=True, exist_ok=True)
    (work_path / ".tliner").mkdir(exist_ok=True)

    return work_path


def add_mcp_server(work_folder: str) -> bool:
    """Add timeliner MCP server via claude CLI."""
    cmd = ["claude", "mcp", "add", "--scope", "project", "--transport", "stdio", "timeliner", "--env", f"TIMELINER_WORK_FOLDER=${{PWD}}/{work_folder}", "--", "uvx", "tliner", "serve"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # noqa: S603
        if result.returncode != 0:
            print_msg(f"[red]Error running claude mcp add:[/red]\n{result.stderr}")
            return False
    except FileNotFoundError:
        print_msg("[red]Error: 'claude' CLI not found. Install Claude Code first.[/red]")
        return False
    else:
        return True


def create_command_file(commands_dir: Path, name: str) -> Path:
    """Copy command template to .claude/commands/{name}.md."""
    template_path = Path(__file__).parent / "save.md"
    template_content = template_path.read_text()

    cmd_file = commands_dir / f"{name}.md"
    cmd_file.write_text(template_content)
    return cmd_file


def run_install_claude(work_folder: str) -> int:
    """Main installation logic. Returns exit code."""
    cwd = Path.cwd()

    print_msg("[bold cyan]Timeliner Installation[/bold cyan]\n")

    has_setup, reason = detect_claude_setup(cwd)
    if has_setup:
        print_msg(f"[green]✓[/green] Claude setup detected: {reason}")
    else:
        print_msg(f"[yellow]⚠[/yellow] {reason}")
        if not confirm("Create .claude/ directory?", default=True):
            print_msg("[red]Installation cancelled.[/red]")
            return 1

    claude_dir = ensure_claude_dir(cwd)
    print_msg(f"[green]✓[/green] Directory ready: {claude_dir}")

    work_path = validate_and_create_work_folder(cwd, work_folder)
    print_msg(f"[green]✓[/green] Work folder created: {work_path}")

    print_msg(f"\n[cyan]Adding MCP server (work folder: {work_folder})...[/cyan]")
    if not add_mcp_server(work_folder):
        return 1
    print_msg("[green]✓[/green] MCP server configured")

    commands_dir = claude_dir / "commands"
    save_cmd = commands_dir / "save.md"

    if save_cmd.exists():
        print_msg("[yellow]⚠[/yellow] /save command already exists")
        if not confirm("Create /step command instead?", default=True):
            print_msg("[red]Installation cancelled.[/red]")
            return 1
        cmd_name = "step"
    else:
        cmd_name = "save"

    cmd_file = create_command_file(commands_dir, cmd_name)
    print_msg(f"[green]✓[/green] Created /{cmd_name} command: {cmd_file}")

    print_msg("\n[bold green]Installation complete![/bold green]")
    print_msg(f"  Work folder: {cwd / work_folder}")
    print_msg(f"  Command: /{cmd_name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Install timeliner into Claude Code project")
    parser.add_argument("--work-folder", "-w", default="docs/timeline", help="Work folder for timeline storage (default: docs/timeline)")
    args = parser.parse_args(argv)

    return run_install_claude(args.work_folder)


if __name__ == "__main__":
    sys.exit(main())
