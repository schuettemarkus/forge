from __future__ import annotations

import uuid
from typing import Optional

from datetime import datetime

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Printer(Base):
    __tablename__ = "printer"

    model: Mapped[str] = mapped_column(String(50))
    serial: Mapped[str] = mapped_column(String(100))
    ip: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="offline")
    last_seen: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # v3: Distributed printer network
    operator_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("operator.id"), nullable=True
    )
    connection_type: Mapped[str] = mapped_column(String(10), default="lan")  # lan | remote
    endpoint_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_key_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    capabilities_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    location_label: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
