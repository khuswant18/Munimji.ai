from ..state import AgentState
from decorators.timeit import time_node

REQUIRED_SLOTS = {
    "add_entry": ["item", "quantity", "price"],
    "add_inventory": ["item", "quantity", "price"],  # Generic inventory addition
    "add_sale": ["amount"],  # Relaxed: just need amount
    "add_purchase": ["amount"],  # Relaxed: just need amount
    "add_expense": ["amount"],
    "add_udhaar": ["customer", "amount"],
    "add_payment": ["amount"],
    "add_customer": ["customer"],  # Just need name, amount optional
    # No slots needed for these:
    # greeting, casual_chat, menu_request, query_*, blocked, off_topic
}

# Intents that don't need slot checking
NO_SLOT_CHECK_INTENTS = [
    "greeting", "casual_chat", "menu_request", "blocked", "off_topic", "unknown",
    "menu_add_customer", "menu_add_expense", "menu_show_ledger",
    "menu_show_summary", "menu_udhaar_list", "menu_help",
    "query_summary", "query_ledger", "query_udhaar", "query_customer",
]

@time_node
def check_slots(state: AgentState) -> AgentState:
    intent = state.get("intent", "")
    
    # Skip slot check for intents that don't need it
    if intent in NO_SLOT_CHECK_INTENTS or intent.startswith("menu_") or intent.startswith("query_"):
        state["needs_followup"] = False
        state["missing_slots"] = []
        return state
    
    entities = state.get("entities", {})
    context = state.get("context", {})
    entries = entities.get("entries", [{}])
    if not entries:
        entries = [{}]
    entity = entries[0]  # Assuming first entry

    required = REQUIRED_SLOTS.get(intent, [])
    missing = [slot for slot in required if not entity.get(slot)]

    state["missing_slots"] = missing
    
    if missing:
        state["needs_followup"] = True
        # Save pending slots and intent to context for next turn
        context["pending_slots"] = missing
        context["pending_intent"] = intent
        context["pending_entities"] = entities
        state["context"] = context
    else:
        state["needs_followup"] = False
        # Clear pending state when complete
        context.pop("pending_slots", None)
        context.pop("pending_intent", None)
        context.pop("pending_entities", None)
        state["context"] = context

    return state 