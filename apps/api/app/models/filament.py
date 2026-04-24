from __future__ import annotations

from typing import Optional

import uuid

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FilamentSpool(Base):
    __tablename__ = "filament_spool"

    material: Mapped[str] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(50))
    hex: Mapped[str] = mapped_column(String(7))
    grams_remaining: Mapped[float] = mapped_column(Float, default=1000.0)
    cost_c_per_g: Mapped[int] = mapped_column(Integer, default=3)  # ~$0.03/g
    ams_slot: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    printer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("printer.id"), nullable=True
    )
