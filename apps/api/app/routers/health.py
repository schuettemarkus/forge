from __future__ import annotations

from typing import Dict

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, str]:
    return {
        "status": "ok",
        "service": "forge-api",
        "version": "0.1.0",
    }
