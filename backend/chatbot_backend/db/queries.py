from sqlalchemy.orm import Session
from backend.chatbot_backend.db.models import Conversation
from sqlalchemy import text
from ...dashbaord.models import LedgerEntry

def get_conversations_by_type(db: Session, user_id: int, message_type: str):
    """Get conversations filtered by context type using JSONB operator."""
    return db.query(Conversation).filter(
        Conversation.user_id == user_id,
        text("context ->> 'type' = :type")
    ).params(type=message_type).all()

def get_conversations_with_media(db: Session, user_id: int):
    """Get conversations that have media_id in context."""
    return db.query(Conversation).filter(
        Conversation.user_id == user_id,
        text("context ? 'media_id'")
    ).all()

def get_conversation_context_value(db: Session, conversation_id: int, key: str):
    """Get a specific value from conversation context."""
    result = db.query(
        text("context ->> :key").label('value')
    ).filter(
        Conversation.id == conversation_id
    ).params(key=key).first()
    return result.value if result else None 

def get_daily_summary(db: Session, user_id: int):
    """Get today's ledger summary."""
    from sqlalchemy import func
    today = func.current_date()
    result = db.query(
        func.sum(LedgerEntry.amount).label('total')
    ).filter(
        LedgerEntry.user_id == user_id,
        func.date(LedgerEntry.created_at) == today
    ).first()
    return result.total or 0

def get_inventory_stock(db: Session, user_id: int, item: str):
    """Get current stock for an item. Placeholder, need inventory model."""
    # For now, return dummy
    return 10 