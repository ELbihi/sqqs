from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class User(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    provider: Mapped[str] = mapped_column(String(32), default="password")
    credits: Mapped[int] = mapped_column(Integer, default=0)

    characters = relationship("Character", back_populates="owner", cascade="all, delete-orphan")
    garments = relationship("Garment", back_populates="owner", cascade="all, delete-orphan")
    backgrounds = relationship("Background", back_populates="owner", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
