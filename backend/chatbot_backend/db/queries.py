from sqlalchemy.orm import Session
from backend.chatbot_backend.db.models import Conversation
from sqlalchemy import text
from ...dashboard.models import LedgerEntry, Customer

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
    """Get today's ledger summary - just total."""
    from sqlalchemy import func
    today = func.current_date()
    result = db.query(
        func.sum(LedgerEntry.amount).label('total')
    ).filter(
        LedgerEntry.user_id == user_id,
        func.date(LedgerEntry.created_at) == today
    ).first()
    return result.total or 0


def get_detailed_daily_summary(db: Session, user_id: int) -> dict:
    """
    Get detailed today's summary with breakdown by type and top customers.
    Returns dict with sales, purchases, expenses, udhaar details.
    """
    from sqlalchemy import func
    today = func.current_date()
    
    # Get totals by type
    type_totals = db.query(
        LedgerEntry.type,
        func.sum(LedgerEntry.amount).label('total'),
        func.count(LedgerEntry.id).label('count')
    ).filter(
        LedgerEntry.user_id == user_id,
        func.date(LedgerEntry.created_at) == today
    ).group_by(LedgerEntry.type).all()
    
    summary = {
        "sale": {"total": 0, "count": 0},
        "purchase": {"total": 0, "count": 0},
        "expense": {"total": 0, "count": 0},
        "udhaar": {"total": 0, "count": 0},
        "payment": {"total": 0, "count": 0},
    }
    
    for row in type_totals:
        if row.type in summary:
            summary[row.type] = {"total": row.total or 0, "count": row.count or 0}
    
    # Get udhaar by customer (who owes how much today)
    udhaar_by_customer = db.query(
        LedgerEntry.counterparty_name,
        func.sum(LedgerEntry.amount).label('total')
    ).filter(
        LedgerEntry.user_id == user_id,
        LedgerEntry.type == "udhaar",
        func.date(LedgerEntry.created_at) == today,
        LedgerEntry.counterparty_name.isnot(None)
    ).group_by(LedgerEntry.counterparty_name).order_by(
        func.sum(LedgerEntry.amount).desc()
    ).limit(10).all()
    
    summary["udhaar_details"] = [
        {"name": row.counterparty_name, "amount": row.total} 
        for row in udhaar_by_customer if row.counterparty_name
    ]
    
    # Get recent entries (last 5)
    recent_entries = db.query(LedgerEntry).filter(
        LedgerEntry.user_id == user_id,
        func.date(LedgerEntry.created_at) == today
    ).order_by(LedgerEntry.created_at.desc()).limit(5).all()
    
    summary["recent"] = [
        {
            "type": e.type,
            "amount": e.amount,
            "description": e.description or e.counterparty_name or ""
        }
        for e in recent_entries
    ]
    
    return summary


def get_all_udhaar_list(db: Session, user_id: int) -> list:
    """
    Get list of all customers who owe money (pending udhaar - payments).
    """
    from sqlalchemy import func, case
    
    # Calculate net balance for each customer (udhaar given - payments received)
    balances = db.query(
        LedgerEntry.counterparty_name,
        func.sum(
            case(
                (LedgerEntry.type == "udhaar", LedgerEntry.amount),
                (LedgerEntry.type == "payment", -LedgerEntry.amount),
                else_=0
            )
        ).label('balance')
    ).filter(
        LedgerEntry.user_id == user_id,
        LedgerEntry.type.in_(["udhaar", "payment"]),
        LedgerEntry.counterparty_name.isnot(None)
    ).group_by(LedgerEntry.counterparty_name).having(
        func.sum(
            case(
                (LedgerEntry.type == "udhaar", LedgerEntry.amount),
                (LedgerEntry.type == "payment", -LedgerEntry.amount),
                else_=0
            )
        ) > 0
    ).order_by(
        func.sum(
            case(
                (LedgerEntry.type == "udhaar", LedgerEntry.amount),
                (LedgerEntry.type == "payment", -LedgerEntry.amount),
                else_=0
            )
        ).desc()
    ).all()
    
    return [{"name": row.counterparty_name, "balance": row.balance} for row in balances]


def get_inventory_stock(db: Session, user_id: int, item: str):
    """Get current stock for an item. Placeholder, need inventory model."""
    # For now, return dummy
    return 10 