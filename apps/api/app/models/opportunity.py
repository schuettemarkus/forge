from __future__ import annotations

from typing import Optional

from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Opportunity(Base):
    __tablename__ = "opportunity"

    concept: Mapped[str] = mapped_column(String(500))
    score: Mapped[float] = mapped_column(Float, default=0.0)
    demand: Mapped[float] = mapped_column(Float, default=0.0)
    competition: Mapped[float] = mapped_column(Float, default=0.0)
    printability: Mapped[float] = mapped_column(Float, default=0.0)
    margin_est: Mapped[float] = mapped_column(Float, default=0.0)
    rationale_md: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_status: Mapped[str] = mapped_column(String(20), default="pending")
    status: Mapped[str] = mapped_column(String(20), default="pending")
