#!/usr/bin/env python3
"""Main CLI entry point for PR to Task processing tool."""

from pathlib import Path
from typing import Annotated, Literal

import typer

from pr_to_task.pr_fetch import fetch_and_save_comments
from pr_to_task.tasks import (
    task_init,
    task_mark_complete,
    task_next,
    task_reset,
    task_status,
)

DEFAULT_OUTPUT_PATH = Path("pr_comments.jsonl")

app = typer.Typer(help="Fetch GitHub PR comments and process them as tasks")


@app.command("fetch")
def fetch_command(
    project: Annotated[
        str,
        typer.Argument(help="GitHub repository (format: owner/repo)"),
    ],
    pr: Annotated[int, typer.Argument(help="Pull request number")],
    token: Annotated[
        str | None,
        typer.Option(help="GitHub personal access token (optional for public repos)"),
    ] = None,
    since: Annotated[
        str | None,
        typer.Option(help="Filter comments since date (ISO 8601)"),
    ] = None,
    quantity: Annotated[
        int | None,
        typer.Option(help="Number of comments (from most recent)"),
    ] = None,
    output: Annotated[
        Path,
        typer.Option(help="Output JSONL file path"),
    ] = DEFAULT_OUTPUT_PATH,
    hooks: Annotated[
        bool,
        typer.Option(help="Generate Claude Code hooks configuration"),
    ] = False,
) -> None:
    """Fetch GitHub PR comments and generate JSONL file."""
    fetch_and_save_comments(
        project=project,
        pr=pr,
        token=token,
        since=since,
        quantity=quantity,
        output=output,
        hooks=hooks,
    )


@app.command("init")
def init_command(
    jsonl_file: Annotated[
        Path,
        typer.Argument(help="Path to JSONL file with PR comments"),
    ] = Path("pr_comments.jsonl"),
    output_dir: Annotated[
        Path | None,
        typer.Option(help="Directory to output AGENTS.md"),
    ] = None,
) -> None:
    """Initialize task processing by generating AGENTS.md and showing first task."""
    task_init(jsonl_file=jsonl_file, output_dir=output_dir)


@app.command("next")
def next_command(
    jsonl_file: Annotated[
        Path,
        typer.Argument(help="Path to JSONL file with PR comments"),
    ] = Path("pr_comments.jsonl"),
) -> None:
    """Show the next uncompleted task."""
    task_next(jsonl_file=jsonl_file)


@app.command("mark-complete")
def mark_complete_command(
    implementation_comments: Annotated[
        str,
        typer.Option(
            "--implementation_comments",
            "-n",
            help="Detailed implementation comments (required)",
        ),
    ],
    jsonl_file: Annotated[
        Path,
        typer.Argument(help="Path to JSONL file with PR comments"),
    ] = Path("pr_comments.jsonl"),
) -> None:
    """Mark current task as complete and show next task.

    Requires detailed implementation comments about what was implemented or why it wasn't applicable.
    """
    if not implementation_comments or not implementation_comments.strip():
        typer.echo(
            "Error: --implementation_comments is required. Please provide detailed implementation comments.",
            err=True,
        )
        raise typer.Exit(1)

    task_mark_complete(
        jsonl_file=jsonl_file,
        implementation_comments=implementation_comments,
    )


@app.command("status")
def status_command(
    jsonl_file: Annotated[
        Path,
        typer.Argument(help="Path to JSONL file with PR comments"),
    ] = Path("pr_comments.jsonl"),
) -> None:
    """Show the current status of all tasks."""
    task_status(jsonl_file=jsonl_file)


@app.command("reset")
def reset_command(
    jsonl_file: Annotated[
        Path,
        typer.Argument(help="Path to JSONL file with PR comments"),
    ] = Path("pr_comments.jsonl"),
    confirm: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Reset all task states (viewed and completed flags)."""
    task_reset(jsonl_file=jsonl_file, confirm=confirm)


# Legacy task command for backward compatibility
@app.command("task")
def task_command(
    action: Annotated[
        Literal["next", "mark-complete", "status", "reset", "init"],
        typer.Argument(help="Task action"),
    ],
    jsonl_file: Annotated[
        Path,
        typer.Argument(help="Path to JSONL file with PR comments"),
    ] = Path("pr_comments.jsonl"),
    implementation_comments: Annotated[
        str | None,
        typer.Option("--implementation_comments", "-n", help="Implementation comments"),
    ] = None,
    confirm: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation"),
    ] = False,
) -> None:
    """Legacy task command (use specific commands instead)."""
    if action == "next":
        task_next(jsonl_file)
    elif action == "mark-complete":
        if not implementation_comments or not implementation_comments.strip():
            typer.echo(
                "Error: --implementation_comments is required for mark-complete",
                err=True,
            )
            raise typer.Exit(1)
        task_mark_complete(jsonl_file, implementation_comments)

    elif action == "status":
        task_status(jsonl_file)
    elif action == "reset":
        task_reset(jsonl_file, confirm)
    elif action == "init":
        task_init(jsonl_file)
    else:
        typer.echo(f"Unknown action: {action}", err=True)
        raise typer.Exit(1)


# Default command shim
def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
