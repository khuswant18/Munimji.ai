"""
Optimized add_entry node with bulk operations and efficient DB handling.

Optimizations:
- Bulk insert for multiple entries
- Single transaction for all operations
- Lazy vectorstore updates (non-blocking)
- Connection reuse
"""
from typing import List, Dict, Any
from ..state import AgentState
from vectorstore.db_vector import add_to_vectorstore
from chatbot_backend.db.session import get_db
from dashboard.models import LedgerEntry, Customer, Supplier
from decorators.timeit import time_node, timed_context
from sqlalchemy.orm import Session
from sqlalchemy import insert
import threading


def _prepare_ledger_entries(
    entities: Dict[str, Any], 
    intent: str, 
    user_id: int
) -> List[Dict[str, Any]]:
    """
    Prepare ledger entry data from entities.
    Returns list of dicts ready for bulk insert.
    """
    entries_data = []
    
    for entry in entities.get("entries", []):
        if intent.startswith("add_sale"):
            ledger_type = "sale"
            amount = entry.get("amount") or (entry.get("quantity", 0) * entry.get("price", 0))
            item_name = entry.get("item", "item")
            quantity = entry.get("quantity", 1)
            customer = entry.get("customer", "")
            description = f"Sold {item_name} x{quantity} to {customer}" if customer else f"Sold {item_name} x{quantity}"
            counterparty_name = customer
            counterparty_type = "customer"
            
        elif intent.startswith("add_purchase"):
            ledger_type = "purchase"
            amount = entry.get("amount") or (entry.get("quantity", 0) * entry.get("price", 0))
            item_name = entry.get("item", "item")
            quantity = entry.get("quantity", 1)
            supplier = entry.get("supplier", "")
            description = f"Bought {item_name} x{quantity} from {supplier}" if supplier else f"Bought {item_name} x{quantity}"
            counterparty_name = supplier
            counterparty_type = "supplier"
        
        elif intent in ["add_inventory", "add_entry"]:
            ledger_type = "inventory"
            quantity = entry.get("quantity", 1)
            price = entry.get("price", 0)
            amount = quantity * price
            item_name = entry.get("item", "item")
            description = f"Added {quantity} {item_name} @ ₹{price}"
            counterparty_name = ""
            counterparty_type = ""
            
        elif intent == "add_expense":
            ledger_type = "expense"
            amount = entry.get("amount", 0)
            description = entry.get("description", "Expense")
            category = entry.get("category", "")
            if category:
                description = f"{category.capitalize()}: {description}"
            counterparty_name = entry.get("supplier", "")
            counterparty_type = "supplier"
            
        elif intent == "add_udhaar":
            ledger_type = "udhaar"
            amount = entry.get("amount", 0)
            customer = entry.get("customer", "Unknown")
            udhaar_type = entry.get("type", "given")
            description = f"Udhaar {udhaar_type}: {entry.get('description', '')} to {customer}"
            counterparty_name = customer
            counterparty_type = "customer"
            
        elif intent == "add_payment":
            ledger_type = "payment"
            amount = entry.get("amount", 0)
            customer = entry.get("customer", "")
            payment_type = entry.get("type", "received")
            description = f"Payment {payment_type}: {amount} from {customer}" if customer else f"Payment {payment_type}: {amount}"
            counterparty_name = customer
            counterparty_type = "customer"
            
        else:
            continue
        
        if amount:  # Only add if we have an amount
            entries_data.append({
                "user_id": user_id,
                "type": ledger_type,
                "amount": amount,
                "description": description,
                "counterparty_name": counterparty_name,
                "counterparty_type": counterparty_type,
            })
    
    return entries_data


def _add_to_vectorstore_async(content: str):
    """Add to vectorstore in background thread."""
    try:
        add_to_vectorstore(content)
    except Exception as e:
        print(f"Vectorstore error (non-blocking): {e}")


@time_node
def add_entry(state: AgentState) -> AgentState:
    """
    Add ledger entries with bulk operations.
    """
    entities = state["entities"]
    intent = state["intent"]
    user_id = state["user_id"] or 1
    
    # Initialize context if not present
    if "context" not in state or state["context"] is None:
        state["context"] = {}

    db: Session = next(get_db())

    try:
        with timed_context("db_prepare"):
            entries_data = _prepare_ledger_entries(entities, intent, user_id)
        
        if not entries_data:
            state["context"]["added"] = False
            state["context"]["error"] = "No valid entries to add"
            return state
        
        with timed_context("db_insert"):
            if len(entries_data) == 1:
                # Single entry - simple insert
                ledger_entry = LedgerEntry(**entries_data[0])
                db.add(ledger_entry)
            else:
                # Multiple entries - bulk insert
                db.execute(
                    insert(LedgerEntry),
                    entries_data
                )
            
            db.commit()
        
        state["context"]["added"] = True
        state["context"]["entries_count"] = len(entries_data)
        state["context"]["total_amount"] = sum(e.get("amount", 0) for e in entries_data)
        
    except Exception as e:
        db.rollback()
        state["context"]["error"] = str(e)
        state["context"]["added"] = False
    finally:
        db.close()

    # Add to vectorstore asynchronously (non-blocking)
    try:
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "content"):
            content = last_msg.content
        elif isinstance(last_msg, dict) and "content" in last_msg:
            content = last_msg["content"]
        else:
            content = str(last_msg)
        
        # Fire and forget - don't block on vectorstore
        thread = threading.Thread(target=_add_to_vectorstore_async, args=(content,))
        thread.daemon = True
        thread.start()
    except:
        pass  # Non-critical, ignore errors
    
    return state