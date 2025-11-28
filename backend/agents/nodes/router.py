from ..state import AgentState
from ...decorators.timeit import time_node

@time_node
def route_request(state: AgentState) -> AgentState:
    intent = state.get("intent", "unknown")
    needs_followup = state.get("needs_followup", False)

    # Menu items that need to fetch data from DB (route to search)
    menu_query_intents = [
        "menu_show_ledger", "menu_show_summary", "menu_udhaar_list"
    ]
    
    # Direct to respond for these intents (no DB action needed)
    respond_intents = [
        "greeting", "casual_chat", "menu_request", "blocked", "off_topic", "unknown",
        "menu_add_customer", "menu_add_expense", "menu_help",
        "query_profile"  # Profile queries handled directly in respond
    ]
    
    if needs_followup:
        state["route"] = "respond"
    elif intent in menu_query_intents:
        # Menu items that show data - route to search
        state["route"] = "search"
    elif intent in respond_intents:
        state["route"] = "respond"
    elif intent.startswith("add_") or intent in ["inventory_update", "add_inventory"]:
        state["route"] = "add_entry"
    elif intent.startswith("query_"):
        state["route"] = "search"
    else:
        state["route"] = "respond"
    return state