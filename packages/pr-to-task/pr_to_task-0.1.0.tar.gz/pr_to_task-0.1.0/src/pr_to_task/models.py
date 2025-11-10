"""Data models for PR to Task processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PRComment:
    """Represents a PR comment with all metadata."""

    comment_id: int
    comment_url: str
    author: str
    created_at: str
    updated_at: str
    comment_type: str  # "review" or "issue"
    text: str
    path: str | None = None
    position: int | None = None
    line: int | None = None
    implementation_comments: str | None = None
    viewed: bool = False
    completed: bool = False
    project: str | None = None
    pr: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "comment_id": self.comment_id,
            "comment_url": self.comment_url,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "comment_type": self.comment_type,
            "path": self.path,
            "position": self.position,
            "line": self.line,
            "text": self.text,
            "implementation_comments": self.implementation_comments,
            "viewed": self.viewed,
            "completed": self.completed,
            "project": self.project,
            "pr": self.pr,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PRComment:
        """Create from dictionary."""
        return cls(
            comment_id=data["comment_id"],
            comment_url=data["comment_url"],
            author=data["author"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            comment_type=data.get("comment_type", "review"),
            text=data["text"],
            path=data.get("path"),
            position=data.get("position"),
            line=data.get("line"),
            implementation_comments=data.get("implementation_comments"),
            viewed=data.get("viewed", False),
            completed=data.get("completed", False),
            project=data.get("project"),
            pr=data.get("pr"),
        )


@dataclass
class TaskState:
    """Represents the state of all tasks."""

    comments: list[PRComment] = field(default_factory=list)

    @property
    def total(self) -> int:
        """Total number of tasks."""
        return len(self.comments)

    @property
    def completed(self) -> int:
        """Number of completed tasks."""
        return sum(1 for c in self.comments if c.completed)

    @property
    def viewed(self) -> int:
        """Number of viewed tasks."""
        return sum(1 for c in self.comments if c.viewed)

    @property
    def remaining(self) -> int:
        """Number of remaining tasks."""
        return self.total - self.completed

    @property
    def current_index(self) -> int | None:
        """Index of current task (viewed but not completed)."""
        for i, comment in enumerate(self.comments):
            if comment.viewed and not comment.completed:
                return i
        return None

    def get_next_task_index(self) -> int | None:
        """Get index of next uncompleted task."""
        for i, comment in enumerate(self.comments):
            if not comment.completed:
                return i
        return None

    def to_dicts(self) -> list[dict[str, Any]]:
        """Convert all comments to dictionaries."""
        return [comment.to_dict() for comment in self.comments]

    @classmethod
    def from_dicts(cls, data: list[dict[str, Any]]) -> TaskState:
        """Create from list of dictionaries."""
        comments = [PRComment.from_dict(item) for item in data]
        return cls(comments=comments)
