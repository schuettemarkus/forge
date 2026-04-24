from __future__ import annotations

import asyncio
from typing import Dict, List, Optional

import httpx
import structlog

from app.config import settings
from app.scrapers.base import BaseScraper

logger = structlog.get_logger()

# Product categories to search on Etsy
ETSY_SEARCH_QUERIES: List[str] = [
    "3d printed desk organizer",
    "3d printed planter",
    "3d printed phone stand",
    "3d printed wall hook",
    "3d printed cookie cutter",
    "3d printed gridfinity",
    "3d printed headphone stand",
    "3d printed cable management",
    "3d printed shelf bracket",
    "3d printed pen holder",
    "3d printed coaster",
    "3d printed vase",
    "3d printed bookend",
    "3d printed drawer organizer",
    "3d printed soap dish",
    "3d printed key holder",
    "3d printed laptop stand",
    "3d printed napkin holder",
    "3d printed light switch cover",
    "3d printed garden marker",
]

ETSY_API_BASE = "https://openapi.etsy.com/v3"


class EtsyScraper(BaseScraper):
    source_name = "etsy"

    async def scrape(self) -> List[dict]:
        if not settings.ETSY_API_KEY:
            logger.warning("etsy.no_api_key", msg="Etsy API key not configured, skipping")
            return []

        signals: List[dict] = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for query in ETSY_SEARCH_QUERIES:
                try:
                    result = await self._search_listings(client, query)
                    if result:
                        signals.append(result)
                except Exception as e:
                    logger.warning(
                        "etsy.search_failed",
                        query=query,
                        error=str(e),
                    )
                await asyncio.sleep(0.5)  # Rate limit: ~2 req/s

        return signals

    async def _search_listings(
        self, client: httpx.AsyncClient, query: str
    ) -> Optional[dict]:
        headers = {"x-api-key": settings.ETSY_API_KEY}

        resp = await client.get(
            f"{ETSY_API_BASE}/application/listings/active",
            headers=headers,
            params={
                "keywords": query,
                "limit": 25,
                "sort_on": "score",
            },
        )
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            return None

        # Compute supply/demand proxies
        listing_count = data.get("count", 0)
        prices = [
            r["price"]["amount"] / r["price"]["divisor"]
            for r in results
            if "price" in r
        ]
        review_counts = [r.get("num_favorers", 0) for r in results]

        avg_price = sum(prices) / len(prices) if prices else 0
        median_price = sorted(prices)[len(prices) // 2] if prices else 0
        avg_favorites = sum(review_counts) / len(review_counts) if review_counts else 0

        # High demand + low supply = opportunity
        # Velocity proxy: favorites per listing (engagement density)
        velocity = avg_favorites / max(listing_count, 1) * 1000

        return {
            "query": query.replace("3d printed ", ""),
            "velocity": velocity,
            "volume": float(listing_count),
            "geography": "US",
            "raw": {
                "source": "etsy",
                "search_query": query,
                "listing_count": listing_count,
                "avg_price": round(avg_price, 2),
                "median_price": round(median_price, 2),
                "avg_favorites": round(avg_favorites, 1),
                "sample_listings": [
                    {
                        "listing_id": r.get("listing_id"),
                        "title": r.get("title", "")[:100],
                        "price": r["price"]["amount"] / r["price"]["divisor"]
                        if "price" in r else 0,
                        "favorites": r.get("num_favorers", 0),
                        "views": r.get("views", 0),
                    }
                    for r in results[:10]
                ],
            },
        }
