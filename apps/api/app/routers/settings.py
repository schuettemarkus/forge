from __future__ import annotations

from typing import Dict, Optional

from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models.operator import Operator

router = APIRouter()


class SettingsOut(BaseModel):
    email: str
    display_name: str
    role: str
    shop_name: str

    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    display_name: Optional[str] = None
    shop_name: Optional[str] = None


@router.get("/", response_model=SettingsOut)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> SettingsOut:
    """Get current user settings. Creates operator record if needed."""
    email = user["sub"]
    result = await db.execute(select(Operator).where(Operator.email == email))
    operator = result.scalar_one_or_none()

    if not operator:
        from app.config import settings as app_settings
        operator = Operator(
            email=email,
            display_name=email.split("@")[0],
            role=user.get("role", "owner"),
        )
        db.add(operator)
        await db.flush()
        await db.refresh(operator)

    from app.config import settings as app_settings
    return SettingsOut(
        email=operator.email,
        display_name=operator.display_name,
        role=operator.role,
        shop_name=app_settings.SHOP_NAME,
    )


@router.put("/", response_model=SettingsOut)
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> SettingsOut:
    """Update user settings."""
    email = user["sub"]
    result = await db.execute(select(Operator).where(Operator.email == email))
    operator = result.scalar_one_or_none()

    if not operator:
        operator = Operator(
            email=email,
            display_name=data.display_name or email.split("@")[0],
            role=user.get("role", "owner"),
        )
        db.add(operator)
    else:
        if data.display_name is not None:
            operator.display_name = data.display_name

    await db.flush()
    await db.refresh(operator)

    from app.config import settings as app_settings
    return SettingsOut(
        email=operator.email,
        display_name=operator.display_name,
        role=operator.role,
        shop_name=app_settings.SHOP_NAME,
    )
