from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.models import CreditLedger, User
from app.services import credits

router = APIRouter(prefix="/billing", tags=["billing"])

# Section 19 - illustrative plans (placeholders until unit economics measured)
PLANS = [
    {"id": "free", "name": "Free", "monthly_credits": 30, "price_eur": 0},
    {"id": "creator", "name": "Creator", "monthly_credits": 300, "price_eur": 9},
    {"id": "pro", "name": "Pro", "monthly_credits": 1200, "price_eur": 29},
    {"id": "business", "name": "Business", "monthly_credits": 5000, "price_eur": 99},
]


class BalanceOut(BaseModel):
    credits: int


class PurchaseIn(BaseModel):
    amount: int


@router.get("/plans")
def list_plans():
    return {"plans": PLANS}


@router.get("/balance", response_model=BalanceOut)
def balance(user: User = Depends(get_current_user)):
    return BalanceOut(credits=user.credits)


@router.get("/ledger")
def ledger(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(CreditLedger)
        .filter(CreditLedger.owner_id == user.id)
        .order_by(CreditLedger.created_at.desc())
        .all()
    )
    return [
        {"amount": r.amount, "reason": r.reason, "ref_id": r.ref_id, "at": r.created_at}
        for r in rows
    ]


@router.post("/credits/purchase", response_model=BalanceOut)
def purchase(body: PurchaseIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """DEV ONLY: grant credits without payment. Replace with Stripe webhook."""
    credits.grant(db, user, body.amount, "purchase")
    db.commit()
    db.refresh(user)
    return BalanceOut(credits=user.credits)
