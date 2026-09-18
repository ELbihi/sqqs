from sqlalchemy import ForeignKey, String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


# Section 17 - Generation Status Model
STATUS_FLOW = [
    "QUEUED",
    "PROCESSING",
    "PREPARING_CHARACTER",
    "PREPARING_GARMENT",
    "GENERATING",
    "UPSCALING",
    "COMPLETED",
]


class Generation(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "generations"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id"), nullable=True, index=True
    )

    output_type: Mapped[str] = mapped_column(String(16), default="image")  # image|video
    status: Mapped[str] = mapped_column(String(32), default="QUEUED", index=True)
    error: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    credits_cost: Mapped[int] = mapped_column(Integer, default=0)

    # Recipe: character + clothes + background + pose/motion
    character_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    garment_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    background_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    pose: Mapped[str | None] = mapped_column(String(64), nullable=True)
    instruction: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    params: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    project = relationship("Project", back_populates="generations")
    assets = relationship(
        "GenerationAsset", back_populates="generation", cascade="all, delete-orphan"
    )


class GenerationAsset(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "generation_assets"

    generation_id: Mapped[str] = mapped_column(
        ForeignKey("generations.id"), index=True
    )
    kind: Mapped[str] = mapped_column(String(16), default="image")  # image|video|thumbnail
    storage_key: Mapped[str] = mapped_column(String(512))

    generation = relationship("Generation", back_populates="assets")
