from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trend import TrendSignal
from app.services.storage import storage

logger = structlog.get_logger()


class BaseScraper(ABC):
    """Base class for all trend scrapers. Each scraper is isolated and fails closed."""

    source_name: str = "unknown"

    @abstractmethod
    async def scrape(self) -> List[dict]:
        """Run the scraper and return a list of raw signal dicts.

        Each dict should have:
            query: str — the search term or topic
            velocity: float — rate of change / trending score
            volume: float — absolute volume / popularity
            geography: Optional[str] — region if available
            raw: dict — the raw payload for archival
        """
        ...

    async def run(self, db: AsyncSession) -> int:
        """Execute scraper, store raw data to R2, persist signals to DB."""
        logger.info("scraper.starting", source=self.source_name)
        try:
            signals = await self.scrape()
        except Exception as e:
            logger.error("scraper.failed", source=self.source_name, error=str(e))
            return 0

        count = 0
        now = datetime.now(timezone.utc)

        for signal in signals:
            try:
                # Archive raw payload to storage
                raw_key = f"raw/{self.source_name}/{now.strftime('%Y/%m/%d')}/{uuid4().hex}.json"
                raw_bytes = json.dumps(signal.get("raw", {}), default=str).encode()
                try:
                    await storage.upload_file_async(raw_key, raw_bytes, "application/json")
                except Exception:
                    raw_key = None
                    logger.warning("scraper.storage_failed", source=self.source_name)

                trend = TrendSignal(
                    source=self.source_name,
                    query=signal["query"],
                    velocity=signal.get("velocity", 0.0),
                    volume=signal.get("volume", 0.0),
                    geography=signal.get("geography"),
                    captured_at=now,
                    raw_s3_key=raw_key,
                )
                db.add(trend)
                count += 1
            except Exception as e:
                logger.warning(
                    "scraper.signal_failed",
                    source=self.source_name,
                    error=str(e),
                    query=signal.get("query", "unknown"),
                )

        if count > 0:
            await db.commit()

        logger.info("scraper.completed", source=self.source_name, signals=count)
        return count
