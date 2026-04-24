from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.scoring.scorer import OpportunityScorer

router = APIRouter()


@router.post("/run")
async def trigger_scoring(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, object]:
    """Manually trigger the opportunity scorer."""
    scorer = OpportunityScorer()
    count = await scorer.run(db)
    return {"status": "completed", "opportunities_created": count}
