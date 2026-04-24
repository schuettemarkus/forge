from __future__ import annotations

import asyncio
from typing import List

import structlog
from pytrends.request import TrendReq

from app.scrapers.base import BaseScraper

logger = structlog.get_logger()

# Seed queries for 3D-printable product categories
SEED_QUERIES: List[str] = [
    "desk organizer",
    "cable management",
    "planter pot",
    "phone stand",
    "wall hook",
    "shelf bracket",
    "cookie cutter custom",
    "gridfinity",
    "pen holder",
    "soap dish",
    "toothbrush holder",
    "key holder wall",
    "headphone stand",
    "laptop stand",
    "coaster set",
    "napkin holder",
    "bookend",
    "drawer organizer",
    "spice rack",
    "vase modern",
]


class GoogleTrendsScraper(BaseScraper):
    source_name = "google_trends"

    async def scrape(self) -> List[dict]:
        signals: List[dict] = []

        # pytrends is synchronous, run in executor
        loop = asyncio.get_event_loop()

        for i in range(0, len(SEED_QUERIES), 5):
            batch = SEED_QUERIES[i : i + 5]
            try:
                result = await loop.run_in_executor(None, self._fetch_batch, batch)
                signals.extend(result)
            except Exception as e:
                logger.warning(
                    "google_trends.batch_failed",
                    batch=batch,
                    error=str(e),
                )
            # Polite delay between batches
            await asyncio.sleep(2)

        # Also fetch related rising queries for top seeds
        for query in SEED_QUERIES[:5]:
            try:
                related = await loop.run_in_executor(
                    None, self._fetch_related, query
                )
                signals.extend(related)
            except Exception as e:
                logger.warning(
                    "google_trends.related_failed",
                    query=query,
                    error=str(e),
                )
            await asyncio.sleep(1)

        return signals

    def _fetch_batch(self, queries: List[str]) -> List[dict]:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload(queries, timeframe="now 7-d", geo="US")
        interest = pytrends.interest_over_time()

        signals: List[dict] = []
        if interest.empty:
            return signals

        for query in queries:
            if query not in interest.columns:
                continue
            series = interest[query]
            avg_volume = float(series.mean())
            # Velocity = difference between last day avg and first day avg
            half = len(series) // 2
            first_half = float(series.iloc[:half].mean()) if half > 0 else 0
            second_half = float(series.iloc[half:].mean()) if half > 0 else 0
            velocity = second_half - first_half

            signals.append({
                "query": query,
                "velocity": velocity,
                "volume": avg_volume,
                "geography": "US",
                "raw": {
                    "source": "google_trends",
                    "timeframe": "now 7-d",
                    "values": series.tolist(),
                },
            })

        return signals

    def _fetch_related(self, query: str) -> List[dict]:
        pytrends = TrendReq(hl="en-US", tz=360)
        pytrends.build_payload([query], timeframe="now 7-d", geo="US")
        related = pytrends.related_queries()

        signals: List[dict] = []
        if query not in related:
            return signals

        rising = related[query].get("rising")
        if rising is not None and not rising.empty:
            for _, row in rising.head(5).iterrows():
                signals.append({
                    "query": str(row["query"]),
                    "velocity": float(row["value"]) if row["value"] != "Breakout" else 100.0,
                    "volume": 0.0,
                    "geography": "US",
                    "raw": {
                        "source": "google_trends_related",
                        "parent_query": query,
                        "type": "rising",
                    },
                })

        return signals
