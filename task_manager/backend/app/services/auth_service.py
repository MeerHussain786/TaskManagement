"""
Authentication Service.

Implements business operations for user registration, credentials check,
refresh token rotation (mitigating session theft), and token revocation/logout.
"""

from datetime import UTC, datetime
from typing import Any
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.cache import CacheService
from app.core.exceptions import AuthenticationException, ConflictException, RateLimitException
from app.core.logging import get_logger
from app.core.security import JWTManager, PasswordHasher, hash_token
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate

logger = get_logger(__name__)


class AuthService:
    """Business service governing registration and session flows."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)
        self.jwt_manager = JWTManager()
        self.cache = CacheService()

    async def register(self, payload: UserCreate) -> User:
        """
        Create a new user account if credentials are unique.

        Raises:
            ConflictException: If email or username is already registered.
        """
        # Enforce rate limit on register endpoints
        rate_key = f"rate:register:{payload.email}"
        allowed = await self.cache.check_rate_limit(rate_key, limit=20, window=60)
        if not allowed:
            raise RateLimitException("Registration attempts limit exceeded. Please wait a minute.")

        if await self.user_repo.exists_by_email(payload.email):
            raise ConflictException("Email is already registered")

        if await self.user_repo.exists_by_username(payload.username):
            raise ConflictException("Username is already taken")

        hashed_password = PasswordHasher.hash(payload.password)
        new_user = User(
            email=payload.email,
            username=payload.username,
            full_name=payload.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
        )

        await self.user_repo.create(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        logger.info("user_registered", user_id=new_user.id, username=new_user.username)
        return new_user

    async def login(self, payload: LoginRequest) -> TokenResponse:
        """
        Verify credentials, issue a short-lived access token and a refresh token.

        Raises:
            AuthenticationException: On invalid email or password.
        """
        # Enforce login rate limit
        rate_key = f"rate:login:{payload.email}"
        allowed = await self.cache.check_rate_limit(rate_key, limit=5, window=60)
        if not allowed:
            raise RateLimitException("Login attempts limit exceeded. Please wait a minute.")

        user = await self.user_repo.get_by_email(payload.email)
        if not user or not PasswordHasher.verify(payload.password, user.hashed_password):
            logger.warning("failed_login_attempt", email=payload.email)
            raise AuthenticationException("Invalid email or password")

        if not user.is_active:
            raise AuthenticationException("User account is deactivated")

        # Create token pair
        user_id_str = str(user.id)
        access_token = self.jwt_manager.create_access_token(user_id_str)
        refresh_token, jti = self.jwt_manager.create_refresh_token(user_id_str)

        # Hash and store refresh token
        # Parse JWT claims properly for precision:
        payload_refresh = self.jwt_manager.decode_token(refresh_token)
        exp_timestamp = payload_refresh.get("exp")
        expires_dt = datetime.fromtimestamp(exp_timestamp, UTC) if exp_timestamp else datetime.now(UTC)


        token_model = RefreshToken(

            id=uuid.UUID(jti),
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_dt,
            revoked=False,
            created_at=datetime.now(UTC),
        )

        self.db.add(token_model)
        await self.db.commit()

        logger.info("user_login_success", user_id=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.jwt_manager.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """
        Perform refresh token rotation.

        Decodes the refresh token. If it is already revoked in the database,
        this constitutes session theft. The system immediately revokes all sessions
        for the compromised user. Otherwise, rotates the refresh token.

        Raises:
            AuthenticationException: If token is expired, invalid, or revoked.
        """
        try:
            payload = self.jwt_manager.decode_refresh_token(refresh_token)
            user_id_str = payload.get("sub")
            jti_str = payload.get("jti")
            if not user_id_str or not jti_str:
                raise AuthenticationException("Malformed refresh token")
        except AuthenticationException as e:
            raise AuthenticationException("Invalid or expired refresh token") from e

        user_id = uuid.UUID(user_id_str)
        jti = uuid.UUID(jti_str)

        # Search for stored token
        query = select(RefreshToken).where(RefreshToken.id == jti)
        result = await self.db.execute(query)
        stored_token = result.scalar_one_or_none()

        # Check for reuse / theft
        if not stored_token or stored_token.revoked:
            logger.warning("potential_token_reuse_detected", user_id=user_id, token_id=jti)
            # Theft detection: Revoke all tokens for this user
            delete_query = delete(RefreshToken).where(RefreshToken.user_id == user_id)
            await self.db.execute(delete_query)
            await self.db.commit()
            raise AuthenticationException("Compromised session. Please sign in again.")

        # Revoke old token
        stored_token.revoked = True

        # Generate new token pair
        new_access_token = self.jwt_manager.create_access_token(user_id_str)
        new_refresh_token, new_jti = self.jwt_manager.create_refresh_token(user_id_str)

        payload_new = self.jwt_manager.decode_token(new_refresh_token)
        new_expires_dt = datetime.fromtimestamp(payload_new.get("exp"), UTC)

        new_token_model = RefreshToken(

            id=uuid.UUID(new_jti),
            user_id=user_id,
            token_hash=hash_token(new_refresh_token),
            expires_at=new_expires_dt,
            revoked=False,
            created_at=datetime.now(UTC),
        )


        self.db.add(new_token_model)
        await self.db.commit()

        logger.info("refresh_token_rotated", user_id=user_id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=self.jwt_manager.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(self, refresh_token: str) -> None:
        """
        Revoke the refresh token.

        Used to explicitly invalidate a session on sign out.
        """
        try:
            payload = self.jwt_manager.decode_refresh_token(refresh_token)
            jti_str = payload.get("jti")
            if jti_str:
                jti = uuid.UUID(jti_str)
                # Mark as revoked
                query = select(RefreshToken).where(RefreshToken.id == jti)
                result = await self.db.execute(query)
                stored_token = result.scalar_one_or_none()
                if stored_token:
                    stored_token.revoked = True
                    await self.db.commit()
                    logger.info("refresh_token_revoked", token_id=jti)
        except Exception as e:
            # Silence auth token failure during logout to stay idempotent
            logger.warning("logout_error_silenced", error=str(e))
