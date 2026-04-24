from __future__ import annotations

from typing import Optional

from datetime import datetime

from sqlalchemy import Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Order(Base):
    __tablename__ = "order"

    marketplace: Mapped[str] = mapped_column(String(20))
    external_id: Mapped[str] = mapped_column(String(200))
    sku: Mapped[str] = mapped_column(String(100))
    customer_hash: Mapped[str] = mapped_column(String(64))
    variant_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    price_c: Mapped[int] = mapped_column(Integer)
    cost_c: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    shipped_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    tracking_no: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
