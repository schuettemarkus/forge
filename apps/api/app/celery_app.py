from __future__ import annotations

from typing import Dict

from celery import Celery

from app.config import settings

celery = Celery(
    "forge",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@celery.task(name="forge.health_check")
def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "forge-worker"}
