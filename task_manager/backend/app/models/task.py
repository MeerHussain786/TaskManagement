"""
Task Domain Model.

Represents a user-owned task with priority levels, due dates,
and completion tracking.
"""

import enum
import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Index, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class TaskPriority(str, enum.Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(Base, UUIDMixin, TimestampMixin):
    """
    Task model.

    Attributes:
        id: UUID primary key.
        title: Task title (max 255 chars).
        description: Optional detailed description.
        completed: Whether the task is done.
        priority: Priority level (low/medium/high/critical).
        due_date: Optional due date.
        owner_id: FK to the owning user.
    """

    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
        index=True,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, native_enum=False, length=20),
        default=TaskPriority.MEDIUM,
        server_default=TaskPriority.MEDIUM.value,
        nullable=False,
        index=True,
    )
    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        default=None,
        index=True,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    tags: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )
    reminder_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        default=None,
    )
    recurring_rule: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
    )
    subtasks: Mapped[list[dict] | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )

    # ── Relationships ────────────────────────────────────────────────────
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="tasks",
        lazy="noload",
    )
    project: Mapped["Project | None"] = relationship(
        "Project",
        back_populates="tasks",
        lazy="noload",
    )

    # ── Table Configuration ──────────────────────────────────────────────
    __table_args__ = (
        Index("ix_tasks_owner_completed", "owner_id", "completed"),
        Index("ix_tasks_owner_priority", "owner_id", "priority"),
        Index("ix_tasks_owner_due_date", "owner_id", "due_date"),
        {"comment": "User tasks with priority and due date tracking"},
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title!r}, completed={self.completed})>"
