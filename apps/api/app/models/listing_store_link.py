from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ListingStoreLink(Base):
    __tablename__ = "listing_store_link"

    listing_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("listing.id")
    )
    store_connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("store_connection.id")
    )
    external_product_id: Mapped[str] = mapped_column(String(200))
    sync_status: Mapped[str] = mapped_column(String(20), default="synced")  # synced | pending | error

    __table_args__ = (
        UniqueConstraint("store_connection_id", "external_product_id", name="uq_store_external_product"),
    )
