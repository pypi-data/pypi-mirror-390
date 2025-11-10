"""GitHub API operations for fetching PR comments."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
import typer
from requests.exceptions import RequestException

from pr_to_task.models import PRComment
from pr_to_task.prompts import render_hooks_config, render_processor_script


def parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse ISO 8601 timestamp strings to timezone-aware datetimes."""
    if not value:
        return None

    formatted_value = value[:-1] + "+00:00" if value.endswith("Z") else value

    try:
        parsed = datetime.fromisoformat(formatted_value)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)

    return parsed


def fetch_paginated_comments(
    api_url: str,
    headers: dict[str, str],
    base_params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Fetch paginated comments from GitHub API."""
    all_comments: list[dict[str, Any]] = []
    params = base_params.copy() if base_params else {}
    page = 1

    while True:
        request_params = {**params, "page": page, "per_page": 100}

        response = requests.get(
            api_url,
            headers=headers,
            params=request_params,
            timeout=30,
        )
        response.raise_for_status()

        comments = response.json()

        if not comments:
            break

        all_comments.extend(comments)

        # Check if there are more pages
        if len(comments) < 100:
            break

        page += 1

    return all_comments


def fetch_pr_comments(
    token: str | None,
    project: str,
    pr: int,
    since: str | None = None,
    quantity: int | None = None,
) -> list[PRComment]:
    """Fetch comments from a GitHub PR.

    Args:
        token: GitHub personal access token (optional for public repos)
        project: Repository in format "owner/repo"
        pr: Pull request number
        since: ISO 8601 date to filter comments (e.g., "2024-01-01T00:00:00Z")
        quantity: Maximum number of comments to fetch (from most recent)

    Returns:
        List of PRComment objects

    """
    # API endpoint for PR comments
    api_url = f"https://api.github.com/repos/{project}/pulls/{pr}/comments"

    headers = {
        "Accept": "application/vnd.github.v3+json",
    }

    # Add authorization if token is provided
    if token:
        headers["Authorization"] = f"token {token}"

    since_dt: datetime | None = None
    if since is not None:
        since_dt = parse_iso_datetime(since)
        if since_dt is None:
            msg = "Invalid ISO 8601 datetime provided for --since option"
            raise ValueError(msg)

    # Fetch review comments
    review_comments = fetch_paginated_comments(api_url, headers)

    # Fetch issue comments (general PR comments, not line-specific)
    issue_api_url = f"https://api.github.com/repos/{project}/issues/{pr}/comments"
    issue_params = {"since": since} if since else None
    issue_comments = fetch_paginated_comments(issue_api_url, headers, issue_params)

    for comment in issue_comments:
        comment["comment_type"] = "issue"

    all_comments = [*review_comments, *issue_comments]

    if since_dt:
        filtered_comments: list[dict[str, Any]] = []
        for comment in all_comments:
            comment_dt = parse_iso_datetime(comment.get("created_at", ""))
            if comment_dt and comment_dt >= since_dt:
                filtered_comments.append(comment)
        all_comments = filtered_comments

    # Sort by created_at, most recent first
    all_comments.sort(
        key=lambda x: parse_iso_datetime(x.get("created_at"))
        or datetime.min.replace(tzinfo=UTC),
        reverse=True,
    )

    # Apply quantity filter if specified
    if quantity:
        all_comments = all_comments[:quantity]

    # Convert to PRComment objects
    return [
        PRComment(
            comment_id=comment["id"],
            comment_url=comment.get("html_url", ""),
            author=comment["user"]["login"],
            created_at=comment["created_at"],
            updated_at=comment.get("updated_at", comment["created_at"]),
            comment_type=comment.get("comment_type", "review"),
            path=comment.get("path"),
            position=comment.get("position"),
            line=comment.get("line"),
            text=comment.get("body", ""),
            implementation_comments=None,
            viewed=False,
            completed=False,
            project=project,
            pr=pr,
        )
        for comment in all_comments
    ]


def generate_agents_file(
    output_dir: Path,
    project: str,
    pr: int,
    total_comments: int,
) -> Path:
    """Generate AGENTS.md file with instructions.

    Args:
        output_dir: Directory to output the file
        project: Repository in format "owner/repo"
        pr: Pull request number
        total_comments: Total number of comments

    Returns:
        Path to the generated file

    """
    from .prompts import render_agents_md

    agents_file = output_dir / "AGENTS.md"

    content = render_agents_md(
        project=project,
        pr=pr,
        total_comments=total_comments,
    )

    try:
        with agents_file.open("w") as f:
            f.write(content)
    except OSError as exc:
        msg = f"Unable to write AGENTS.md file to {agents_file}"
        raise OSError(msg) from exc

    return agents_file


def generate_hooks_file(jsonl_file: Path, output_dir: Path) -> Path:
    """Generate Claude Code hooks configuration file.

    Args:
        jsonl_file: Path to the JSONL file with comments
        output_dir: Directory to output the hooks file

    Returns:
        Path to the generated hooks file

    """
    hooks_config = render_hooks_config(jsonl_file)

    hooks_file = output_dir / ".claude" / "settings.json"
    hooks_file.parent.mkdir(parents=True, exist_ok=True)

    # Read existing settings if any
    existing_settings: dict[str, Any] = {}
    if hooks_file.exists():
        try:
            with hooks_file.open("r") as f:
                existing_settings = json.load(f)
        except json.JSONDecodeError as exc:
            msg = f"Existing hooks configuration {hooks_file} contains invalid JSON"
            raise ValueError(
                msg,
            ) from exc
        except OSError as exc:
            msg = f"Unable to read existing hooks configuration at {hooks_file}"
            raise OSError(
                msg,
            ) from exc

    # Merge hooks
    if "hooks" not in existing_settings:
        existing_settings["hooks"] = {}

    existing_settings["hooks"]["SessionStart"] = hooks_config["hooks"]["SessionStart"]

    # Write updated settings
    try:
        with hooks_file.open("w") as f:
            json.dump(existing_settings, f, indent=2)
    except OSError as exc:
        msg = f"Unable to write hooks configuration to {hooks_file}"
        raise OSError(msg) from exc

    return hooks_file


def generate_processor_script(output_dir: Path) -> Path:
    """Generate a Python script that processes comments one at a time.

    Args:
        output_dir: Directory to output the processor script

    Returns:
        Path to the generated processor script

    """
    processor_script = output_dir / "process_comments.py"

    script_content = render_processor_script()

    try:
        with processor_script.open("w") as f:
            f.write(script_content)
    except OSError as exc:
        msg = f"Unable to write processor script to {processor_script}"
        raise OSError(msg) from exc

    try:
        processor_script.chmod(0o755)
    except OSError as exc:
        msg = f"Unable to set execute permissions on {processor_script}"
        raise OSError(msg) from exc

    return processor_script


def fetch_and_save_comments(
    project: str,
    pr: int,
    token: str | None = None,
    since: str | None = None,
    quantity: int | None = None,
    output: Path = Path("pr_comments.jsonl"),
    hooks: bool = False,
) -> None:
    """Fetch PR comments and save to JSONL file.

    Args:
        project: Repository in format "owner/repo"
        pr: Pull request number
        token: GitHub personal access token
        since: ISO 8601 date to filter comments
        quantity: Maximum number of comments to fetch
        output: Output JSONL file path
        hooks: Whether to generate Claude Code hooks

    """
    # Validate project format
    if "/" not in project:
        typer.echo(
            f"Error: Project must be in format 'owner/repo', got '{project}'",
            err=True,
        )
        raise typer.Exit(1)

    # Get token from environment if not provided
    if not token:
        token = os.getenv("GITHUB_TOKEN")
        if token:
            typer.echo("Using token from GITHUB_TOKEN environment variable")
        else:
            typer.echo(
                "Warning: No token provided. Using unauthenticated requests (may have rate limits)",
                err=True,
            )

    typer.echo(f"Fetching comments from {project} PR #{pr}...")

    try:
        # Fetch comments
        comments = fetch_pr_comments(token, project, pr, since, quantity)

        typer.echo(f"Found {len(comments)} comments")

        # Save to JSONL
        try:
            with output.open("w") as f:
                for comment in comments:
                    f.write(json.dumps(comment.to_dict()) + "\n")
        except OSError as exc:
            msg = f"Unable to write output file {output}"
            raise OSError(msg) from exc

        typer.echo(f"✓ Wrote {len(comments)} comments to {output}")

        # Generate hooks if requested
        if hooks:
            output_dir = output.parent
            hooks_file = generate_hooks_file(output, output_dir)
            processor_script = generate_processor_script(output_dir)

            typer.echo(f"✓ Generated hooks file: {hooks_file}")
            typer.echo(f"✓ Generated processor script: {processor_script}")
            typer.echo(
                "\nTo use: Add the .claude directory to your project and run Claude Code.",
            )
            typer.echo(
                "The SessionStart hook will process comments one at a time automatically.",
            )

    except ValueError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1)
    except RequestException as exc:
        typer.echo(f"Error fetching comments: {exc}", err=True)
        raise typer.Exit(1)
    except OSError as exc:
        typer.echo(f"File system error: {exc}", err=True)
        raise typer.Exit(1)
