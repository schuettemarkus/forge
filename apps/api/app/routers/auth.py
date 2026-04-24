from __future__ import annotations

import secrets
from typing import Dict

from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, HTTPException, status

from app.auth import (
    create_access_token,
    create_refresh_token,
    verify_token,
    hash_password,
    verify_password,
)
from app.config import settings

router = APIRouter()

# In-memory magic link store (replace with Redis in production)
_pending_magic_links: Dict[str, str] = {}


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    message: str


class VerifyRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(request: MagicLinkRequest) -> MagicLinkResponse:
    """Generate a magic link token for passwordless login.

    In development, the token is returned in the response for convenience.
    In production, it would be emailed via Resend.
    """
    # Only allow the configured operator email
    if settings.OPERATOR_EMAIL and request.email != settings.OPERATOR_EMAIL:
        # Don't reveal whether the email exists
        return MagicLinkResponse(message="If that email is registered, a magic link has been sent.")

    token = secrets.token_urlsafe(32)
    _pending_magic_links[token] = request.email

    # In dev mode, include the token in the response
    if settings.ENV == "development":
        return MagicLinkResponse(
            message=f"Dev mode — use this token to verify: {token}"
        )

    # TODO: Send email via Resend in production
    return MagicLinkResponse(message="If that email is registered, a magic link has been sent.")


@router.post("/verify", response_model=TokenResponse)
async def verify_magic_link(request: VerifyRequest) -> TokenResponse:
    """Exchange a magic link token for access + refresh JWT tokens."""
    email = _pending_magic_links.pop(request.token, None)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired magic link",
        )

    access_token = create_access_token({"sub": email, "role": "owner"})
    refresh_token = create_refresh_token({"sub": email, "role": "owner"})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(request: RefreshRequest) -> TokenResponse:
    """Exchange a refresh token for a new access + refresh token pair."""
    payload = verify_token(request.refresh_token, expected_type="refresh")

    access_token = create_access_token({
        "sub": payload["sub"],
        "role": payload.get("role", "owner"),
    })
    refresh_token = create_refresh_token({
        "sub": payload["sub"],
        "role": payload.get("role", "owner"),
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
