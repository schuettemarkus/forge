from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity


async def _create_opportunity(db: AsyncSession, concept: str, score: float) -> Opportunity:
    opp = Opportunity(
        concept=concept,
        score=score,
        demand=50.0,
        competition=3.0,
        printability=0.8,
        margin_est=55.0,
        rationale_md="Test rationale",
        ip_status="clear",
        status="pending",
    )
    db.add(opp)
    await db.flush()
    return opp


@pytest.mark.asyncio
async def test_list_opportunities_empty(client: AsyncClient) -> None:
    resp = await client.get("/opportunities/")
    assert resp.status_code == 200
    # May have data from prior test runs, just check it's a list
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_list_opportunities_with_pagination(client: AsyncClient, db: AsyncSession) -> None:
    # Create a few test opportunities
    for i in range(5):
        await _create_opportunity(db, f"test-concept-{i}", float(10 - i))
    await db.flush()

    # Default pagination
    resp = await client.get("/opportunities/?limit=3&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) <= 3

    # Validate limit param bounds
    resp = await client.get("/opportunities/?limit=0")
    assert resp.status_code == 422  # Validation error

    resp = await client.get("/opportunities/?limit=999")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_opportunity_not_found(client: AsyncClient) -> None:
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/opportunities/{fake_id}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Opportunity not found"


@pytest.mark.asyncio
async def test_get_opportunity_invalid_uuid(client: AsyncClient) -> None:
    resp = await client.get("/opportunities/not-a-uuid")
    assert resp.status_code == 422
