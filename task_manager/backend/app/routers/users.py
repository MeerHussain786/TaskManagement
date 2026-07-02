"""
User API Router.

Exposes profile management endpoints for the currently authenticated user.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.common import ErrorResponse
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        409: {"model": ErrorResponse, "description": "Conflict"},
    },
)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> UserResponse:
    """
    Retrieve details about the currently authenticated user profile.
    """
    return UserResponse.from_orm(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
)
async def update_me(
    payload: UserUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Update profile details (email, username, full name) for the active user.
    Validates uniqueness parameters to prevent credential collisions.
    """
    user_service = UserService(db)
    updated_user = await user_service.update_profile(current_user.id, payload)
    return UserResponse.from_orm(updated_user)
