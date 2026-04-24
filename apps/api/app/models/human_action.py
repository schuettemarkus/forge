from __future__ import annotations

from typing import Optional

import uuid
from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class HumanAction(Base):
    __tablename__ = "human_action"

    ts: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped[str] = mapped_column(String(100))
    screen: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(50))
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
