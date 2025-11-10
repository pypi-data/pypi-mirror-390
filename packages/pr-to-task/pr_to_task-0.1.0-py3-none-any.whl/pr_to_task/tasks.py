"""Task management functions for PR to Task processing."""

import json
from pathlib import Path
from typing import Any

import typer

from pr_to_task.models import PRComment, TaskState
from pr_to_task.prompts import (
    render_all_tasks_complete,
    render_task_complete_confirmation,
    render_task_next_prompt,
)


def load_task_state(jsonl_file: Path) -> TaskState:
    """Load task state from JSONL file."""
    if not jsonl_file.exists():
        typer.echo(f"Error: JSONL file not found: {jsonl_file}", err=True)
        raise typer.Exit(1)

    try:
        with jsonl_file.open("r") as f:
            # Read non-empty lines
            lines = [line for line in (ln.rstrip("\n") for ln in f) if line.strip()]
    except OSError as exc:
        typer.echo(f"Error reading file: {exc}", err=True)
        raise typer.Exit(1)

    if not lines:
        return TaskState()

    parsed: list[dict[str, Any]] = []
    for idx, line in enumerate(lines, start=1):
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError as exc:
            typer.echo(
                f"Error: Invalid JSON in file {jsonl_file} at line {idx}: {exc.msg}",
                err=True,
            )
            raise typer.Exit(1)

    return TaskState.from_dicts(parsed)


def save_task_state(jsonl_file: Path, task_state: TaskState) -> None:
    """Save task state to JSONL file."""
    try:
        with jsonl_file.open("w") as f:
            for comment_dict in task_state.to_dicts():
                f.write(json.dumps(comment_dict) + "\n")
    except OSError as exc:
        typer.echo(f"Error writing file: {exc}", err=True)
        raise typer.Exit(1)


def display_comment(comment: PRComment, index: int, total: int) -> None:
    """Display a comment in a formatted way."""
    typer.echo(f"\n{'=' * 60}")
    typer.echo(f"Comment {index + 1}/{total}:")
    typer.echo(f"  Author: {comment.author}")
    typer.echo(f"  Created: {comment.created_at}")
    typer.echo(f"  Type: {comment.comment_type}")
    if comment.path:
        typer.echo(f"  File: {comment.path}")
        if comment.line:
            typer.echo(f"  Line: {comment.line}")
    typer.echo(
        f"  Status: {'✓ Completed' if comment.completed else '◯ Not completed'}",
    )
    typer.echo(f"  Viewed: {'Yes' if comment.viewed else 'No'}")

    if comment.implementation_comments:
        typer.echo(
            f"\n  Implementation implementation_comments: {comment.implementation_comments}",
        )

    typer.echo("\nComment:")
    typer.echo(comment.text)
    typer.echo(f"\nURL: {comment.comment_url}")


def task_next(jsonl_file: Path) -> None:
    """Pick the next unviewed task and mark it as viewed."""
    task_state = load_task_state(jsonl_file)

    if task_state.total == 0:
        typer.echo("No comments found in the JSONL file.", err=True)
        raise typer.Exit(1)

    # Get next task index
    next_index = task_state.get_next_task_index()
    if next_index is None:
        # Show completion message with delay
        typer.echo(render_all_tasks_complete(), err=False)
        import time

        time.sleep(600)  # 10 minutes delay
        raise typer.Exit(0)

    comment = task_state.comments[next_index]

    # Check if already viewed
    if comment.viewed:
        typer.echo(
            "\n⚠️  THIS TASK WAS ALREADY VIEWED BEFORE! ENSURE IT WASN'T COMPLETED OR SKIPPED.\n",
            err=True,
        )

    # Mark as viewed
    comment.viewed = True

    # Display the comment
    display_comment(comment, next_index, task_state.total)

    # Append the special prompt for the agent with the actual comment text
    prompt = render_task_next_prompt(comment.text)
    typer.echo(prompt)

    # Save updated state
    save_task_state(jsonl_file, task_state)

    # Show progress
    typer.echo(f"\nProgress: {task_state.completed}/{task_state.total} tasks completed")


def task_mark_complete(jsonl_file: Path, implementation_comments: str) -> None:
    """Mark the current task as complete and show the next one."""
    task_state = load_task_state(jsonl_file)

    if task_state.total == 0:
        typer.echo("No comments found in the JSONL file.", err=True)
        raise typer.Exit(1)

    # Get current task index
    current_index = task_state.current_index
    if current_index is None:
        # No viewed uncompleted task
        next_idx = task_state.get_next_task_index()
        if next_idx is not None:
            typer.echo(
                f"No currently viewed task. Use 'task next' first to view task {next_idx + 1}.",
                err=True,
            )
        else:
            typer.echo("🎉 MISSION COMPLETE! All tasks have been completed!", err=False)
        raise typer.Exit(1)

    # Mark current task as complete
    task_state.comments[current_index].completed = True
    task_state.comments[current_index].implementation_comments = implementation_comments

    # Save updated state
    save_task_state(jsonl_file, task_state)

    # Find next task
    next_index = task_state.get_next_task_index()
    if next_index is None:
        # All tasks complete - show summary
        confirmation_msg = render_task_complete_confirmation("All tasks completed!")
        typer.echo(confirmation_msg, err=False)

        typer.echo("\n📊 Final Summary:")
        typer.echo(f"  Total tasks: {task_state.total}")
        typer.echo(f"  Completed: {task_state.completed}")
        raise typer.Exit(0)

    # Show confirmation and move to next task
    next_comment = task_state.comments[next_index]
    confirmation_msg = render_task_complete_confirmation(next_comment.text)
    typer.echo(confirmation_msg, err=False)

    # Mark next as viewed
    next_comment.viewed = True

    # Display the next comment
    display_comment(next_comment, next_index, task_state.total)

    # Save updated state again
    save_task_state(jsonl_file, task_state)

    # Show progress
    typer.echo(f"\nProgress: {task_state.completed}/{task_state.total} tasks completed")


def task_status(jsonl_file: Path) -> None:
    """Show the current status of all tasks."""
    task_state = load_task_state(jsonl_file)

    if task_state.total == 0:
        typer.echo("No comments found in the JSONL file.", err=True)
        raise typer.Exit(1)

    typer.echo("\n📊 Task Status Summary")
    typer.echo(f"{'=' * 40}")
    typer.echo(f"Total tasks: {task_state.total}")
    typer.echo(
        f"Completed: {task_state.completed} ({task_state.completed * 100 // task_state.total}%)",
    )
    typer.echo(f"Viewed: {task_state.viewed}")
    typer.echo(f"Remaining: {task_state.remaining}")

    # Show breakdown by type
    review_count = sum(1 for c in task_state.comments if c.comment_type != "issue")
    issue_count = sum(1 for c in task_state.comments if c.comment_type == "issue")
    typer.echo("\nBy Type:")
    typer.echo(f"  Review comments: {review_count}")
    typer.echo(f"  Issue comments: {issue_count}")

    # Show authors
    authors = {c.author for c in task_state.comments}
    typer.echo(f"\nAuthors: {', '.join(sorted(authors))}")

    # Show current task
    current_index = task_state.current_index
    if current_index is not None:
        typer.echo(f"\n📍 Current task: #{current_index + 1}")
        typer.echo(f"   Author: {task_state.comments[current_index].author}")
        preview = task_state.comments[current_index].text[:100]
        if len(task_state.comments[current_index].text) > 100:
            preview += "..."
        typer.echo(f"   Preview: {preview}")
    elif task_state.completed < task_state.total:
        typer.echo("\n💡 Use 'pr_to_task task next' to view the next task")


def task_reset(jsonl_file: Path, confirm: bool = False) -> None:
    """Reset all task states (viewed and completed flags)."""
    if not confirm:
        response = typer.confirm("Are you sure you want to reset all task states?")
        if not response:
            typer.echo("Reset cancelled.")
            raise typer.Exit(0)

    task_state = load_task_state(jsonl_file)

    if task_state.total == 0:
        typer.echo("No comments found in the JSONL file.", err=True)
        raise typer.Exit(1)

    # Reset all states
    for comment in task_state.comments:
        comment.viewed = False
        comment.completed = False
        comment.implementation_comments = None

    # Save updated state
    save_task_state(jsonl_file, task_state)

    typer.echo(f"✓ Reset all {task_state.total} tasks to initial state")


def task_init(jsonl_file: Path, output_dir: Path | None = None) -> None:
    """Initialize task processing by generating AGENTS.md and showing first task."""
    task_state = load_task_state(jsonl_file)

    if task_state.total == 0:
        typer.echo("No comments found in the JSONL file.", err=True)
        raise typer.Exit(1)

    # Determine output directory
    if output_dir is None:
        output_dir = jsonl_file.parent

    # Try to get project and PR info from first comment
    project = None
    pr = None
    if task_state.comments:
        project = task_state.comments[0].project
        pr = task_state.comments[0].pr

    # Generate AGENTS.md
    from .pr_fetch import generate_agents_file

    agents_file = generate_agents_file(
        output_dir=output_dir,
        project=project or "unknown/repo",
        pr=pr or 0,
        total_comments=task_state.total,
    )
    typer.echo(f"✓ Generated {agents_file}")

    # Now show the first task
    typer.echo("\n" + "=" * 60)
    typer.echo("Starting task processing...")
    task_next(jsonl_file)
