from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class Background(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "backgrounds"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(32), default="library")  # library|upload|camera|ai
    image_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    prompt: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    owner = relationship("User", back_populates="backgrounds")
