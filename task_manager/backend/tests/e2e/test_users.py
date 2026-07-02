"""
End-to-End Tests for User Profile management.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_profile_endpoints(client: AsyncClient, auth_headers: dict[str, str]):
    """Verify profile querying and updates with conflict checks."""
    # ── 1. Read profile ──────────────────────────────────────────────────────
    profile_res = await client.get("/api/v1/users/me", headers=auth_headers)
    assert profile_res.status_code == 200
    profile = profile_res.json()
    assert profile["email"] == "testuser@example.com"
    assert profile["username"] == "testuser"
    assert profile["is_active"] is True

    # ── 2. Update profile ────────────────────────────────────────────────────
    update_payload = {"full_name": "Updated Test User Name"}
    update_res = await client.put("/api/v1/users/me", json=update_payload, headers=auth_headers)
    assert update_res.status_code == 200
    assert update_res.json()["full_name"] == "Updated Test User Name"

    # Verify updates persisted
    profile_res_recheck = await client.get("/api/v1/users/me", headers=auth_headers)
    assert profile_res_recheck.json()["full_name"] == "Updated Test User Name"

    # ── 3. Attempt update with conflicting email ─────────────────────────────
    # Create another user first
    register_payload_other = {
        "email": "existing_email@example.com",
        "username": "existinguser",
        "full_name": "Existing User",
        "password": "SecureP@ss123!",
    }
    await client.post("/api/v1/auth/register", json=register_payload_other)

    # Try updating current user email to the other user's email
    conflict_res = await client.put(
        "/api/v1/users/me", 
        json={"email": "existing_email@example.com"}, 
        headers=auth_headers
    )
    assert conflict_res.status_code == 409
    assert "email" in conflict_res.json()["detail"].lower()
