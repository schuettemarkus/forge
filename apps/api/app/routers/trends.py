from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_owner
from app.db import get_db
from app.models.trend import TrendSignal

router = APIRouter()


class TrendSignalOut(BaseModel):
    id: uuid.UUID
    source: str
    query: str
    velocity: float
    volume: float
    geography: Optional[str]
    captured_at: datetime

    model_config = {"from_attributes": True}


class TrendSummary(BaseModel):
    total_signals: int
    by_source: Dict[str, int]
    latest_capture: Optional[datetime]


@router.get("/", response_model=List[TrendSignalOut])
async def list_trends(
    source: Optional[str] = Query(None, max_length=50),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
) -> List[TrendSignalOut]:
    query = select(TrendSignal).where(TrendSignal.deleted_at.is_(None))
    if source:
        query = query.where(TrendSignal.source == source)
    query = query.order_by(TrendSignal.velocity.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return [TrendSignalOut.model_validate(r) for r in result.scalars().all()]


@router.get("/summary", response_model=TrendSummary)
async def trend_summary(
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
) -> TrendSummary:
    total_result = await db.execute(
        select(func.count(TrendSignal.id)).where(TrendSignal.deleted_at.is_(None))
    )
    total = total_result.scalar() or 0

    source_result = await db.execute(
        select(TrendSignal.source, func.count(TrendSignal.id))
        .where(TrendSignal.deleted_at.is_(None))
        .group_by(TrendSignal.source)
    )
    by_source = {row[0]: row[1] for row in source_result.all()}

    latest_result = await db.execute(
        select(func.max(TrendSignal.captured_at))
    )
    latest = latest_result.scalar()

    return TrendSummary(
        total_signals=total,
        by_source=by_source,
        latest_capture=latest,
    )


@router.post("/scrape")
async def trigger_scrape(
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_owner),
) -> Dict[str, object]:
    """Manually trigger all scrapers in parallel. Requires owner role."""
    import asyncio
    from app.scrapers.google_trends import GoogleTrendsScraper
    from app.scrapers.reddit import RedditScraper
    from app.scrapers.etsy import EtsyScraper
    from app.scrapers.makerworld import MakerWorldScraper
    from app.scrapers.printables import PrintablesScraper

    scrapers = [
        GoogleTrendsScraper(),
        MakerWorldScraper(),
        PrintablesScraper(),
        EtsyScraper(),
        RedditScraper(),
    ]

    async def run_scraper(scraper):  # type: ignore
        try:
            return scraper.source_name, await scraper.run(db)
        except Exception:
            return scraper.source_name, 0

    completed = await asyncio.gather(*[run_scraper(s) for s in scrapers])
    results = {name: count for name, count in completed}

    return {"status": "completed", "signals": results}
