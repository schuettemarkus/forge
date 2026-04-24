from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class QAReport(Base):
    __tablename__ = "qa_report"

    design_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("design.id")
    )
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    checks_json: Mapped[dict] = mapped_column(JSON, default=dict)
    time_s: Mapped[int] = mapped_column(Integer, default=0)
    filament_g: Mapped[float] = mapped_column(Float, default=0.0)
    cost_estimate_c: Mapped[int] = mapped_column(Integer, default=0)
