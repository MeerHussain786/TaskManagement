"""
Task Repository implementation.

Handles dynamic filtering, sorting, pagination, and full-text search
for User tasks, preventing N+1 queries using selective eager loading.
"""

import uuid
from datetime import date
from typing import Literal

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskPriority
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository managing Task database query building and execution."""

    def __init__(self, db) -> None:
        super().__init__(Task, db)

    async def get_user_task(self, task_id: uuid.UUID, owner_id: uuid.UUID) -> Task | None:
        """Retrieve a task owned by a specific user, preventing unauthorized access."""
        query = select(Task).where(and_(Task.id == task_id, Task.owner_id == owner_id))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_tasks(
        self,
        owner_id: uuid.UUID,
        *,
        completed: bool | None = None,
        priority: TaskPriority | None = None,
        due_before: date | None = None,
        due_after: date | None = None,
        search_query: str | None = None,
        sort_by: str = "created_at",
        order: Literal["asc", "desc"] = "desc",
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Task], int]:
        """
        Query user tasks with advanced filtering, sorting, search, and pagination.

        Returns:
            A tuple of (tasks list, total matching tasks count).
        """
        # Base select query
        stmt = select(Task).where(Task.owner_id == owner_id)

        # Filters
        if completed is not None:
            stmt = stmt.where(Task.completed == completed)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        if due_before is not None:
            stmt = stmt.where(Task.due_date <= due_before)
        if due_after is not None:
            stmt = stmt.where(Task.due_date >= due_after)

        # Search (case-insensitive on title and description)
        if search_query:
            search_pattern = f"%{search_query}%"
            stmt = stmt.where(
                or_(
                    Task.title.ilike(search_pattern),
                    Task.description.ilike(search_pattern),
                )
            )

        # Count total matches before pagination
        from sqlalchemy import func

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar() or 0


        # Sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        # Pagination
        stmt = stmt.offset(offset).limit(limit)

        # Eager load owner to prevent N+1 queries if needed (although task schemas decouple owner_id)
        stmt = stmt.options(selectinload(Task.owner))

        result = await self.db.execute(stmt)
        tasks = list(result.scalars().all())

        return tasks, total_count
