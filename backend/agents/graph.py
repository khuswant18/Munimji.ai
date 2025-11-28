from langgraph.graph import StateGraph, START, END
from .state import AgentState
from .nodes.classify import classify_intent
from .nodes.extract import extract_entities
from .nodes.slot_check import check_slots
from .nodes.slot_fill import fill_slots, is_followup_response
from .nodes.router import route_request
from .nodes.add_entry import add_entry
from .nodes.search_notes import search_notes
from .nodes.respond import generate_response


def route_from_start(state: AgentState) -> str:
    """
    Route from START based on whether this is a follow-up response.
    
    - If we have pending slots and short message → slot_fill
    - Otherwise → classify (new request)
    """
    if is_followup_response(state):
        return "slot_fill"
    return "classify"


def route_after_slot_check(state: AgentState) -> str:
    """
    Route after slot_check based on whether slots are complete.
    
    - If needs_followup (missing slots) → respond (ask for missing)
    - Otherwise → router (proceed with action)
    """
    if state.get("needs_followup", False):
        return "respond"
    return "router"


graph = StateGraph(AgentState)

# Add all nodes
graph.add_node("classify", classify_intent)
graph.add_node("extract", extract_entities)
graph.add_node("slot_check", check_slots)
graph.add_node("slot_fill", fill_slots)
graph.add_node("router", route_request)
graph.add_node("add_entry", add_entry)
graph.add_node("search_notes", search_notes)
graph.add_node("respond", generate_response)

# Conditional edge from START - check if follow-up or new request
graph.add_conditional_edges(
    START,
    route_from_start,
    {
        "slot_fill": "slot_fill",
        "classify": "classify",
    }
)

# Normal flow: classify → extract → slot_check
graph.add_edge("classify", "extract")
graph.add_edge("extract", "slot_check")

# After slot_check: either ask for missing slots or proceed
graph.add_conditional_edges(
    "slot_check",
    route_after_slot_check,
    {
        "respond": "respond",  # Ask for missing slots
        "router": "router",     # Proceed to action
    }
)

# slot_fill → slot_check (re-check if all slots filled)
graph.add_edge("slot_fill", "slot_check")

# Router conditional edges
graph.add_conditional_edges( 
    "router",
    lambda state: state["route"],
    {
        "add_entry": "add_entry",
        "search": "search_notes",
        "respond": "respond",
    }
)

# Action nodes → respond
graph.add_edge("add_entry", "respond")
graph.add_edge("search_notes", "respond")
graph.add_edge("respond", END)


compiled_graph = graph.compile() 

