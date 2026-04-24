from __future__ import annotations

from typing import Optional

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Printer(Base):
    __tablename__ = "printer"

    model: Mapped[str] = mapped_column(String(50))
    serial: Mapped[str] = mapped_column(String(100))
    ip: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="offline")
    last_seen: Mapped[Optional[datetime]] = mapped_column(nullable=True)
