from __future__ import annotations

from typing import List, Optional

import uuid
from datetime import datetime

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
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
    status: Optional[str] = Query(None, max_length=20),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
) -> List[OpportunityOut]:
    query = select(Opportunity).where(Opportunity.deleted_at.is_(None))
    if status:
        query = query.where(Opportunity.status == status)
    query = query.order_by(Opportunity.score.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    rows = result.scalars().all()
    return [OpportunityOut.model_validate(r) for r in rows]


@router.get("/{opportunity_id}", response_model=OpportunityOut)
async def get_opportunity(
    opportunity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
) -> OpportunityOut:
    result = await db.execute(
        select(Opportunity).where(
            Opportunity.id == opportunity_id,
            Opportunity.deleted_at.is_(None),
        )
    )
    opp = result.scalar_one_or_none()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )
    return OpportunityOut.model_validate(opp)
