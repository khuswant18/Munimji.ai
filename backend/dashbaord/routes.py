# backend/dashboard/routes.py
import os
import random
import string
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

# Twilio client (optional)
from twilio.rest import Client as TwilioClient

# reuse your existing DB session and models
from ..chatbot_backend.db.session import get_db
from ..chatbot_backend.db.models import User
from .models import LedgerEntry, Customer, Supplier  # assume these exist & have sensible fields

router = APIRouter(prefix="/api", tags=["dashboard"])

# In-memory stores for demo; replace with Redis/JWT for prod
otp_store: Dict[str, str] = {}
token_store: Dict[str, int] = {}  # token -> user_id mapping (demo)


# ---------- Utilities ----------
def _gen_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def _gen_token(length: int = 32) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def _send_otp_via_twilio(phone: str, otp: str) -> bool:
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth = os.environ.get("TWILIO_AUTH_TOKEN")
    from_num = os.environ.get("TWILIO_FROM_NUMBER")
    if not (sid and auth and from_num):
        # Twilio not configured — print OTP for local development
        print(f"[DEV-OTP] {phone} -> OTP: {otp}")
        return False
    client = TwilioClient(sid, auth)
    body = f"Your Munimji login OTP is: {otp}"
    try:
        client.messages.create(to=phone, from_=from_num, body=body)
        return True
    except Exception as e:
        print("Twilio send error:", e)
        return False


# ---------- Pydantic schemas ----------
class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., example="+919876543210")


class SendOTPResponse(BaseModel):
    success: bool


class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp: str


class VerifyOTPResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    user: Optional[Dict] = None


class UserOut(BaseModel):
    id: int
    phone_number: str
    name: Optional[str] = None
    shop_name: Optional[str] = None


class LedgerEntryOut(BaseModel):
    id: int
    date: Optional[str] = None
    type: str
    amount: float
    description: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_type: Optional[str] = None
    source: Optional[str] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    phone_number: Optional[str] = None
    outstanding_balance: float = 0.0
    last_activity: Optional[str] = None


class SupplierOut(BaseModel):
    id: int
    name: str
    phone_number: Optional[str] = None
    outstanding_balance: float = 0.0
    last_activity: Optional[str] = None


class AddEntryRequest(BaseModel):
    type: str  # "sale" | "purchase" | "expense" | "udhaar" | "payment"
    amount: float
    description: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_type: Optional[str] = None  # "customer" | "supplier" | None


class OverviewOut(BaseModel):
    total_sales: float
    total_purchases: float
    total_expenses: float
    net_income: float
    outstanding_udhaar: float
    recent_activity: List[LedgerEntryOut]


# ---------- Auth dependency ----------
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    """
    Expects header Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization header")
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    token = authorization.split(" ", 1)[1].strip()
    user_id = token_store.get(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# ---------- Auth endpoints ----------
@router.post("/auth/send-otp", response_model=SendOTPResponse)
def send_otp(req: SendOTPRequest):
    phone = req.phone_number.strip()
    otp = _gen_otp()
    otp_store[phone] = otp
    _send_otp_via_twilio(phone, otp)
    # For security: do not return OTP in response; printed to console in dev mode
    return SendOTPResponse(success=True)


@router.post("/auth/verify-otp", response_model=VerifyOTPResponse)
def verify_otp(req: VerifyOTPRequest, db: Session = Depends(get_db)):
    phone = req.phone_number.strip()
    expected = otp_store.get(phone)
    if not expected or req.otp.strip() != expected:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    # OTP valid -> create/fetch user
    user = db.query(User).filter(User.phone_number == phone).first()
    if not user:
        user = User(phone_number=phone)
        db.add(user)
        db.commit()
        db.refresh(user)
    # create token and store mapping
    token = _gen_token()
    token_store[token] = user.id
    # clear otp
    otp_store.pop(phone, None)
    return VerifyOTPResponse(success=True, token=token, user={"id": user.id, "phone_number": user.phone_number, "name": user.name})


@router.post("/auth/logout")
def logout(current_user: User = Depends(get_current_user)):
    # remove all tokens for this demo user
    remove = []
    for t, uid in list(token_store.items()):
        if uid == current_user.id:
            remove.append(t)
    for t in remove:
        token_store.pop(t, None)
    return {"success": True}


# ---------- Dashboard endpoints ----------
@router.get("/dashboard/overview", response_model=OverviewOut)
def get_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id

    # Aggregates
    total_sales = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0.0)).filter(
        LedgerEntry.user_id == user_id, LedgerEntry.type == "sale"
    ).scalar() or 0.0

    total_purchases = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0.0)).filter(
        LedgerEntry.user_id == user_id, LedgerEntry.type == "purchase"
    ).scalar() or 0.0

    total_expenses = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0.0)).filter(
        LedgerEntry.user_id == user_id, LedgerEntry.type == "expense"
    ).scalar() or 0.0

    # udhaar outstanding
    outstanding = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0.0)).filter(
        LedgerEntry.user_id == user_id, LedgerEntry.type == "udhaar"
    ).scalar() or 0.0

    net_income = (total_sales - total_purchases - total_expenses)

    # recent activity (20)
    recent_q = db.query(LedgerEntry).filter(LedgerEntry.user_id == user_id).order_by(LedgerEntry.created_at.desc()).limit(10).all()
    recent = [
        LedgerEntryOut(
            id=e.id,
            date=str(e.created_at.date()) if hasattr(e, "created_at") and e.created_at else None,
            type=e.type,
            amount=e.amount,
            description=e.description,
            counterparty_name=e.counterparty_name,
            counterparty_type=e.counterparty_type,
            source=e.source
        )
        for e in recent_q
    ]

    return OverviewOut(
        total_sales=total_sales,
        total_purchases=total_purchases,
        total_expenses=total_expenses,
        net_income=net_income,
        outstanding_udhaar=outstanding,
        recent_activity=recent
    )


@router.get("/dashboard/ledger", response_model=List[LedgerEntryOut])
def get_ledger(limit: int = 50, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    rows = db.query(LedgerEntry).filter(LedgerEntry.user_id == user_id).order_by(LedgerEntry.created_at.desc()).limit(limit).all()
    return [
        LedgerEntryOut(
            id=r.id,
            date=str(r.created_at.date()) if r.created_at else None,
            type=r.type,
            amount=r.amount,
            description=r.description,
            counterparty_name=r.counterparty_name,
            counterparty_type=r.counterparty_type,
            source=r.source
        ) for r in rows
    ]


@router.get("/dashboard/transactions/{tx_id}", response_model=LedgerEntryOut)
def get_transaction(tx_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = db.query(LedgerEntry).filter(LedgerEntry.id == tx_id, LedgerEntry.user_id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return LedgerEntryOut(
        id=row.id,
        date=str(row.created_at.date()) if row.created_at else None,
        type=row.type,
        amount=row.amount,
        description=row.description,
        counterparty_name=row.counterparty_name,
        counterparty_type=row.counterparty_type,
        source=row.source
    )


@router.get("/dashboard/customers", response_model=List[CustomerOut])
def get_customers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    customers = db.query(Customer).filter(Customer.user_id == user_id).order_by(Customer.name.asc()).all()
    out = []
    for c in customers:
        out.append(CustomerOut(
            id=c.id,
            name=c.name,
            phone_number=c.phone_number,
            outstanding_balance=c.outstanding_balance or 0.0,
            last_activity=str(c.last_activity.date()) if getattr(c, "last_activity", None) else None
        ))
    return out


@router.get("/dashboard/suppliers", response_model=List[SupplierOut])
def get_suppliers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    suppliers = db.query(Supplier).filter(Supplier.user_id == user_id).order_by(Supplier.name.asc()).all()
    out = []
    for s in suppliers:
        out.append(SupplierOut(
            id=s.id,
            name=s.name,
            phone_number=s.phone_number,
            outstanding_balance=s.outstanding_balance or 0.0,
            last_activity=str(s.last_activity.date()) if getattr(s, "last_activity", None) else None
        ))
    return out


@router.get("/dashboard/udhaar", response_model=List[LedgerEntryOut])
def get_udhaar(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(LedgerEntry).filter(LedgerEntry.user_id == current_user.id, LedgerEntry.type == "udhaar").order_by(LedgerEntry.created_at.desc()).all()
    return [
        LedgerEntryOut(
            id=r.id,
            date=str(r.created_at.date()) if r.created_at else None,
            type=r.type,
            amount=r.amount,
            description=r.description,
            counterparty_name=r.counterparty_name,
            counterparty_type=r.counterparty_type,
            source=r.source
        ) for r in rows
    ]


@router.post("/dashboard/add-entry")
def add_entry(req: AddEntryRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    # Basic validation
    if req.amount is None or req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be > 0")
    # create LedgerEntry instance - adapt fields to your model
    entry = LedgerEntry(
        user_id=user_id,
        type=req.type,
        amount=req.amount,
        description=req.description,
        source="manual",
        counterparty_name=req.counterparty_name,
        counterparty_type=req.counterparty_type
    )
    db.add(entry)

    # Update outstanding balances
    if req.counterparty_type == "customer" and req.counterparty_name:
        cust = db.query(Customer).filter(Customer.user_id == user_id, Customer.name == req.counterparty_name).first()
        # create if not exists
        if not cust:
            cust = Customer(user_id=user_id, name=req.counterparty_name, phone_number=None, outstanding_balance=0.0)
            db.add(cust)
            db.flush()
        # interpret types
        if req.type == "sale" or req.type == "udhaar":
            cust.outstanding_balance = (cust.outstanding_balance or 0.0) + req.amount
        elif req.type == "payment":
            cust.outstanding_balance = (cust.outstanding_balance or 0.0) - req.amount

    if req.counterparty_type == "supplier" and req.counterparty_name:
        sup = db.query(Supplier).filter(Supplier.user_id == user_id, Supplier.name == req.counterparty_name).first()
        if not sup:
            sup = Supplier(user_id=user_id, name=req.counterparty_name, phone_number=None, outstanding_balance=0.0)
            db.add(sup)
            db.flush()
        if req.type == "purchase":
            sup.outstanding_balance = (sup.outstanding_balance or 0.0) + req.amount
        elif req.type == "payment":
            sup.outstanding_balance = (sup.outstanding_balance or 0.0) - req.amount

    db.commit()
    db.refresh(entry)
    return {"success": True, "id": entry.id}


# ---------- Cashbook & Expenses endpoints ----------
@router.get("/dashboard/cashbook", response_model=List[LedgerEntryOut])
def get_cashbook(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # cashbook is simply ledger entries filtered by source/payment method "cash"
    rows = db.query(LedgerEntry).filter(LedgerEntry.user_id == current_user.id, LedgerEntry.source == "cash").order_by(LedgerEntry.created_at.desc()).all()
    return [
        LedgerEntryOut(
            id=r.id,
            date=str(r.created_at.date()) if r.created_at else None,
            type=r.type,
            amount=r.amount,
            description=r.description,
            counterparty_name=r.counterparty_name,
            counterparty_type=r.counterparty_type,
            source=r.source
        ) for r in rows
    ]


@router.get("/dashboard/expenses", response_model=List[LedgerEntryOut])
def get_expenses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = db.query(LedgerEntry).filter(LedgerEntry.user_id == current_user.id, LedgerEntry.type == "expense").order_by(LedgerEntry.created_at.desc()).all()
    return [
        LedgerEntryOut(
            id=r.id,
            date=str(r.created_at.date()) if r.created_at else None,
            type=r.type,
            amount=r.amount,
            description=r.description,
            counterparty_name=r.counterparty_name,
            counterparty_type=r.counterparty_type,
            source=r.source
        ) for r in rows
    ]


# ---------- Reports endpoint (simple aggregations) ----------
@router.get("/dashboard/reports")
def get_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_id = current_user.id
    # Profit & Loss (monthly placeholder)
    sales_by_month = db.query(func.date_trunc("month", LedgerEntry.created_at).label("month"),
                              func.coalesce(func.sum(func.case([(LedgerEntry.type == "sale", LedgerEntry.amount)], else_=0.0)), 0.0).label("sales"),
                              func.coalesce(func.sum(func.case([(LedgerEntry.type == "purchase", LedgerEntry.amount)], else_=0.0)), 0.0).label("purchases"),
                              func.coalesce(func.sum(func.case([(LedgerEntry.type == "expense", LedgerEntry.amount)], else_=0.0)), 0.0).label("expenses")
                              ).filter(LedgerEntry.user_id == user_id).group_by("month").order_by("month").limit(12).all()

    # Sales by customer
    sales_by_customer = db.query(LedgerEntry.counterparty_name, func.coalesce(func.sum(LedgerEntry.amount), 0.0).label("total")).filter(
        LedgerEntry.user_id == user_id, LedgerEntry.type == "sale"
    ).group_by(LedgerEntry.counterparty_name).order_by(func.sum(LedgerEntry.amount).desc()).limit(10).all()

    # Simple udhaar aging placeholder
    udhaar = db.query(LedgerEntry).filter(LedgerEntry.user_id == user_id, LedgerEntry.type == "udhaar").order_by(LedgerEntry.created_at.desc()).limit(20).all()

    return {
        "sales_by_month": [{"month": str(r.month.date()), "sales": float(r.sales), "purchases": float(r.purchases), "expenses": float(r.expenses)} for r in sales_by_month],
        "sales_by_customer": [{"customer": r[0], "total": float(r[1])} for r in sales_by_customer],
        "udhaar": [{"id": u.id, "counterparty": u.counterparty_name, "amount": u.amount, "date": str(u.created_at.date()) if u.created_at else None} for u in udhaar]
    }


# ---------- Profile endpoints ----------
@router.get("/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return UserOut(id=current_user.id, phone_number=current_user.phone_number, name=current_user.name, shop_name=current_user.shop_name)


class UpdateProfileRequest(BaseModel):
    name: Optional[str]
    shop_name: Optional[str]
    preferred_language: Optional[str]


@router.put("/me")
def update_profile(payload: UpdateProfileRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    u = db.query(User).filter(User.id == current_user.id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if payload.name is not None:
        u.name = payload.name
    if payload.shop_name is not None:
        u.shop_name = payload.shop_name
    if payload.preferred_language is not None:
        u.preferred_language = payload.preferred_language
    db.commit()
    db.refresh(u)
    return {"success": True, "user": {"id": u.id, "name": u.name, "shop_name": u.shop_name, "phone_number": u.phone_number}}
