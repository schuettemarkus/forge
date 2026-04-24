from __future__ import annotations

import time
from typing import Dict, Optional

import structlog
from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.db import async_session
from app.config import settings

logger = structlog.get_logger()

router = APIRouter(tags=["health"])


class ServiceStatus(BaseModel):
    status: str  # ok | error
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    env: str
    checks: Dict[str, ServiceStatus]


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic liveness probe."""
    return {
        "status": "ok",
        "service": "forge-api",
        "version": "0.1.0",
    }


@router.get("/health/detailed", response_model=HealthResponse)
async def detailed_health() -> HealthResponse:
    """Readiness probe — checks Postgres, Redis, and storage."""
    checks: Dict[str, ServiceStatus] = {}

    # Postgres
    try:
        start = time.monotonic()
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        latency = (time.monotonic() - start) * 1000
        checks["postgres"] = ServiceStatus(status="ok", latency_ms=round(latency, 1))
    except Exception as e:
        checks["postgres"] = ServiceStatus(status="error", error=str(e))

    # Redis
    try:
        import redis as redis_lib
        start = time.monotonic()
        r = redis_lib.Redis.from_url(settings.REDIS_URL, socket_timeout=3)
        r.ping()
        latency = (time.monotonic() - start) * 1000
        checks["redis"] = ServiceStatus(status="ok", latency_ms=round(latency, 1))
        r.close()
    except Exception as e:
        checks["redis"] = ServiceStatus(status="error", error=str(e))

    # Storage
    try:
        from app.services.storage import storage  # noqa: F811
        checks["storage"] = ServiceStatus(status="ok", latency_ms=0)
    except Exception as e:
        checks["storage"] = ServiceStatus(status="error", error=str(e))

    all_ok = all(c.status == "ok" for c in checks.values())

    return HealthResponse(
        status="ok" if all_ok else "degraded",
        service="forge-api",
        version="0.1.0",
        env=settings.ENV,
        checks=checks,
    )
