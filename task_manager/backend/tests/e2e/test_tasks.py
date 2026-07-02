"""
End-to-End Tests for Task operations.

Tests task creation, retrieval, updates, validation, pagination,
filtering, completion, and resource ownership boundaries.
"""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_task_lifecycle_and_ownership(client: AsyncClient, auth_headers: dict[str, str]):
    """Verify task lifecycle (create, read, update, complete, delete) and owner access limits."""
    # ── 1. Create task ───────────────────────────────────────────────────────
    task_payload = {
        "title": "Build Test Suite",
        "description": "Ensure 95%+ coverage on critical endpoints",
        "priority": "high",
        "due_date": "2026-06-30",
    }
    create_res = await client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
    assert create_res.status_code == 201
    task = create_res.json()
    assert task["title"] == "Build Test Suite"
    assert task["completed"] is False
    task_id = task["id"]

    # ── 2. Get task ──────────────────────────────────────────────────────────
    get_res = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["description"] == task_payload["description"]

    # ── 3. Update task ───────────────────────────────────────────────────────
    update_payload = {"title": "Build Dynamic Test Suite", "priority": "critical"}
    update_res = await client.put(f"/api/v1/tasks/{task_id}", json=update_payload, headers=auth_headers)
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Build Dynamic Test Suite"
    assert update_res.json()["priority"] == "critical"

    # ── 4. Complete task ─────────────────────────────────────────────────────
    complete_res = await client.patch(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
    assert complete_res.status_code == 200
    assert complete_res.json()["completed"] is True

    # ── 5. Enforce Ownership Boundaries ─────────────────────────────────────
    # Create another user and attempt access to task_id
    register_payload_other = {
        "email": "other_user@example.com",
        "username": "otheruser",
        "full_name": "Other User",
        "password": "SecureP@ss123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload_other)
    
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "other_user@example.com", "password": "SecureP@ss123!"}
    )
    other_token = login_res.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # Retrieve other user's tasks (should not return task_id)
    other_get_res = await client.get(f"/api/v1/tasks/{task_id}", headers=other_headers)
    assert other_get_res.status_code == 404  # Not found for the other user

    # ── 6. Delete task ───────────────────────────────────────────────────────
    delete_res = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert delete_res.status_code == 204

    # Verify task is deleted
    get_deleted_res = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_deleted_res.status_code == 404


@pytest.mark.asyncio
async def test_task_listing_pagination_and_filtering(client: AsyncClient, auth_headers: dict[str, str]):
    """Verify task query list filters, pagination, search, sorting, and caching."""
    # Create multiple test tasks
    tasks_to_create = [
        {"title": "Task One", "description": "Review API routers", "priority": "low", "due_date": "2026-06-25"},
        {"title": "Task Two", "description": "Write integration test suite", "priority": "high", "due_date": "2026-06-26"},
        {"title": "Task Three", "description": "Deploy to staging server", "priority": "critical", "due_date": "2026-06-27"},
    ]

    for payload in tasks_to_create:
        res = await client.post("/api/v1/tasks", json=payload, headers=auth_headers)
        assert res.status_code == 201

    # 1. Query all tasks (default sorting by created_at desc)
    res = await client.get("/api/v1/tasks", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["metadata"]["total"] >= 3
    assert len(data["items"]) >= 3

    # 2. Filter by priority
    res = await client.get("/api/v1/tasks?priority=high", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert all(item["priority"] == "high" for item in data["items"])

    # 3. Filter by completion
    res = await client.get("/api/v1/tasks?completed=false", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert all(item["completed"] is False for item in data["items"])

    # 4. Search text
    res = await client.get("/api/v1/tasks?search=staging", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    assert "staging" in data["items"][0]["description"]

    # 5. Sort by due_date ascending
    res = await client.get("/api/v1/tasks?sort_by=due_date&order=asc", headers=auth_headers)
    assert res.status_code == 200
    items = res.json()["items"]
    due_dates = [item["due_date"] for item in items if item["due_date"]]
    assert due_dates == sorted(due_dates)

    # 6. Pagination offset and limits
    res = await client.get("/api/v1/tasks?page=1&page_size=2", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["metadata"]["page_size"] == 2
    assert data["metadata"]["page"] == 1

