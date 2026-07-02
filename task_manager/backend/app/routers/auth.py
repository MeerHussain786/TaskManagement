"""
Authentication API Router.

Exposes endpoints for registration, login, token refresh, and logout.
Uses dependency injection to resolve db sessions and service logic.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.common import ErrorResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        429: {"model": ErrorResponse, "description": "Too Many Requests"},
    },
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """
    Register a new user with email, username, password and full name.
    Validates password complexity and unique constraint conflicts on email/username.
    """
    auth_service = AuthService(db)
    user = await auth_service.register(payload)
    return UserResponse.from_orm(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User authentication / Login",
)
async def login(
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Authenticate a user using email and password.
    Returns access and refresh token pair on success.
    Endpoints are rate limited per email to prevent brute-force attacks.
    """
    auth_service = AuthService(db)
    return await auth_service.login(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate refresh token / Session refresh",
)
async def refresh(
    payload: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """
    Exchange a valid JWT refresh token for a new set of access/refresh tokens.
    Implements single-use token rotation: using a rotated or invalid token
    revokes all sessions for safety.
    """
    auth_service = AuthService(db)
    return await auth_service.refresh(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deauthenticate / Log out",
)
async def logout(
    payload: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    """
    Log out the user by revoking the refresh token in the backend registry.
    """
    auth_service = AuthService(db)
    await auth_service.logout(payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
