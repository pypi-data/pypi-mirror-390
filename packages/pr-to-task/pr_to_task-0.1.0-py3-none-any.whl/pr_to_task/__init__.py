__version__ = "0.1.0"

from pr_to_task.main import app, main
from pr_to_task.models import PRComment, TaskState
from pr_to_task.pr_fetch import (
    fetch_pr_comments,
    generate_agents_file,
    generate_hooks_file,
    generate_processor_script,
)
from pr_to_task.tasks import (
    task_init,
    task_mark_complete,
    task_next,
    task_reset,
    task_status,
)

# Public API exports
__all__ = [
    # Models
    "PRComment",
    "TaskState",
    # Main entry points
    "app",
    # PR fetch functions
    "fetch_pr_comments",
    "generate_agents_file",
    "generate_hooks_file",
    "generate_processor_script",
    "main",
    # Task management functions
    "task_init",
    "task_mark_complete",
    "task_next",
    "task_reset",
    "task_status",
]
