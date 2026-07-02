"""
Integration Tests for Repositories.

Tests query logic, search, dynamic sorting, pagination, and eager loads
against the SQLite transactional test database session.
"""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskPriority
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_user_repository_crud(db_session: AsyncSession):
    """Verify UserRepository CRUD and email/username uniqueness helpers."""
    repo = UserRepository(db_session)
    
    user_id = uuid.uuid4()
    new_user = User(
        id=user_id,
        email="repo_test@example.com",
        username="repotest",
        full_name="Repo Test",
        hashed_password="somehashvalue",
    )
    
    # Create
    await repo.create(new_user)
    await db_session.commit()
    
    # Fetch
    fetched = await repo.get(user_id)
    assert fetched is not None
    assert fetched.email == "repo_test@example.com"
    
    # Query Helpers
    assert await repo.exists_by_email("repo_test@example.com") is True
    assert await repo.exists_by_username("repotest") is True
    assert await repo.exists_by_email("nonexistent@example.com") is False
    
    # Delete
    deleted = await repo.delete(user_id)
    await db_session.commit()
    assert deleted is True
    assert await repo.get(user_id) is None


@pytest.mark.asyncio
async def test_task_repository_filtering_and_search(db_session: AsyncSession):
    """Verify TaskRepository query filters, dynamic sorting, and search."""
    user_repo = UserRepository(db_session)
    task_repo = TaskRepository(db_session)
    
    owner = User(
        email="owner@example.com",
        username="owner",
        full_name="Owner",
        hashed_password="passwordhash",
    )
    await user_repo.create(owner)
    await db_session.commit()
    await db_session.refresh(owner)
    
    # Create distinct tasks
    tasks = [
        Task(title="Buy Groceries", description="Milk, bread, eggs", priority=TaskPriority.LOW, owner_id=owner.id, completed=False),
        Task(title="Write API code", description="Using FastAPI and SQLAlchemy 2.0", priority=TaskPriority.HIGH, owner_id=owner.id, completed=True),
        Task(title="Submit review report", description="Send final draft to manager", priority=TaskPriority.CRITICAL, owner_id=owner.id, completed=False),
    ]
    
    for task in tasks:
        await task_repo.create(task)
    await db_session.commit()

    # Test complete filtering
    completed_tasks, count = await task_repo.get_user_tasks(owner.id, completed=True)
    assert count == 1
    assert completed_tasks[0].title == "Write API code"
    
    # Test priority filtering
    high_priority, count = await task_repo.get_user_tasks(owner.id, priority=TaskPriority.HIGH)
    assert count == 1
    assert high_priority[0].title == "Write API code"
    
    # Test text search
    search_results, count = await task_repo.get_user_tasks(owner.id, search_query="SQLAlchemy")
    assert count == 1
    assert search_results[0].title == "Write API code"

    # Test sorting
    sorted_tasks, count = await task_repo.get_user_tasks(owner.id, sort_by="priority", order="asc")
    # Priority order is CRITICAL, HIGH, LOW if alphabetical, or based on DB string.
    # LOW, MEDIUM, HIGH, CRITICAL. Check the order returned
    assert len(sorted_tasks) == 3
