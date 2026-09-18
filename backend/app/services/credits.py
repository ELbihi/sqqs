"""Credit metering (section 19). Illustrative costs — replace once unit
economics are measured."""
from sqlalchemy.orm import Session

from app.models import CreditLedger, User

CREDIT_COST = {
    ("image", "standard"): 2,
    ("image", "hd"): 4,
    ("video", "5s"): 15,
    ("video", "10s"): 25,
}


def cost_for(output_type: str, tier: str = "standard") -> int:
    if output_type == "video":
        return CREDIT_COST[("video", tier if tier in ("5s", "10s") else "5s")]
    return CREDIT_COST[("image", tier if tier in ("standard", "hd") else "standard")]


def get_balance(db: Session, user: User) -> int:
    return user.credits


def charge(db: Session, user: User, amount: int, reason: str, ref_id: str | None = None) -> None:
    if user.credits < amount:
        raise ValueError("Insufficient credits")
    user.credits -= amount
    db.add(CreditLedger(owner_id=user.id, amount=-amount, reason=reason, ref_id=ref_id))
    db.add(user)


def grant(db: Session, user: User, amount: int, reason: str, ref_id: str | None = None) -> None:
    user.credits += amount
    db.add(CreditLedger(owner_id=user.id, amount=amount, reason=reason, ref_id=ref_id))
    db.add(user)
