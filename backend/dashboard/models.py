# backend/dashboard/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.chatbot_backend.db.session import Base  # adjust import to your project

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    phone_number = Column(String, nullable=True)
    outstanding_balance = Column(Float, default=0.0)
    last_activity = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="customers")


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    phone_number = Column(String, nullable=True)
    outstanding_balance = Column(Float, default=0.0)
    last_activity = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="suppliers")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String, nullable=False)  # "sale","purchase","expense","udhaar","payment"
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    counterparty_name = Column(String, nullable=True)  # customer/supplier name
    counterparty_type = Column(String, nullable=True)  # "customer"/"supplier"/null
    source = Column(String, nullable=True, default="manual")  # "whatsapp","pdf","cash",...
    payment_method = Column(String, nullable=True)  # "cash","upi","bank" (for cashbook)
    extra_metadata = Column(Text, nullable=True)  # optional JSON as string (bill url, attachments)  # Renamed from 'metadata'
    created_at = Column(DateTime, server_default=func.now(), index=True)

    user = relationship("User", back_populates="ledger_entries")


# OPTIONAL: quick table for CSV exports / audit if needed
class ExportRecord(Base):
    __tablename__ = "export_records"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    export_type = Column(String)  # "ledger_csv","statement_pdf",...
    path = Column(String)  # file path or URL
    created_at = Column(DateTime, server_default=func.now())

# Note: User relationships (customers, suppliers, ledger_entries) are defined 
# in backend/chatbot_backend/db/models.py User class
