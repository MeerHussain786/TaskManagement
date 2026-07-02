"""
Project Domain Model.

Represents a user-owned project that groups tasks together.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class Project(Base, UUIDMixin, TimestampMixin):
    """
    Project model for organizing tasks.

    Attributes:
        id: UUID primary key.
        name: Project name.
        description: Optional description.
        owner_id: FK to the owning user.
    """

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Relationships ────────────────────────────────────────────────────
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="projects",
        lazy="noload",
    )
    
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="noload",
    )

    # ── Table Configuration ──────────────────────────────────────────────
    __table_args__ = (
        Index("ix_projects_owner", "owner_id"),
        {"comment": "User projects for organizing tasks"},
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name!r})>"
