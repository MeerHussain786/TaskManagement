"""
Task API Router.

Provides thin endpoints for task CRUD operations, pagination, search,
filtering, sorting, and idempotent completion marking.
All operations require authentication and enforce resource ownership.
"""

import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.task import TaskPriority
from app.models.user import User
from app.schemas.common import ErrorResponse, PaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
    },
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    payload: TaskCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """
    Create a new task owned by the authenticated user.
    """
    task_service = TaskService(db)
    return await task_service.create_task(current_user.id, payload)


@router.get(
    "",
    response_model=PaginatedResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List tasks with pagination, filters, sorting and search",
)
async def list_tasks(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    completed: Annotated[bool | None, Query(description="Filter by completion status")] = None,
    priority: Annotated[TaskPriority | None, Query(description="Filter by priority")] = None,
    due_before: Annotated[date | None, Query(description="Filter tasks due on/before date")] = None,
    due_after: Annotated[date | None, Query(description="Filter tasks due on/after date")] = None,
    search: Annotated[str | None, Query(description="Text search on title/description")] = None,
    sort_by: Annotated[
        Literal["created_at", "due_date", "priority", "title"],
        Query(description="Property to sort by"),
    ] = "created_at",
    order: Annotated[Literal["asc", "desc"], Query(description="Sort ordering")] = "desc",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
) -> PaginatedResponse[TaskResponse]:
    """
    Query, filter, search, and page through the authenticated user's tasks.
    """
    task_service = TaskService(db)
    return await task_service.list_tasks(
        current_user.id,
        completed=completed,
        priority=priority,
        due_before=due_before,
        due_after=due_after,
        search_query=search,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get task details",
)
async def get_task(
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """
    Fetch details for a specific task. Enforces that task belongs to the caller.
    """
    task_service = TaskService(db)
    return await task_service.get_task(task_id, current_user.id)


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
)
async def update_task(
    task_id: uuid.UUID,
    payload: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """
    Modify details (title, status, priority, due date) of an existing user-owned task.
    """
    task_service = TaskService(db)
    return await task_service.update_task(task_id, current_user.id, payload)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Permanently delete a task belonging to the caller.
    """
    task_service = TaskService(db)
    await task_service.delete_task(task_id, current_user.id)


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark task as completed",
)
async def complete_task(
    task_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    """
    Idempotently mark a task completed.
    """
    task_service = TaskService(db)
    return await task_service.complete_task(task_id, current_user.id)

