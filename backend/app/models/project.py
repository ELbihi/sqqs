from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class Project(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), default="Untitled project")

    owner = relationship("User", back_populates="projects")
    generations = relationship(
        "Generation", back_populates="project", cascade="all, delete-orphan"
    )
