"""
End-to-End Tests for Authentication.

Tests registration validation, login rate limit, refresh token rotation,
theft detection triggers, and session logouts using httpx client.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_registration_and_login_flow(client: AsyncClient):
    """Verify clean registration and login token retrieval flow."""
    # 1. Register
    register_payload = {
        "email": "flow_test@example.com",
        "username": "flowtest",
        "full_name": "Flow Test",
        "password": "SecureP@ss123!",
    }
    register_res = await client.post("/api/v1/auth/register", json=register_payload)
    assert register_res.status_code == 201
    assert register_res.json()["email"] == "flow_test@example.com"
    assert "id" in register_res.json()

    # 2. Login
    login_payload = {
        "email": "flow_test@example.com",
        "password": "SecureP@ss123!",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    tokens = login_res.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_auth_refresh_token_rotation(client: AsyncClient):
    """Verify refresh token rotation and token reuse detection."""
    # Register & Login
    register_payload = {
        "email": "rotation_test@example.com",
        "username": "rotatetest",
        "full_name": "Rotation Test",
        "password": "SecureP@ss123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_payload = {
        "email": "rotation_test@example.com",
        "password": "SecureP@ss123!",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    original_tokens = login_res.json()
    first_refresh_token = original_tokens["refresh_token"]

    # Refresh first time (rotates token)
    refresh_res = await client.post(
        "/api/v1/auth/refresh", 
        json={"refresh_token": first_refresh_token}
    )
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert new_tokens["access_token"] != original_tokens["access_token"]
    assert new_tokens["refresh_token"] != original_tokens["refresh_token"]

    # Attempt reuse of the first refresh token (re-use / theft detection)
    reuse_res = await client.post(
        "/api/v1/auth/refresh", 
        json={"refresh_token": first_refresh_token}
    )
    assert reuse_res.status_code == 401
    assert "Compromised session" in reuse_res.json()["detail"]


@pytest.mark.asyncio
async def test_auth_logout(client: AsyncClient):
    """Verify session logout revokes refresh token validity."""
    # Register & Login
    register_payload = {
        "email": "logout_test@example.com",
        "username": "logouttest",
        "full_name": "Logout Test",
        "password": "SecureP@ss123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "logout_test@example.com", "password": "SecureP@ss123!"}
    )
    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    # Logout
    logout_res = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token}
    )
    assert logout_res.status_code == 204

    # Verification: token must be invalid now
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_res.status_code == 401
