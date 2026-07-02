"""
Task Business Logic Service.

Implements all CRUD operations for Tasks, enforces ownership validation,
incorporates structured audit logging, and manages Redis-based caching
with selective invalidation on state mutations.
"""

import json
import uuid
from datetime import date
from typing import Literal

from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import CacheService
from app.core.exceptions import TaskNotFoundException
from app.core.logging import get_logger
from app.models.task import Task, TaskPriority
from app.repositories.task_repository import TaskRepository
from app.schemas.common import PaginatedMetadata, PaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

logger = get_logger(__name__)


class TaskService:
    """Business service governing task CRUD logic and caching."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.task_repo = TaskRepository(db)
        self.cache = CacheService()

    async def create_task(self, owner_id: uuid.UUID, payload: TaskCreate) -> TaskResponse:
        """Create a new task for the authenticated user and invalidate caches."""
        new_task = Task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            due_date=payload.due_date,
            owner_id=owner_id,
            completed=False,
        )
        await self.task_repo.create(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)

        # Clear cache for this user's tasks
        await self._invalidate_user_cache(owner_id)

        logger.info("task_created", task_id=new_task.id, owner_id=owner_id)
        return TaskResponse.model_validate(new_task)

    async def get_task(self, task_id: uuid.UUID, owner_id: uuid.UUID) -> TaskResponse:
        """
        Retrieve a single task, verifying ownership. Uses Cache-Aside pattern.

        Raises:
            TaskNotFoundException: If task is missing or owned by another user.
        """
        cache_key = f"cache:task:{owner_id}:{task_id}"

        # Try cache
        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                return TaskResponse.model_validate_json(cached_data)
            except Exception as e:
                logger.warning("failed_parsing_cached_task", key=cache_key, error=str(e))

        # DB fallback
        task = await self.task_repo.get_user_task(task_id, owner_id)
        if not task:
            raise TaskNotFoundException(task_id=str(task_id))

        response = TaskResponse.model_validate(task)

        # Cache for next time (15 mins)
        await self.cache.set(cache_key, response.model_dump_json(), ttl=900)

        return response

    async def list_tasks(
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
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedResponse[TaskResponse]:
        """
        List paginated tasks matching query filters, checking Cache-Aside.
        """
        # Create a deterministic key from query parameters
        params_str = (
            f"c={completed}&p={priority}&db={due_before}&da={due_after}&"
            f"s={search_query}&sb={sort_by}&o={order}&pg={page}&ps={page_size}"
        )
        cache_key = f"cache:tasks:{owner_id}:{params_str}"

        cached_data = await self.cache.get(cache_key)
        if cached_data:
            try:
                # Setup proper generic deserialization
                adapter = TypeAdapter(PaginatedResponse[TaskResponse])
                return adapter.validate_json(cached_data)
            except Exception as e:
                logger.warning("failed_parsing_cached_task_list", key=cache_key, error=str(e))

        # Calculate offsets
        offset = (page - 1) * page_size
        tasks, total_count = await self.task_repo.get_user_tasks(
            owner_id,
            completed=completed,
            priority=priority,
            due_before=due_before,
            due_after=due_after,
            search_query=search_query,
            sort_by=sort_by,
            order=order,
            offset=offset,
            limit=page_size,
        )

        # Build response
        task_responses = [TaskResponse.model_validate(t) for t in tasks]
        total_pages = max(1, (total_count + page_size - 1) // page_size)

        response = PaginatedResponse[TaskResponse](
            items=task_responses,
            metadata=PaginatedMetadata(
                total=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            ),
        )

        # Store in Cache (5 mins)
        await self.cache.set(cache_key, response.model_dump_json(), ttl=300)

        return response

    async def update_task(
        self, task_id: uuid.UUID, owner_id: uuid.UUID, payload: TaskUpdate
    ) -> TaskResponse:
        """
        Update task details and invalidate caches.

        Raises:
            TaskNotFoundException: If task is missing or owned by another user.
        """
        task = await self.task_repo.get_user_task(task_id, owner_id)
        if not task:
            raise TaskNotFoundException(task_id=str(task_id))

        # Patch attributes
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        await self.task_repo.update(task)
        await self.db.commit()
        await self.db.refresh(task)

        # Clear Cache
        await self._invalidate_user_cache(owner_id)
        await self.cache.delete(f"cache:task:{owner_id}:{task_id}")

        logger.info("task_updated", task_id=task_id, owner_id=owner_id)
        return TaskResponse.model_validate(task)

    async def delete_task(self, task_id: uuid.UUID, owner_id: uuid.UUID) -> None:
        """
        Delete a task and invalidate caches.

        Raises:
            TaskNotFoundException: If task is missing or owned by another user.
        """
        task = await self.task_repo.get_user_task(task_id, owner_id)
        if not task:
            raise TaskNotFoundException(task_id=str(task_id))

        await self.task_repo.delete(task_id)
        await self.db.commit()

        # Clear Cache
        await self._invalidate_user_cache(owner_id)
        await self.cache.delete(f"cache:task:{owner_id}:{task_id}")

        logger.info("task_deleted", task_id=task_id, owner_id=owner_id)

    async def complete_task(self, task_id: uuid.UUID, owner_id: uuid.UUID) -> TaskResponse:
        """
        Mark a task completed idempotently and invalidate caches.

        Raises:
            TaskNotFoundException: If task is missing or owned by another user.
        """
        task = await self.task_repo.get_user_task(task_id, owner_id)
        if not task:
            raise TaskNotFoundException(task_id=str(task_id))

        if not task.completed:
            task.completed = True
            await self.task_repo.update(task)
            await self.db.commit()
            await self.db.refresh(task)

            # Invalidate caches
            await self._invalidate_user_cache(owner_id)
            await self.cache.delete(f"cache:task:{owner_id}:{task_id}")

            logger.info("task_completed_success", task_id=task_id, owner_id=owner_id)

        return TaskResponse.model_validate(task)

    async def _invalidate_user_cache(self, owner_id: uuid.UUID) -> None:
        """Invalides all cached task listings for a user by scanning pattern match keys."""
        if not self.cache.client:
            return

        pattern = f"cache:tasks:{owner_id}:*"
        try:
            cursor = 0
            keys_to_delete = []
            while True:
                cursor, keys = await self.cache.client.scan(cursor, match=pattern, count=100)
                keys_to_delete.extend(keys)
                if cursor == 0:
                    break

            if keys_to_delete:
                await self.cache.client.delete(*keys_to_delete)
                logger.info("user_task_caches_invalidated", owner_id=owner_id, count=len(keys_to_delete))
        except Exception as e:
            logger.error("cache_invalidation_error", owner_id=owner_id, error=str(e))
