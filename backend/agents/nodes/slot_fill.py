"""
Slot Fill Node - Handles follow-up responses to fill missing slots.

This node processes user responses when we're waiting for slot values.
Uses regex-only extraction for speed (no LLM calls).

Flow:
- User: "pen add karo" → missing: [quantity, price]
- Bot: "Kitne pen?" 
- User: "2" → slot_fill extracts quantity=2, still missing: [price]
- Bot: "Pen ki price kitni rakhu?"
- User: "5" → slot_fill extracts price=5, complete!
"""
import re
from typing import Optional
from ..state import AgentState
from ...decorators.timeit import time_node


# Patterns for extracting slot values from follow-up responses
AMOUNT_PATTERN = re.compile(r'(?:rs?\.?|₹|rupee?s?|rupaiye?)?\s*(\d+(?:\.\d{1,2})?)', re.IGNORECASE)
QUANTITY_PATTERN = re.compile(r'^(\d+(?:\.\d{1,2})?)\s*(?:kg|g|gram|pcs?|pieces?|litre?s?|l|ml|dozen|dz|packet|box)?$', re.IGNORECASE)
SIMPLE_NUMBER_PATTERN = re.compile(r'^(\d+(?:\.\d{1,2})?)$')
NAME_PATTERN = re.compile(r'^([a-zA-Z\u0900-\u097F\s]+)$')  # Hindi + English names


def extract_amount_from_followup(text: str) -> Optional[float]:
    """Extract amount/price from a follow-up response."""
    text = text.strip()
    
    # Try simple number first
    match = SIMPLE_NUMBER_PATTERN.match(text)
    if match:
        return float(match.group(1))
    
    # Try amount with currency
    match = AMOUNT_PATTERN.search(text)
    if match:
        return float(match.group(1))
    
    return None


def extract_quantity_from_followup(text: str) -> Optional[float]:
    """Extract quantity from a follow-up response."""
    text = text.strip()
    
    # Try quantity with optional unit
    match = QUANTITY_PATTERN.match(text)
    if match:
        return float(match.group(1))
    
    # Try simple number
    match = SIMPLE_NUMBER_PATTERN.match(text)
    if match:
        return float(match.group(1))
    
    return None


def extract_name_from_followup(text: str) -> Optional[str]:
    """Extract name (customer/supplier/item) from follow-up response."""
    text = text.strip()
    
    # Check if it's a valid name (letters only, no numbers)
    match = NAME_PATTERN.match(text)
    if match:
        return text.title()
    
    # Return as-is if short enough (likely a name)
    if len(text) <= 50 and not any(c.isdigit() for c in text[:5]):
        return text.strip()
    
    return None


def fill_slot(slot_name: str, text: str) -> Optional[any]:
    """Extract value for a specific slot from user response."""
    extractors = {
        "amount": extract_amount_from_followup,
        "price": extract_amount_from_followup,
        "quantity": extract_quantity_from_followup,
        "customer": extract_name_from_followup,
        "supplier": extract_name_from_followup,
        "item": extract_name_from_followup,
    }
    
    extractor = extractors.get(slot_name)
    if extractor:
        return extractor(text)
    
    # Default: return text as-is for unknown slots
    return text.strip() if text.strip() else None


@time_node
def fill_slots(state: AgentState) -> AgentState:
    """
    Fill missing slots from user's follow-up response.
    
    This node is called when:
    1. We previously asked for a missing slot
    2. User responded with a short message (likely the answer)
    
    It extracts the value and updates entities.
    """
    context = state.get("context", {})
    missing_slots = context.get("pending_slots", [])
    messages = state.get("messages", [])
    
    # Restore intent and entities from context (from previous turn)
    if context.get("pending_intent"):
        state["intent"] = context["pending_intent"]
    
    if context.get("pending_entities"):
        entities = context["pending_entities"].copy()
    else:
        entities = state.get("entities", {})
    
    if not missing_slots or not messages:
        return state
    
    # Get the latest user message
    last_message = messages[-1].content if messages else ""
    
    # Get the first missing slot we're waiting for
    current_slot = missing_slots[0]
    
    # Try to extract value
    value = fill_slot(current_slot, last_message)
    
    if value is not None:
        # Update entities with the filled slot
        entries = entities.get("entries", [{}])
        if not entries:
            entries = [{}]
        
        # Map slot names to entity fields
        slot_to_field = {
            "amount": "amount",
            "price": "price", 
            "quantity": "quantity",
            "customer": "customer",
            "supplier": "supplier",
            "item": "item",
        }
        
        field = slot_to_field.get(current_slot, current_slot)
        entries[0][field] = value
        entities["entries"] = entries
        state["entities"] = entities
        
        # Remove filled slot from pending
        remaining_slots = missing_slots[1:]
        context["pending_slots"] = remaining_slots
        context["pending_entities"] = entities  # Save updated entities
        state["context"] = context
        
        # Update state
        state["missing_slots"] = remaining_slots
        state["needs_followup"] = len(remaining_slots) > 0
    
    return state


def is_followup_response(state: AgentState) -> bool:
    """
    Check if current message is a follow-up response to a slot question.
    
    Returns True if:
    - We have pending slots from previous turn
    - The message is short (likely just the answer)
    """
    context = state.get("context", {})
    pending_slots = context.get("pending_slots", [])
    messages = state.get("messages", [])
    
    if not pending_slots:
        return False
    
    if not messages:
        return False
    
    # Get last message
    last_message = messages[-1].content if messages else ""
    
    # Short messages are likely follow-up answers
    # Long messages are likely new requests
    return len(last_message.strip()) < 50
