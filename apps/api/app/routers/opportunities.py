from __future__ import annotations

from typing import List, Optional

import uuid
from datetime import datetime

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.opportunity import Opportunity

router = APIRouter()


class OpportunityOut(BaseModel):
    id: uuid.UUID
    concept: str
    score: float
    demand: float
    competition: float
    printability: float
    margin_est: float
    rationale_md: Optional[str]
    ip_status: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("/", response_model=List[OpportunityOut])
async def list_opportunities(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[OpportunityOut]:
    query = select(Opportunity).where(Opportunity.deleted_at.is_(None))
    if status:
        query = query.where(Opportunity.status == status)
    query = query.order_by(Opportunity.score.desc())
    result = await db.execute(query)
    rows = result.scalars().all()
    return [OpportunityOut.model_validate(r) for r in rows]


@router.get("/{opportunity_id}", response_model=OpportunityOut)
async def get_opportunity(
    opportunity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> OpportunityOut:
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opp = result.scalar_one()
    return OpportunityOut.model_validate(opp)
