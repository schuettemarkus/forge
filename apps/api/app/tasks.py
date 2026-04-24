from __future__ import annotations

import asyncio
from typing import Dict

import structlog

from app.celery_app import celery
from app.db import async_session
from app.scrapers.google_trends import GoogleTrendsScraper
from app.scrapers.reddit import RedditScraper
from app.scrapers.etsy import EtsyScraper
from app.scrapers.makerworld import MakerWorldScraper
from app.scrapers.printables import PrintablesScraper
from app.scoring.scorer import OpportunityScorer

logger = structlog.get_logger()

SCRAPERS = [
    GoogleTrendsScraper(),
    RedditScraper(),
    EtsyScraper(),
    MakerWorldScraper(),
    PrintablesScraper(),
]


def _run_async(coro):
    """Helper to run async code from sync Celery tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery.task(name="forge.run_all_scrapers", bind=True, max_retries=2, time_limit=300)
def run_all_scrapers(self) -> Dict[str, int]:
    """Run all trend scrapers in parallel and return signal counts."""
    logger.info("task.scrapers.starting")

    async def _run():
        async with async_session() as db:
            async def run_one(scraper):  # type: ignore
                try:
                    count = await scraper.run(db)
                    return scraper.source_name, count
                except Exception as e:
                    logger.error("task.scraper.failed", source=scraper.source_name, error=str(e))
                    return scraper.source_name, 0

            completed = await asyncio.gather(*[run_one(s) for s in SCRAPERS])
            return {name: count for name, count in completed}

    results = _run_async(_run())
    logger.info("task.scrapers.completed", results=results)
    return results


@celery.task(name="forge.run_scorer", bind=True, max_retries=2, time_limit=600)
def run_scorer(self) -> int:
    """Run the opportunity scorer on recent trend signals."""
    logger.info("task.scorer.starting")

    async def _run():
        async with async_session() as db:
            scorer = OpportunityScorer()
            return await scorer.run(db)

    count = _run_async(_run())
    logger.info("task.scorer.completed", opportunities_created=count)
    return count


@celery.task(name="forge.scrape_and_score", time_limit=900)
def scrape_and_score() -> Dict[str, object]:
    """Full pipeline: run all scrapers then score. This is the daily cron task."""
    scraper_results = run_all_scrapers()
    score_count = run_scorer()
    return {
        "scrapers": scraper_results,
        "opportunities_created": score_count,
    }


# Celery Beat schedule — run daily at 6am UTC
celery.conf.beat_schedule = {
    "daily-scrape-and-score": {
        "task": "forge.scrape_and_score",
        "schedule": 86400.0,
    },
}
