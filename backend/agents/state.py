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
    # New fields for interactive menu
    show_menu: bool  # Whether to show menu after response
    is_blocked: bool  # Whether content was blocked
    menu_state: str  # Current menu state: 'main', 'add_customer', etc.
    conversation_mode: str  # 'greeting', 'menu', 'action', 'followup' 