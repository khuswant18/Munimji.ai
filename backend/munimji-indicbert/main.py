# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import os
import re

from model_loader import IntentModel
from database import SessionLocal, engine, Base
from models import User, Debt

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Munimji NLU + Debt System", version="0.1")

# --------- DB dependency ---------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------- AI model (same as before) ---------
_model = None

def get_model():
    global _model
    if _model is None:
        _model = IntentModel(model_name=os.environ.get("INTENT_MODEL", "ai4bharat/indic-bert"))
    return _model

# --------- Pydantic schemas ---------
class InferReq(BaseModel):
    text: str

class InferRes(BaseModel):
    intent: str
    confidence: float

class UserCreate(BaseModel):
    phone: str
    name: Optional[str] = None

class UserRead(BaseModel):
    id: int
    phone: str
    name: Optional[str] = None

    class Config:
        orm_mode = True

class DebtRead(BaseModel):
    id: int
    amount: float
    description: Optional[str] = None
    creditor_name: Optional[str] = None
    created_at: str

    class Config:
        orm_mode = True

class MessageRequest(BaseModel):
    phone: str
    text: str  # raw user message like "Ramesh ko 1500 rs udhaar diya"

class MessageResponse(BaseModel):
    user: UserRead
    debt: DebtRead
    predicted_intent: Optional[str] = None
    confidence: Optional[float] = None
    note: Optional[str] = None

# --------- Simple amount extractor (for demo) ---------
def extract_amount(text: str) -> Optional[float]:
    # Very simple regex: first number like 1500, 1,500, 1500.50
    m = re.search(r"([0-9][\d,]*\.?\d*)", text)
    if not m:
        return None
    num_str = m.group(1).replace(",", "")
    try:
        return float(num_str)
    except ValueError:
        return None

# --------- Basic routes ---------
@app.get("/")
def root():
    return {"service": "munimji-debt-system", "status": "ok"}

@app.post("/infer", response_model=InferRes)
def infer(req: InferReq):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    model = get_model()
    res = model.predict(req.text)
    return {"intent": res["intent"], "confidence": res["confidence"]}

# --------- User CRUD (minimal) ---------
@app.post("/users", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == user_in.phone).first()
    if user:
        raise HTTPException(status_code=400, detail="User with this phone already exists")
    user = User(phone=user_in.phone, name=user_in.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/users/{phone}", response_model=UserRead)
def get_user(phone: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/{phone}/debts", response_model=List[DebtRead])
def get_user_debts(phone: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    debts = db.query(Debt).filter(Debt.user_id == user.id).order_by(Debt.created_at.desc()).all()
    return debts

# --------- AI-powered "message" endpoint that saves debt ---------
@app.post("/message", response_model=MessageResponse)
def add_debt_from_message(req: MessageRequest, db: Session = Depends(get_db)):
    # 1. get or create user
    user = db.query(User).filter(User.phone == req.phone).first()
    if not user:
        user = User(phone=req.phone)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. run AI intent model (for now, backbone; once you fine-tune, you'll get proper intents)
    model = get_model()
    ai_res = model.predict(req.text)
    intent = ai_res["intent"]
    conf = ai_res["confidence"]

    # 3. extract amount from text (simple regex)
    amount = extract_amount(req.text)
    if amount is None:
        raise HTTPException(status_code=400, detail="Could not find amount in text. Please include a number.")

    # 4. naive creditor_name extraction (optional, example only)
    creditor_name = None  # you can improve this later with NER
    description = req.text

    # 5. save debt
    debt = Debt(
        user_id=user.id,
        amount=amount,
        description=description,
        creditor_name=creditor_name,
    )
    db.add(debt)
    db.commit()
    db.refresh(debt)

    return MessageResponse(
        user=user,
        debt=debt,
        predicted_intent=str(intent),
        confidence=float(conf),
        note="This is a simple demo. Once you fine-tune IndicBERT for intents/entities, replace the logic accordingly."
    )
