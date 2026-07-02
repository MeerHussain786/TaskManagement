"""
Unit Tests for Service Layer (Service logic mocking repository dependencies).
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ConflictException, UserNotFoundException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdate
from app.services.user_service import UserService


@pytest.mark.asyncio
async def test_get_profile_success():
    """Verify UserService retrieves profile successfully if user exists."""
    db_mock = MagicMock()
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@example.com", username="test", full_name="Test")
    
    # Mock repository
    repo_mock = MagicMock(spec=UserRepository)
    repo_mock.get = AsyncMock(return_value=mock_user)
    
    service = UserService(db_mock)
    service.user_repo = repo_mock
    
    result = await service.get_profile(user_id)
    
    assert result == mock_user
    repo_mock.get.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_get_profile_not_found():
    """Verify UserService raises UserNotFoundException if user is missing."""
    db_mock = MagicMock()
    user_id = uuid.uuid4()
    
    repo_mock = MagicMock(spec=UserRepository)
    repo_mock.get = AsyncMock(return_value=None)
    
    service = UserService(db_mock)
    service.user_repo = repo_mock
    
    with pytest.raises(UserNotFoundException):
        await service.get_profile(user_id)


@pytest.mark.asyncio
async def test_update_profile_conflict():
    """Verify UserService raises ConflictException if email is already taken."""
    db_mock = MagicMock()
    user_id = uuid.uuid4()
    mock_user = User(id=user_id, email="test@example.com", username="test", full_name="Test")
    
    repo_mock = MagicMock(spec=UserRepository)
    repo_mock.get = AsyncMock(return_value=mock_user)
    repo_mock.exists_by_email = AsyncMock(return_value=True)  # Email taken
    
    service = UserService(db_mock)
    service.user_repo = repo_mock
    
    payload = UserUpdate(email="taken@example.com")
    
    with pytest.raises(ConflictException):
        await service.update_profile(user_id, payload)
