from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user, require_owner
from app.db import get_db
from app.models.printer import Printer

router = APIRouter()


class PrinterOut(BaseModel):
    id: uuid.UUID
    model: str
    serial: str
    ip: str
    status: str
    last_seen: Optional[datetime]
    connection_type: str
    location_label: Optional[str]
    capabilities_json: Optional[Dict]
    created_at: datetime

    model_config = {"from_attributes": True}


class PrinterCreate(BaseModel):
    model: str = Field(max_length=50)
    serial: str = Field(max_length=100)
    ip: str = Field(max_length=50)
    connection_type: str = Field(default="lan", max_length=10)
    location_label: Optional[str] = Field(default=None, max_length=200)
    capabilities_json: Optional[Dict] = None


class PrinterUpdate(BaseModel):
    model: Optional[str] = Field(default=None, max_length=50)
    serial: Optional[str] = Field(default=None, max_length=100)
    ip: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=20)
    connection_type: Optional[str] = Field(default=None, max_length=10)
    location_label: Optional[str] = Field(default=None, max_length=200)
    capabilities_json: Optional[Dict] = None


@router.get("/", response_model=List[PrinterOut])
async def list_printers(
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
) -> List[PrinterOut]:
    result = await db.execute(
        select(Printer).where(Printer.deleted_at.is_(None)).order_by(Printer.created_at.desc())
    )
    return [PrinterOut.model_validate(p) for p in result.scalars().all()]


@router.get("/{printer_id}", response_model=PrinterOut)
async def get_printer(
    printer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(get_current_user),
) -> PrinterOut:
    result = await db.execute(
        select(Printer).where(Printer.id == printer_id, Printer.deleted_at.is_(None))
    )
    printer = result.scalar_one_or_none()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Printer not found")
    return PrinterOut.model_validate(printer)


@router.post("/", response_model=PrinterOut, status_code=status.HTTP_201_CREATED)
async def create_printer(
    data: PrinterCreate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_owner),
) -> PrinterOut:
    printer = Printer(
        model=data.model,
        serial=data.serial,
        ip=data.ip,
        connection_type=data.connection_type,
        location_label=data.location_label,
        capabilities_json=data.capabilities_json,
        status="offline",
    )
    db.add(printer)
    await db.flush()
    await db.refresh(printer)
    return PrinterOut.model_validate(printer)


@router.put("/{printer_id}", response_model=PrinterOut)
async def update_printer(
    printer_id: uuid.UUID,
    data: PrinterUpdate,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_owner),
) -> PrinterOut:
    result = await db.execute(
        select(Printer).where(Printer.id == printer_id, Printer.deleted_at.is_(None))
    )
    printer = result.scalar_one_or_none()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Printer not found")

    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(printer, field, value)

    await db.flush()
    await db.refresh(printer)
    return PrinterOut.model_validate(printer)


@router.delete("/{printer_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_printer(
    printer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict = Depends(require_owner),
) -> None:
    from datetime import datetime, timezone
    result = await db.execute(
        select(Printer).where(Printer.id == printer_id, Printer.deleted_at.is_(None))
    )
    printer = result.scalar_one_or_none()
    if not printer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Printer not found")
    printer.deleted_at = datetime.now(timezone.utc)
    await db.flush()
