from sqlalchemy import ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class Character(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "characters"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(32), default="upload")  # upload|camera|ai
    original_photo_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    face_reference_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    body_reference_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    appearance_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    owner = relationship("User", back_populates="characters")

    @property
    def photos(self):
        saved = (self.appearance_metadata or {}).get("photos")
        if saved:
            return saved
        return [{"storage_key": self.original_photo_key, "label": "Main"}] if self.original_photo_key else []
