from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    intent: str
    intent_confidence: float
    intent_reason: str
    entities: dict
    context: dict
    response: str
    user_id: int
    missing_slots: List[str]
    needs_followup: bool
    route: str
    show_menu: bool
    is_blocked: bool 
    menu_state: str  
    conversation_mode: str  