from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class CreditLedger(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "credit_ledger"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    # positive = credited (signup, purchase), negative = spent (generation)
    amount: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(64))  # signup|purchase|generation|refund
    ref_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
