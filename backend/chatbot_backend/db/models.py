# backend/db/models.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, BIGINT, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    phone_number = Column(String, unique=True, nullable=False)
    name = Column(String)
    shop_name = Column(String)
    preferred_language = Column(String, default="hi-IN")
    plan = Column(String, default="free")
    state = Column(String, default="new")  # new, onboarding_name, onboarding_shop, menu
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    # Relationships to dashboard models
    customers = relationship("Customer", back_populates="user", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="user", cascade="all, delete-orphan")
    ledger_entries = relationship("LedgerEntry", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"))
    last_message = Column(Text)
    context = Column(JSONB)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Memory(Base):
    __tablename__ = "memory"
    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.id", ondelete="CASCADE"))
    key = Column(String)  # e.g., "message_embedding"
    value = Column(Text)  # Raw message text
    embedding_vector = Column(Vector(768))  # Adjust dimension based on your embedding model (e.g., 768 for sentence-transformers)
    created_at = Column(TIMESTAMP, server_default=func.now())

# Import dashboard models for Alembic detection 
try:
    from dashboard.models import LedgerEntry, Customer, Supplier
except ImportError:
    pass
