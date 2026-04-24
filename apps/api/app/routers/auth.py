from __future__ import annotations

from pydantic import BaseModel, EmailStr
from fastapi import APIRouter

router = APIRouter()


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    message: str


class VerifyRequest(BaseModel):
    token: str


class VerifyResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/magic-link", response_model=MagicLinkResponse)
async def request_magic_link(request: MagicLinkRequest) -> MagicLinkResponse:
    # TODO: M0 — send actual magic link via Resend
    return MagicLinkResponse(message=f"Magic link sent to {request.email}")


@router.post("/verify", response_model=VerifyResponse)
async def verify_token(request: VerifyRequest) -> VerifyResponse:
    # TODO: M0 — verify actual JWT token
    return VerifyResponse(access_token="stub-token", token_type="bearer")
