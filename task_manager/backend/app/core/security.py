"""
Security Module.

Provides JWT token management and password hashing utilities.
Implements secure defaults: bcrypt for passwords, HS256 for JWT,
with configurable parameters via application settings.
"""

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import AuthenticationException

# ── Password Hashing ────────────────────────────────────────────────────────


class PasswordHasher:
    """
    Password hashing and verification using bcrypt natively.
    """

    @staticmethod
    def hash(password: str) -> str:
        """Hash a plaintext password using bcrypt."""
        rounds = get_settings().BCRYPT_ROUNDS
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a bcrypt hash."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False

    @staticmethod
    def needs_rehash(hashed_password: str) -> bool:
        """Check if a hash needs to be re-computed (e.g., cost factor changed)."""
        # Bcrypt hashes format is $2b$[rounds]$[hash]
        # We can inspect the rounds parameter from the prefix if needed.
        try:
            parts = hashed_password.split("$")
            if len(parts) >= 3 and parts[1] == "2b":
                current_rounds = int(parts[2])
                return current_rounds != get_settings().BCRYPT_ROUNDS
        except Exception:
            pass
        return True


# ── JWT Token Management ────────────────────────────────────────────────────


class TokenType:
    """Token type constants."""

    ACCESS = "access"
    REFRESH = "refresh"


class JWTManager:
    """
    JWT token creation and validation.

    Tokens include:
    - sub: user ID
    - exp: expiration timestamp
    - iat: issued-at timestamp
    - jti: unique token ID (for revocation)
    - type: access or refresh
    """

    def __init__(self) -> None:
        self.settings = get_settings()

    def create_access_token(self, user_id: str, extra_claims: dict[str, Any] | None = None) -> str:
        """
        Create a short-lived access token.

        Args:
            user_id: The user's UUID as string.
            extra_claims: Optional additional JWT claims.

        Returns:
            Encoded JWT string.
        """
        expires_delta = timedelta(minutes=self.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return self._create_token(
            user_id=user_id,
            token_type=TokenType.ACCESS,
            expires_delta=expires_delta,
            extra_claims=extra_claims,
        )

    def create_refresh_token(self, user_id: str) -> tuple[str, str]:
        """
        Create a long-lived refresh token.

        Returns:
            Tuple of (encoded_token, jti) where jti is the unique token ID
            used for storage and revocation.
        """
        expires_delta = timedelta(days=self.settings.REFRESH_TOKEN_EXPIRE_DAYS)
        jti = str(uuid.uuid4())
        token = self._create_token(
            user_id=user_id,
            token_type=TokenType.REFRESH,
            expires_delta=expires_delta,
            jti=jti,
        )
        return token, jti

    def decode_token(self, token: str) -> dict[str, Any]:
        """
        Decode and validate a JWT token.

        Args:
            token: The encoded JWT string.

        Returns:
            Decoded token payload.

        Raises:
            AuthenticationException: If token is invalid, expired, or malformed.
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.JWT_SECRET_KEY,
                algorithms=[self.settings.JWT_ALGORITHM],
            )
        except JWTError as e:
            raise AuthenticationException(detail=f"Invalid token: {e}") from e

        if "sub" not in payload:
            raise AuthenticationException(detail="Token missing subject claim")

        return payload

    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        """
        Decode a refresh token with type validation.

        Raises:
            AuthenticationException: If token is not a refresh token.
        """
        payload = self.decode_token(token)
        if payload.get("type") != TokenType.REFRESH:
            raise AuthenticationException(detail="Invalid token type: expected refresh token")
        return payload

    def _create_token(
        self,
        user_id: str,
        token_type: str,
        expires_delta: timedelta,
        jti: str | None = None,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """Internal token creation with all claims."""
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "sub": user_id,
            "type": token_type,
            "iat": now,
            "exp": now + expires_delta,
            "jti": jti or str(uuid.uuid4()),
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(
            payload,
            self.settings.JWT_SECRET_KEY,
            algorithm=self.settings.JWT_ALGORITHM,
        )


# ── Utility Functions ────────────────────────────────────────────────────────


def hash_token(token: str) -> str:
    """
    Create a SHA-256 hash of a token for secure storage.

    Refresh tokens are stored as hashes in the database to prevent
    exposure if the database is compromised.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
