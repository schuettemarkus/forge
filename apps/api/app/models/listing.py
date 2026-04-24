from __future__ import annotations

from typing import Optional

import uuid

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Listing(Base):
    __tablename__ = "listing"

    design_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("design.id")
    )
    sku: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    description_md: Mapped[str] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    price_c: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    etsy_listing_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    shopify_product_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
