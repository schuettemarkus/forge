from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Render(Base):
    __tablename__ = "render"

    design_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("design.id")
    )
    angle: Mapped[int] = mapped_column(Integer, default=0)
    image_s3_key: Mapped[str] = mapped_column(Text)
    style: Mapped[str] = mapped_column(String(50))
