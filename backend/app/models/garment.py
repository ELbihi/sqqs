from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class Garment(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "garments"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(128), nullable=True)
    original_image_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    cleaned_image_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    segmentation_mask_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    color_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    owner = relationship("User", back_populates="garments")
