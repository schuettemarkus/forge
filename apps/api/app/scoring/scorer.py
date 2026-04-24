from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

import structlog
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.opportunity import Opportunity
from app.models.trend import TrendSignal

logger = structlog.get_logger()

# Blocklists — kept in-module to avoid sys.path manipulation.
# Canonical source: packages/shared/constants.py
IP_BLOCKLIST = [
    "disney", "marvel", "dc comics", "batman", "superman", "spider-man",
    "pokemon", "pikachu", "nintendo", "mario", "zelda", "kirby",
    "star wars", "lucasfilm", "mandalorian", "baby yoda", "grogu",
    "harry potter", "hogwarts", "wizarding world",
    "hello kitty", "sanrio", "pusheen",
    "lego", "barbie", "hot wheels", "transformers", "gi joe",
    "my little pony", "care bears", "sesame street",
    "mickey mouse", "frozen", "elsa", "moana", "pixar",
    "nfl", "nba", "mlb", "nhl", "fifa", "mls",
    "coca-cola", "pepsi", "nike", "adidas", "supreme",
    "louis vuitton", "gucci", "chanel", "hermes",
    "apple", "google", "tesla", "ferrari", "lamborghini",
    "fortnite", "minecraft", "roblox", "among us",
    "one piece", "naruto", "dragon ball",
    "spongebob", "paw patrol", "peppa pig",
]
EXCLUDED_CATEGORIES = [
    "firearms", "weapons", "gun accessories", "ammunition",
    "religious", "political", "adult", "drug paraphernalia",
    "tobacco", "vaping", "knives", "brass knuckles",
]
MARGIN_FLOOR_PCT = 40


class OpportunityScorer:
    """Turns raw trend signals into ranked, actionable product opportunities."""

    async def run(self, db: AsyncSession) -> int:
        """Score all unprocessed trend signals and create/update opportunities."""
        logger.info("scorer.starting")

        # 1. Cluster signals into product concepts
        concepts = await self._cluster_signals(db)
        logger.info("scorer.clustered", concept_count=len(concepts))

        # 2. Score each concept
        created = 0
        for concept_name, signals in concepts.items():
            # IP & category filter
            if self._is_blocked(concept_name):
                logger.info("scorer.blocked", concept=concept_name)
                continue

            # Check if we already have this opportunity
            existing = await db.execute(
                select(Opportunity).where(
                    Opportunity.concept == concept_name,
                    Opportunity.deleted_at.is_(None),
                )
            )
            if existing.scalar_one_or_none():
                continue

            scores = self._compute_scores(concept_name, signals)

            # Reject low-margin opportunities
            if scores["margin_est"] < MARGIN_FLOOR_PCT:
                continue

            # Create opportunity with composite score
            composite = (
                scores["demand"]
                * scores["margin_est"] / 100
                * (1 / max(scores["competition"], 0.1))
                * scores["printability"]
                * scores["ip_safe"]
            )

            rationale = self._build_rationale(concept_name, signals, scores)

            opp = Opportunity(
                concept=concept_name,
                score=round(composite, 2),
                demand=scores["demand"],
                competition=scores["competition"],
                printability=scores["printability"],
                margin_est=scores["margin_est"],
                rationale_md=rationale,
                ip_status="clear" if scores["ip_safe"] == 1.0 else "flagged",
                status="pending",
            )
            db.add(opp)
            created += 1

        if created > 0:
            await db.commit()

        logger.info("scorer.completed", opportunities_created=created)
        return created

    async def _cluster_signals(
        self, db: AsyncSession
    ) -> Dict[str, List[dict]]:
        """Group trend signals by normalized concept name.

        Simple approach for v1: normalize query text, group exact matches.
        TODO: Use embeddings + pgvector for semantic clustering in v2.
        """
        # Get recent signals (last 7 days)
        result = await db.execute(
            select(TrendSignal)
            .where(
                TrendSignal.captured_at >= func.now() - text("interval '7 days'"),
                TrendSignal.deleted_at.is_(None),
            )
            .order_by(TrendSignal.velocity.desc())
        )
        signals = result.scalars().all()

        concepts: Dict[str, List[dict]] = {}
        for signal in signals:
            # Normalize: lowercase, strip common prefixes, collapse whitespace
            name = self._normalize_concept(signal.query)
            if not name or len(name) < 3:
                continue

            if name not in concepts:
                concepts[name] = []

            concepts[name].append({
                "source": signal.source,
                "query": signal.query,
                "velocity": signal.velocity,
                "volume": signal.volume,
                "geography": signal.geography,
            })

        return concepts

    def _normalize_concept(self, query: str) -> str:
        """Normalize a search query into a product concept name."""
        name = query.lower().strip()
        # Remove common prefixes
        for prefix in ["3d printed ", "3d print ", "custom ", "diy "]:
            if name.startswith(prefix):
                name = name[len(prefix):]
        # Remove special chars, collapse whitespace
        name = re.sub(r"[^\w\s-]", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        # Cap length
        return name[:100]

    def _is_blocked(self, concept: str) -> bool:
        """Check if concept hits IP blocklist or excluded categories."""
        lower = concept.lower()
        for blocked in IP_BLOCKLIST:
            if blocked in lower:
                return True
        for excluded in EXCLUDED_CATEGORIES:
            if excluded in lower:
                return True
        return False

    def _compute_scores(
        self, concept: str, signals: List[dict]
    ) -> Dict[str, float]:
        """Compute individual scoring dimensions for a concept."""
        # Demand: weighted average of velocity across sources
        total_velocity = sum(s["velocity"] for s in signals)
        total_volume = sum(s["volume"] for s in signals)
        source_count = len(set(s["source"] for s in signals))

        # More sources = stronger signal (cross-platform validation)
        demand = (total_velocity * 0.6 + total_volume * 0.2 + source_count * 20) / max(
            len(signals), 1
        )
        demand = min(demand, 100)  # Cap at 100

        # Competition: estimate from Etsy signals if available
        etsy_signals = [s for s in signals if s["source"] == "etsy"]
        if etsy_signals:
            # Higher volume on Etsy = more competition
            competition = min(etsy_signals[0]["volume"] / 1000, 10)
        else:
            competition = 5.0  # Default medium competition

        # Printability: heuristic based on concept keywords
        printability = self._estimate_printability(concept)

        # Margin estimate: rough based on category
        margin_est = self._estimate_margin(concept)

        # IP safety: 1.0 if clear, 0.0 if blocked (already filtered above)
        ip_safe = 1.0

        return {
            "demand": round(demand, 2),
            "competition": round(competition, 2),
            "printability": round(printability, 2),
            "margin_est": round(margin_est, 2),
            "ip_safe": ip_safe,
        }

    def _estimate_printability(self, concept: str) -> float:
        """Heuristic printability score 0-1 based on concept keywords."""
        lower = concept.lower()

        # High printability: simple geometric shapes
        high_print = [
            "organizer", "holder", "stand", "hook", "bracket", "tray",
            "box", "bin", "cup", "vase", "planter", "coaster",
            "gridfinity", "shelf", "mount", "clip", "cover",
        ]
        # Medium: some complexity
        medium_print = [
            "cookie cutter", "bookend", "lamp", "sign", "frame",
            "dispenser", "rack", "marker",
        ]
        # Low: complex / multi-part
        low_print = [
            "articulated", "mechanical", "gear", "hinge", "spring",
            "figure", "statue", "bust", "miniature",
        ]

        for kw in high_print:
            if kw in lower:
                return 0.9
        for kw in medium_print:
            if kw in lower:
                return 0.7
        for kw in low_print:
            if kw in lower:
                return 0.4
        return 0.6  # Default moderate

    def _estimate_margin(self, concept: str) -> float:
        """Rough margin estimate as percentage. Returns the estimated margin."""
        lower = concept.lower()

        # High margin items (small, fast print, high perceived value)
        high_margin = [
            "cookie cutter", "coaster", "hook", "clip", "cover",
            "switch", "cap", "ring", "tag", "marker",
        ]
        # Medium margin
        medium_margin = [
            "organizer", "holder", "stand", "bracket", "mount",
            "tray", "cup", "gridfinity",
        ]
        # Lower margin (large, long print time)
        low_margin = [
            "vase", "planter", "lamp", "shelf", "bookend",
            "bust", "statue", "figure",
        ]

        for kw in high_margin:
            if kw in lower:
                return 65.0
        for kw in medium_margin:
            if kw in lower:
                return 55.0
        for kw in low_margin:
            if kw in lower:
                return 42.0
        return 50.0  # Default

    def _build_rationale(
        self, concept: str, signals: List[dict], scores: Dict[str, float]
    ) -> str:
        """Build a human-readable rationale for this opportunity."""
        sources = list(set(s["source"] for s in signals))
        top_velocity = max(s["velocity"] for s in signals)

        lines = [
            f"## {concept.title()}",
            "",
            f"**Composite Score:** {scores.get('demand', 0) * scores.get('margin_est', 0) / 100:.1f}",
            "",
            f"**Demand:** {scores['demand']:.1f}/100 — trending across {len(sources)} source(s): {', '.join(sources)}",
            f"**Competition:** {scores['competition']:.1f}/10 — {'low' if scores['competition'] < 3 else 'medium' if scores['competition'] < 6 else 'high'} supply",
            f"**Printability:** {scores['printability']:.0%} — {'easy' if scores['printability'] > 0.8 else 'moderate' if scores['printability'] > 0.5 else 'complex'} to print on P1S",
            f"**Est. Margin:** {scores['margin_est']:.0f}%",
            "",
            f"**Top signal velocity:** {top_velocity:.1f} (from {len(signals)} signals)",
            "",
            "**Recommendation:** " + (
                "Strong candidate — high demand, low competition, easy to print."
                if scores["demand"] > 50 and scores["competition"] < 4 and scores["printability"] > 0.7
                else "Worth exploring — moderate signals, review before designing."
                if scores["demand"] > 25
                else "Weak signal — monitor but don't prioritize."
            ),
        ]
        return "\n".join(lines)
