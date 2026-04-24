from __future__ import annotations

import asyncio
from typing import List

import httpx
import structlog

from app.scrapers.base import BaseScraper

logger = structlog.get_logger()

# MakerWorld has a public API for browsing models
MAKERWORLD_API = "https://makerworld.com/api/v1/design"

CATEGORIES: List[str] = [
    "home",
    "office",
    "garden",
    "kitchen",
    "toys",
    "tools",
    "organization",
]


class MakerWorldScraper(BaseScraper):
    source_name = "makerworld"

    async def scrape(self) -> List[dict]:
        signals: List[dict] = []

        async with httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Forge/0.1 (trend-research; contact@forgeprints.com)",
                "Accept": "application/json",
            },
        ) as client:
            # Fetch trending/popular models
            for sort_by in ["trending", "popular", "newest"]:
                try:
                    result = await self._fetch_models(client, sort_by)
                    signals.extend(result)
                except Exception as e:
                    logger.warning(
                        "makerworld.fetch_failed",
                        sort_by=sort_by,
                        error=str(e),
                    )
                await asyncio.sleep(2)  # Polite rate limiting

        return signals

    async def _fetch_models(
        self, client: httpx.AsyncClient, sort_by: str
    ) -> List[dict]:
        try:
            resp = await client.get(
                MAKERWORLD_API,
                params={
                    "sort": sort_by,
                    "limit": 30,
                },
            )

            if resp.status_code == 403 or resp.status_code == 429:
                logger.warning(
                    "makerworld.rate_limited",
                    status=resp.status_code,
                    sort_by=sort_by,
                )
                return []

            if resp.status_code != 200:
                logger.warning(
                    "makerworld.unexpected_status",
                    status=resp.status_code,
                    sort_by=sort_by,
                )
                return []

            data = resp.json()
        except Exception as e:
            logger.warning("makerworld.parse_failed", error=str(e))
            return []

        models = data if isinstance(data, list) else data.get("hits", data.get("results", []))
        signals: List[dict] = []

        for model in models:
            if not isinstance(model, dict):
                continue

            title = model.get("title", model.get("name", ""))
            if not title:
                continue

            downloads = float(model.get("downloadCount", model.get("downloads", 0)))
            likes = float(model.get("likeCount", model.get("likes", 0)))
            views = float(model.get("viewCount", model.get("views", 0)))

            # Velocity: engagement rate (likes + downloads relative to views)
            velocity = (likes + downloads) / max(views, 1) * 100

            signals.append({
                "query": title[:200],
                "velocity": velocity,
                "volume": downloads + likes,
                "geography": None,
                "raw": {
                    "source": "makerworld",
                    "sort": sort_by,
                    "model_id": model.get("id", model.get("designId", "")),
                    "title": title,
                    "downloads": downloads,
                    "likes": likes,
                    "views": views,
                    "license": model.get("license", ""),
                    "category": model.get("category", ""),
                },
            })

        return signals
