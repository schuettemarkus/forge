from __future__ import annotations

from typing import Optional

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Design(Base):
    __tablename__ = "design"

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunity.id")
    )
    source_path: Mapped[str] = mapped_column(String(20))  # parametric | remix | aigen
    license: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    license_attribution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_s3_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
