"""Jinja templates for prompts and messages."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

# Initialize Jinja2 environment
env = Environment(
    loader=PackageLoader("pr_to_task", "templates"),
    autoescape=select_autoescape(),
)


def render_task_next_prompt(comment_text: str) -> str:
    """Render the task next prompt with the comment text."""
    template = env.get_template("task_next_prompt.txt")
    return template.render(comment_text=comment_text)


def render_task_complete_confirmation(next_comment_text: str) -> str:
    """Render the task complete confirmation with next comment."""
    template = env.get_template("task_complete_confirmation.txt")
    return template.render(comment_text=next_comment_text)


def render_all_tasks_complete() -> str:
    """Render the all tasks complete message."""
    template = env.get_template("all_tasks_complete.txt")
    return template.render()


def render_agents_md(project: str, pr: int, total_comments: int) -> str:
    """Render the AGENTS.md file content."""
    template = env.get_template("agents_md.md")
    return template.render(
        project=project,
        pr=pr,
        total_comments=total_comments,
    )


def render_processor_script() -> str:
    """Render the processor script content."""
    template = env.get_template("process_comments.py.j2")
    return template.render()


def render_hooks_config(jsonl_file: Path) -> dict[str, Any]:
    """Render the hooks configuration."""
    import shlex

    jsonl_argument = shlex.quote(str(jsonl_file))
    return {
        "hooks": {
            "SessionStart": {
                "command": f"pr_to_task task next {jsonl_argument}",
                "description": "Process PR comments one at a time",
            },
        },
    }
