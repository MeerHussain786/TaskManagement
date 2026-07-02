"""
Unit Tests for Security Utilities.
"""

import time
import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.exceptions import AuthenticationException
from app.core.security import JWTManager, PasswordHasher, hash_token


def test_password_hashing():
    """Verify password hashing and verification workflows."""
    password = "MyComplexPassword1!"
    hashed = PasswordHasher.hash(password)

    assert hashed != password
    assert PasswordHasher.verify(password, hashed) is True
    assert PasswordHasher.verify("wrongpassword", hashed) is False


def test_password_needs_rehash():
    """Verify check for password rehash requirements."""
    password = "MyComplexPassword1!"
    hashed = PasswordHasher.hash(password)
    # Since cost factor rounds are same, shouldn't need rehash
    assert PasswordHasher.needs_rehash(hashed) is False


def test_jwt_token_creation_and_validation():
    """Verify JWT access token serialization, expiration, and decoding."""
    jwt_manager = JWTManager()
    user_id = "123e4567-e89b-12d3-a456-426614174000"

    token = jwt_manager.create_access_token(user_id)
    assert isinstance(token, str)

    payload = jwt_manager.decode_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "jti" in payload


def test_jwt_token_expiration():
    """Verify expired token validation fails."""
    jwt_manager = JWTManager()
    settings = get_settings()
    
    # Temporarily set token expiry to -1 minute
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = -1
    
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    token = jwt_manager.create_access_token(user_id)

    with pytest.raises(AuthenticationException) as exc_info:
        jwt_manager.decode_token(token)
    
    assert "Signature has expired" in str(exc_info.value.detail)
    
    # Restore settings
    settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30


def test_refresh_token_rotation_payloads():
    """Verify JWT refresh token structure and rotation helpers."""
    jwt_manager = JWTManager()
    user_id = "123e4567-e89b-12d3-a456-426614174000"

    token, jti = jwt_manager.create_refresh_token(user_id)
    assert isinstance(token, str)
    assert isinstance(jti, str)

    payload = jwt_manager.decode_refresh_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti


def test_token_hash_helper():
    """Verify token hash utility uses SHA-256."""
    token = "my-secret-jwt-token"
    hashed = hash_token(token)
    
    assert len(hashed) == 64  # SHA-256 is 64 hex chars
    assert hashed == hash_token(token)
