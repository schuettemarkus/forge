from __future__ import annotations

import pytest

from app.scoring.scorer import OpportunityScorer


@pytest.fixture
def scorer() -> OpportunityScorer:
    return OpportunityScorer()


def test_normalize_concept(scorer: OpportunityScorer) -> None:
    assert scorer._normalize_concept("3D Printed Desk Organizer") == "desk organizer"
    assert scorer._normalize_concept("Custom Cookie Cutter") == "cookie cutter"
    assert scorer._normalize_concept("DIY Phone Stand") == "phone stand"
    assert scorer._normalize_concept("  hello world  ") == "hello world"
    assert len(scorer._normalize_concept("ab")) <= 3  # Short input


def test_is_blocked_ip(scorer: OpportunityScorer) -> None:
    assert scorer._is_blocked("disney princess planter")
    assert scorer._is_blocked("pokemon cookie cutter")
    assert scorer._is_blocked("nintendo switch holder")
    assert scorer._is_blocked("star wars helmet")
    assert scorer._is_blocked("nfl logo coaster")
    assert not scorer._is_blocked("desk organizer")
    assert not scorer._is_blocked("cable management")
    assert not scorer._is_blocked("gridfinity bin")


def test_is_blocked_categories(scorer: OpportunityScorer) -> None:
    assert scorer._is_blocked("firearms accessory mount")
    assert scorer._is_blocked("gun accessories holder")
    assert scorer._is_blocked("political sign stand")
    assert scorer._is_blocked("religious figurine")
    assert not scorer._is_blocked("kitchen utensil holder")


def test_estimate_printability(scorer: OpportunityScorer) -> None:
    # High printability items
    assert scorer._estimate_printability("desk organizer") == 0.9
    assert scorer._estimate_printability("wall hook") == 0.9
    assert scorer._estimate_printability("gridfinity bin") == 0.9

    # Medium
    assert scorer._estimate_printability("cookie cutter") == 0.7

    # Low
    assert scorer._estimate_printability("articulated dragon") == 0.4

    # Default
    assert scorer._estimate_printability("something random") == 0.6


def test_estimate_margin(scorer: OpportunityScorer) -> None:
    assert scorer._estimate_margin("cookie cutter") == 65.0
    assert scorer._estimate_margin("desk organizer") == 55.0
    assert scorer._estimate_margin("large vase") == 42.0
    assert scorer._estimate_margin("unknown product") == 50.0


def test_compute_scores(scorer: OpportunityScorer) -> None:
    signals = [
        {"source": "google_trends", "query": "desk organizer", "velocity": 50.0, "volume": 30.0, "geography": "US"},
        {"source": "etsy", "query": "desk organizer", "velocity": 40.0, "volume": 500.0, "geography": "US"},
    ]
    scores = scorer._compute_scores("desk organizer", signals)
    assert "demand" in scores
    assert "competition" in scores
    assert "printability" in scores
    assert "margin_est" in scores
    assert "ip_safe" in scores
    assert scores["ip_safe"] == 1.0
    assert scores["printability"] == 0.9  # organizer = high
    assert scores["demand"] <= 100  # Capped


def test_build_rationale(scorer: OpportunityScorer) -> None:
    signals = [{"source": "google_trends", "query": "test", "velocity": 50.0, "volume": 30.0, "geography": "US"}]
    scores = {"demand": 60.0, "competition": 2.0, "printability": 0.9, "margin_est": 55.0, "ip_safe": 1.0}
    rationale = scorer._build_rationale("desk organizer", signals, scores)
    assert "Desk Organizer" in rationale
    assert "Demand" in rationale
    assert "Recommendation" in rationale
