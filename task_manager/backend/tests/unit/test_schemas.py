"""
Unit Tests for Pydantic Validation Schemas.
"""

import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest, RefreshTokenRequest
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.user import UserCreate, UserUpdate


def test_user_create_validation_success():
    """Verify UserCreate succeeds with valid fields."""
    payload = {
        "email": "jane.doe@example.com",
        "username": "janedoe_1",
        "full_name": "Jane Doe",
        "password": "SecureP@ss123!",
    }
    schema = UserCreate(**payload)
    assert schema.email == payload["email"]
    assert schema.username == payload["username"]


def test_user_create_validation_username_failures():
    """Verify invalid usernames fail validation constraint."""
    invalid_usernames = ["ab", "user name", "user-name!", "a"*51]
    
    for username in invalid_usernames:
        payload = {
            "email": "jane.doe@example.com",
            "username": username,
            "full_name": "Jane Doe",
            "password": "SecureP@ss123!",
        }
        with pytest.raises(ValidationError):
            UserCreate(**payload)


def test_user_create_validation_password_failures():
    """Verify password complexity requirements enforce uppercase, lowercase, numbers, and symbols."""
    invalid_passwords = [
        "short1!",        # too short (7 chars)
        "nouppercase1!",    # missing uppercase
        "NOLOWERCASE1!",    # missing lowercase
        "NoDigitHere!",     # missing digit
        "NoSpecialChar123", # missing special character
    ]

    for password in invalid_passwords:
        payload = {
            "email": "jane.doe@example.com",
            "username": "janedoe",
            "full_name": "Jane Doe",
            "password": password,
        }
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**payload)
        assert "password" in str(exc_info.value)


def test_user_update_validation():
    """Verify UserUpdate validation limits."""
    # Empty update is okay (all optional)
    schema = UserUpdate()
    assert schema.email is None

    # Partial update validation
    schema = UserUpdate(full_name="New Name")
    assert schema.full_name == "New Name"

    # Invalid username inside update
    with pytest.raises(ValidationError):
        UserUpdate(username="invalid username")


def test_task_create_validation():
    """Verify TaskCreate schema defaults and validation."""
    payload = {
        "title": "My Task",
        "description": "Task description",
    }
    schema = TaskCreate(**payload)
    assert schema.title == "My Task"
    assert schema.priority.value == "medium"  # Default
    assert schema.due_date is None

    # Missing title must fail
    with pytest.raises(ValidationError):
        TaskCreate(description="only description")


def test_task_update_validation():
    """Verify TaskUpdate allows optional fields."""
    schema = TaskUpdate(completed=True)
    assert schema.completed is True
    assert schema.title is None
