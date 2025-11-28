# backend/db/session.py
"""
Database session configuration with connection pooling optimizations.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    'postgresql://neondb_owner:npg_PgrLGhItM4U0@ep-muddy-night-a4pigh32-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
)

# Connection pool settings for better performance
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,  # Number of connections to keep open
    max_overflow=10,  # Additional connections when pool is exhausted
    pool_timeout=30,  # Timeout waiting for connection from pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Verify connection is alive before using
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """
    Get database session.
    Use as context manager or with next() for single operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    Get a new database session directly (not a generator).
    Caller is responsible for closing the session.
    """
    return SessionLocal() 