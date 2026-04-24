from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password,
)


def test_create_and_verify_access_token() -> None:
    token = create_access_token({"sub": "test@forge.local", "role": "owner"})
    payload = verify_token(token)
    assert payload["sub"] == "test@forge.local"
    assert payload["role"] == "owner"
    assert payload["type"] == "access"


def test_create_and_verify_refresh_token() -> None:
    token = create_refresh_token({"sub": "test@forge.local", "role": "owner"})
    payload = verify_token(token, expected_type="refresh")
    assert payload["sub"] == "test@forge.local"
    assert payload["type"] == "refresh"


def test_verify_wrong_token_type_fails() -> None:
    from fastapi import HTTPException

    token = create_access_token({"sub": "test@forge.local"})
    with pytest.raises(HTTPException) as exc_info:
        verify_token(token, expected_type="refresh")
    assert exc_info.value.status_code == 401


def test_verify_invalid_token_fails() -> None:
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        verify_token("invalid-garbage-token")
    assert exc_info.value.status_code == 401


def test_password_hashing() -> None:
    # Use a short password to avoid bcrypt 72-byte limit issues
    hashed = hash_password("secret")
    assert verify_password("secret", hashed)
    assert not verify_password("wrong", hashed)


@pytest.mark.asyncio
async def test_magic_link_flow(client: AsyncClient) -> None:
    # Request magic link
    resp = await client.post("/auth/magic-link", json={"email": "dev@example.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data["message"] or "magic link" in data["message"].lower()

    # In dev mode the token is in the response
    if "token" in data["message"]:
        # Extract token from "Dev mode — use this token to verify: <token>"
        token = data["message"].split(": ")[-1]

        # Verify the magic link
        resp = await client.post("/auth/verify", json={"token": token})
        assert resp.status_code == 200
        tokens = resp.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert tokens["token_type"] == "bearer"

        # Refresh
        resp = await client.post(
            "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )
        assert resp.status_code == 200
        new_tokens = resp.json()
        assert "access_token" in new_tokens


@pytest.mark.asyncio
async def test_magic_link_invalid_token(client: AsyncClient) -> None:
    resp = await client.post("/auth/verify", json={"token": "bogus-token"})
    assert resp.status_code == 401
