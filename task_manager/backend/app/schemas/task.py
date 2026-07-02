"""
Task Pydantic Schemas.

Defines validation and serialization rules for Task CRUD, including
sorting, filtering, and pagination query schemas.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.task import TaskPriority


class TaskBase(BaseModel):
    """Shared fields for Task models."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title",
        examples=["Complete implementation review"],
    )
    description: str | None = Field(
        default=None,
        description="Detailed task description",
        examples=["Review all schemas, repositories, and routers before code generation"],
    )
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority level",
        examples=[TaskPriority.HIGH],
    )
    due_date: date | None = Field(
        default=None,
        description="Optional date the task is due",
        examples=["2026-06-30"],
    )
    tags: list[str] | None = Field(
        default=None,
        description="List of tags for categorization",
        examples=[["work", "urgent"]],
    )
    reminder_at: datetime | None = Field(
        default=None,
        description="Optional date and time to remind the user",
        examples=["2026-06-30T15:00:00Z"],
    )
    recurring_rule: str | None = Field(
        default=None,
        description="Optional recurring rule like daily, weekly, monthly",
        examples=["daily"],
    )
    subtasks: list[dict] | None = Field(
        default=None,
        description="List of subtasks with title and completed status",
        examples=[[{"title": "Step 1", "completed": False}]],
    )


class TaskCreate(TaskBase):
    """Payload required to create a new task."""

    pass


class TaskUpdate(BaseModel):
    """Payload to update an existing task. All fields are optional."""

    title: str | None = Field(default=None, min_length=1, max_length=255, description="New title")
    description: str | None = Field(default=None, description="New description")
    completed: bool | None = Field(default=None, description="Updated completion status")
    priority: TaskPriority | None = Field(default=None, description="New priority level")
    due_date: date | None = Field(default=None, description="New due date")
    tags: list[str] | None = Field(default=None, description="New tags")
    reminder_at: datetime | None = Field(default=None, description="New reminder date and time")
    recurring_rule: str | None = Field(default=None, description="New recurring rule")
    subtasks: list[dict] | None = Field(default=None, description="New list of subtasks")


class TaskResponse(TaskBase):
    """Serialized task representation for API responses."""

    id: uuid.UUID = Field(..., description="Unique task identifier")
    completed: bool = Field(..., description="Whether the task has been marked completed")
    owner_id: uuid.UUID = Field(..., description="UUID of the user who owns this task")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last updated timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
