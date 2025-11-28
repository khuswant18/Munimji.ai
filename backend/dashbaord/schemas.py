# backend/dashboard/schemas.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Auth schemas
class SendOTPRequest(BaseModel):
    phone_number: str

class SendOTPResponse(BaseModel):
    success: bool

class VerifyOTPRequest(BaseModel):
    phone_number: str
    otp: str

class VerifyOTPResponse(BaseModel):
    success: bool
    token: str
    user: dict  # Simplified user data

# Dashboard schemas
class LedgerEntryResponse(BaseModel):
    id: int
    user_id: int
    type: str
    amount: float
    description: Optional[str]
    created_at: datetime
    source: str
    counterparty_name: Optional[str]
    counterparty_type: Optional[str]

class CustomerResponse(BaseModel):
    id: int
    user_id: int
    name: str
    phone: Optional[str]
    outstanding_balance: float
    created_at: datetime

class SupplierResponse(BaseModel):
    id: int
    user_id: int
    name: str
    phone: Optional[str]
    outstanding_balance: float
    created_at: datetime

class AddEntryRequest(BaseModel):
    type: str
    amount: float
    description: Optional[str]
    counterparty_name: Optional[str]
    counterparty_type: Optional[str]