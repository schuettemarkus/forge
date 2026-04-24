from __future__ import annotations

import asyncio
from typing import List

import httpx
import structlog

from app.scrapers.base import BaseScraper

logger = structlog.get_logger()

# Printables has a GraphQL API
PRINTABLES_API = "https://api.printables.com/graphql/"


class PrintablesScraper(BaseScraper):
    source_name = "printables"

    async def scrape(self) -> List[dict]:
        signals: List[dict] = []

        async with httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Forge/0.1 (trend-research; contact@forgeprints.com)",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        ) as client:
            for ordering in ["trending", "popular", "newest"]:
                try:
                    result = await self._fetch_models(client, ordering)
                    signals.extend(result)
                except Exception as e:
                    logger.warning(
                        "printables.fetch_failed",
                        ordering=ordering,
                        error=str(e),
                    )
                await asyncio.sleep(2)

        return signals

    async def _fetch_models(
        self, client: httpx.AsyncClient, ordering: str
    ) -> List[dict]:
        # Printables GraphQL query for trending prints
        query = """
        query PrintList($limit: Int!, $ordering: String) {
            printList(limit: $limit, ordering: $ordering) {
                items {
                    id
                    name
                    slug
                    likesCount
                    makesCount
                    downloadCount
                    displayCount
                    datePublished
                    category {
                        name
                    }
                    license {
                        name
                        abbreviation
                    }
                }
            }
        }
        """

        order_map = {
            "trending": "-hot",
            "popular": "-likes_count",
            "newest": "-first_publish",
        }

        try:
            resp = await client.post(
                PRINTABLES_API,
                json={
                    "query": query,
                    "variables": {
                        "limit": 30,
                        "ordering": order_map.get(ordering, "-hot"),
                    },
                },
            )

            if resp.status_code != 200:
                logger.warning(
                    "printables.bad_status",
                    status=resp.status_code,
                    ordering=ordering,
                )
                return []

            data = resp.json()
        except Exception as e:
            logger.warning("printables.request_failed", error=str(e))
            return []

        items = (
            data.get("data", {})
            .get("printList", {})
            .get("items", [])
        )

        signals: List[dict] = []
        for item in items:
            if not isinstance(item, dict):
                continue

            name = item.get("name", "")
            if not name:
                continue

            downloads = float(item.get("downloadCount", 0))
            likes = float(item.get("likesCount", 0))
            makes = float(item.get("makesCount", 0))
            views = float(item.get("displayCount", 0))

            # Makes are a strong signal — someone printed it
            velocity = (makes * 3 + likes + downloads) / max(views, 1) * 100

            license_info = item.get("license", {}) or {}
            category_info = item.get("category", {}) or {}

            signals.append({
                "query": name[:200],
                "velocity": velocity,
                "volume": downloads + makes,
                "geography": None,
                "raw": {
                    "source": "printables",
                    "ordering": ordering,
                    "model_id": item.get("id", ""),
                    "name": name,
                    "slug": item.get("slug", ""),
                    "downloads": downloads,
                    "likes": likes,
                    "makes": makes,
                    "views": views,
                    "license": license_info.get("abbreviation", ""),
                    "category": category_info.get("name", ""),
                    "date_published": item.get("datePublished", ""),
                },
            })

        return signals
