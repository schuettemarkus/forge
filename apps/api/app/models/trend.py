from __future__ import annotations

from typing import Optional

from datetime import datetime

from sqlalchemy import Float, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TrendSignal(Base):
    __tablename__ = "trend_signal"

    source: Mapped[str] = mapped_column(String(50), index=True)
    query: Mapped[str] = mapped_column(String(500))
    velocity: Mapped[float] = mapped_column(Float, default=0.0)
    volume: Mapped[float] = mapped_column(Float, default=0.0)
    geography: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(index=True)
    raw_s3_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_trend_source_captured", "source", "captured_at"),
    )
