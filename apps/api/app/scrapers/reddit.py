from __future__ import annotations

import asyncio
from typing import List

import structlog

from app.config import settings
from app.scrapers.base import BaseScraper

logger = structlog.get_logger()

TARGET_SUBREDDITS = [
    "functionalprint",
    "3Dprinting",
    "BambuLab",
    "FixMyPrint",
    "3dprintingdms",
]


class RedditScraper(BaseScraper):
    source_name = "reddit"

    async def scrape(self) -> List[dict]:
        signals: List[dict] = []

        loop = asyncio.get_event_loop()
        for subreddit in TARGET_SUBREDDITS:
            try:
                result = await loop.run_in_executor(
                    None, self._fetch_subreddit, subreddit
                )
                signals.extend(result)
            except Exception as e:
                logger.warning(
                    "reddit.subreddit_failed",
                    subreddit=subreddit,
                    error=str(e),
                )
            await asyncio.sleep(1)

        return signals

    def _fetch_subreddit(self, subreddit_name: str) -> List[dict]:
        import praw

        reddit_client_id = getattr(settings, "REDDIT_CLIENT_ID", "") or ""
        reddit_client_secret = getattr(settings, "REDDIT_CLIENT_SECRET", "") or ""

        reddit = praw.Reddit(
            client_id=reddit_client_id or "forge-scraper",
            client_secret=reddit_client_secret,
            user_agent="forge-trend-scraper/0.1 (by /u/forge-bot)",
        )

        signals: List[dict] = []
        subreddit = reddit.subreddit(subreddit_name)

        for post in subreddit.hot(limit=25):
            # Score = upvotes, velocity = upvote ratio * score
            score = float(post.score)
            velocity = score * float(post.upvote_ratio)

            # Extract product-relevant keywords from title
            title = post.title.lower()

            signals.append({
                "query": post.title[:200],
                "velocity": velocity,
                "volume": score,
                "geography": None,
                "raw": {
                    "source": "reddit",
                    "subreddit": subreddit_name,
                    "post_id": post.id,
                    "title": post.title,
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "url": post.url,
                    "created_utc": post.created_utc,
                },
            })

        return signals
