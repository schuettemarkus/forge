from __future__ import annotations

from typing import Optional

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class StoreConnection(Base):
    __tablename__ = "store_connection"

    platform: Mapped[str] = mapped_column(String(50))  # etsy | shopify | woocommerce | squarespace | manual
    display_name: Mapped[str] = mapped_column(String(200))
    credentials_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Fernet-encrypted in prod
    webhook_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | paused | error
