from __future__ import annotations

from typing import Optional

import uuid
from datetime import datetime

from sqlalchemy import Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class LedgerEntry(Base):
    __tablename__ = "ledger"

    ts: Mapped[datetime] = mapped_column(server_default=func.now())
    type: Mapped[str] = mapped_column(String(50))
    amount_c: Mapped[int] = mapped_column(Integer)
    ref_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    ref_table: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
