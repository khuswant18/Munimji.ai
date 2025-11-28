"""
Optimized response generation with template-based fast paths.

Optimizations:
- Template responses for common successful operations (no LLM needed)
- LLM only used for complex conversations and clarifications
- Shorter prompts for faster LLM responses
- Interactive menu support
"""
from ..state import AgentState
from ...llm.groq_client import groq_chat
from ...llm.prompts import RESPONSE_PROMPT
from ...decorators.timeit import time_node
from .guardrails import get_blocked_response, get_off_topic_response, get_main_menu

# Template responses for successful operations (avoid LLM call)
SUCCESS_TEMPLATES = {
    "add_expense": "✅ Done! ₹{amount} expense add ho gaya. {description}",
    "add_sale": "✅ Done! ₹{amount} ki sale record ho gayi. {description}",
    "add_purchase": "✅ Done! ₹{amount} ka purchase add ho gaya. {description}",
    "add_udhaar": "✅ Done! {customer} ke naam ₹{amount} udhaar likh diya.",
    "add_payment": "✅ Done! ₹{amount} payment record ho gaya. {description}",
    "add_entry": "✅ Added: {quantity} {item} @ ₹{price}",
    "add_inventory": "✅ Added: {quantity} {item} @ ₹{price}",
    "add_customer": "✅ {customer} add ho gaya! Ab unka hisab rakh sakte ho.",
}

# Greeting responses (rotate for variety)
GREETING_RESPONSES = [
    "Namaste! 🙏 Main Munimji hoon, aapka dukaan assistant. Kaise madad karun?",
    "Hello! 🙏 Dukaan me kya madad karun?",
    "Namaskar! Main aapke hisab-kitab mein madad karne ke liye hoon. Bataiye?",
]

# Template for missing slot follow-ups (Hindi/Hinglish)
FOLLOWUP_TEMPLATES = {
    "amount": "💰 Kitne ka hai? Amount batao.",
    "price": "💵 {item} ki price kitni rakhu?",
    "quantity": "📦 Kitne {item}?",
    "customer": "👤 Customer ka naam batao.",
    "supplier": "🏪 Supplier ka naam batao.",
    "item": "📝 Kya item hai?",
    "name": "👤 Naam batao.",
}

# Casual chat responses
CASUAL_RESPONSES = {
    "thanks": "🙏 Aapka swagat hai! Aur kuch madad chahiye?",
    "bye": "👋 Alvida! Phir milenge. Apna khayal rakhna!",
    "ok": "👍 Theek hai! Aur kuch karna hai?",
    "how_are": "Main bilkul theek hoon! 😊 Aapka kya haal hai? Dukaan kaisi chal rahi hai?",
    "default": "Ji bilkul! Aur kuch madad chahiye?",
}

# Menu option responses
MENU_RESPONSES = {
    "menu_add_customer": "👤 *Naya Customer/Udhaar Add*\n\nSeedha type karo:\n• \"Ramesh ke 500 udhaar\"\n• \"Mohan ka 1000 baaki\"\n\nYa sirf naam batao, main amount baad mein puch lunga.",
    "menu_add_expense": "💸 *Expense Add*\n\nSeedha type karo:\n• \"100 ka petrol\"\n• \"500 bijli bill\"\n• \"200 chai nashta\"\n\nYa sirf amount batao.",
    "menu_show_ledger": "📒 *Ledger Dikhao*\n\nAaj ki entries dekhne ke liye \"aaj ka ledger\" likho.\n\nSpecific customer ka hisab: \"Ramesh ka hisab dikhao\"",
    "menu_show_summary": "📊 *Summary*\n\n\"Aaj ka summary\" ya \"is hafte ka summary\" likho.\n\nTotal sale, purchase, expense sab dikha dunga.",
    "menu_udhaar_list": "📋 *Udhaar List*\n\n\"Udhaar list dikhao\" ya \"kaun kitna dena hai\" likho.\n\nSaare pending udhaar dikha dunga.",
    "menu_help": """❓ *Help - Kaise Use Kare*

📝 *Entry Add Karna:*
• \"Ramesh ke 500 udhaar\" - Udhaar add
• \"100 ka petrol\" - Expense add  
• \"5 pen @ 10\" - Item add

📊 *Dekhna:*
• \"Aaj ka hisab\" - Today's summary
• \"Ledger dikhao\" - All entries
• \"Kaun kitna dena\" - Udhaar list

💡 Seedha Hindi mein likho, samajh jaunga!""",
}


def _format_template(template: str, entities: dict, context: dict) -> str:
    """Format template with available values."""
    entry = {}
    if entities and entities.get("entries"):
        entry = entities["entries"][0]
    
    values = {
        "amount": entry.get("amount", context.get("total_amount", "?")),
        "customer": entry.get("customer", "customer"),
        "supplier": entry.get("supplier", "supplier"),
        "item": entry.get("item", "item"),
        "description": entry.get("description", context.get("description", "")),
        "entries_count": context.get("entries_count", 1),
    }
    
    try:
        return template.format(**values)
    except:
        return template


def _generate_followup_response(missing_slots: list, entities: dict = None) -> str:
    """Generate follow-up question for missing slots with context."""
    if not missing_slots:
        return ""
    
    # Get first missing slot
    slot = missing_slots[0]
    template = FOLLOWUP_TEMPLATES.get(slot, f"Please provide {slot}.")
    
    # Get item name for context
    item = "item"
    if entities and entities.get("entries"):
        item = entities["entries"][0].get("item", "item")
    
    try:
        return template.format(item=item)
    except:
        return template


@time_node
def generate_response(state: AgentState) -> AgentState:
    """
    Generate response with template fast path and menu support.
    """
    intent = state.get("intent", "unknown")
    entities = state.get("entities", {})
    context = state.get("context", {})
    missing_slots = state.get("missing_slots", [])
    needs_followup = state.get("needs_followup", False)
    show_menu = state.get("show_menu", False)
    
    # 0. Handle blocked content
    if state.get("is_blocked") or intent == "blocked":
        state["response"] = get_blocked_response()
        return state
    
    # 1. Handle menu selection
    if intent.startswith("menu_"):
        response = MENU_RESPONSES.get(intent, get_main_menu())
        state["response"] = response
        return state
    
    # 2. Handle menu request
    if intent == "menu_request":
        state["response"] = get_main_menu()
        return state
    
    # 2.5 Handle profile queries (name, shop, account info)
    if intent == "query_profile":
        user_id = state.get("user_id")
        if user_id:
            try:
                from ...chatbot_backend.db.session import get_db
                from ...chatbot_backend.db.models import User
                db = next(get_db())
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        # Build profile response
                        name = user.name or "abhi set nahi hai"
                        shop_name = user.shop_name or "abhi set nahi hai"
                        
                        # Check what specifically was asked
                        messages = state.get("messages", [])
                        last_message = ""
                        if messages:
                            last_msg = messages[-1]
                            last_message = (last_msg.content if hasattr(last_msg, "content") else str(last_msg)).lower()
                        
                        if any(w in last_message for w in ["naam", "name", "kaun", "who"]):
                            if user.name:
                                response = f"🙏 Aapka naam *{user.name}* hai!"
                            else:
                                response = "🤔 Aapka naam abhi mere paas nahi hai. Apna naam batao toh save kar lunga!"
                        elif any(w in last_message for w in ["dukaan", "shop"]):
                            if user.shop_name:
                                response = f"🏪 Aapki dukaan ka naam *{user.shop_name}* hai!"
                            else:
                                response = "🤔 Dukaan ka naam abhi set nahi hai. Batao toh save kar lunga!"
                        else:
                            # Full profile
                            response = f"""👤 *Aapki Profile:*

🙏 Naam: *{name}*
🏪 Dukaan: *{shop_name}*
📱 Number: {user.phone_number}

Kuch update karna hai toh batao!"""
                        
                        state["response"] = response
                        return state
                finally:
                    db.close()
            except Exception as e:
                print(f"Error fetching user profile: {e}")
        
        # Fallback if user not found
        state["response"] = "🤔 Aapki profile abhi nahi mili. Pehle apna naam aur dukaan ka naam batao!"
        return state
    
    # 3. Handle casual chat
    if intent == "casual_chat":
        messages = state.get("messages", [])
        last_message = ""
        if messages:
            last_msg = messages[-1]
            last_message = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
        
        last_lower = last_message.lower()
        if any(w in last_lower for w in ["thank", "shukriya", "dhanyavad"]):
            response = CASUAL_RESPONSES["thanks"]
        elif any(w in last_lower for w in ["bye", "alvida", "tata"]):
            response = CASUAL_RESPONSES["bye"]
        elif any(w in last_lower for w in ["ok", "okay", "theek", "accha", "sahi"]):
            response = CASUAL_RESPONSES["ok"]
        elif any(w in last_lower for w in ["kaise", "kaisa", "how are", "kya haal"]):
            response = CASUAL_RESPONSES["how_are"]
        else:
            response = CASUAL_RESPONSES["default"]
        
        # Set flag to show interactive menu (don't append text menu)
        state["show_menu"] = True
        state["response"] = response
        return state
    
    # 4. Handle follow-up needed (missing slots)
    if needs_followup and missing_slots:
        response = _generate_followup_response(missing_slots, entities)
        state["response"] = response
        return state
    
    # 5. Handle errors
    if context.get("error"):
        state["response"] = f"❌ Oops! Kuch gadbad ho gayi: {context['error']}\n\nDubara try karo ya 'menu' likho."
        return state
    
    # 6. Template response for successful operations
    if context.get("added") and intent in SUCCESS_TEMPLATES:
        response = _format_template(SUCCESS_TEMPLATES[intent], entities, context)
        # Add follow-up prompt after successful action
        response += "\n\n✨ Aur kuch karna hai? 'menu' likho ya seedha next entry karo!"
        state["response"] = response
        return state
    
    # 7. Template for greetings - show interactive menu
    if intent == "greeting":
        import random
        response = random.choice(GREETING_RESPONSES)
        # Set flag for interactive menu (don't append text menu)
        state["show_menu"] = True
        state["response"] = response
        return state
    
    # 8. Simple response for queries with search results
    if intent.startswith("query_") and context.get("search_results"):
        response = context["search_results"]
        response += "\n\n📌 Aur kuch dekhna hai? 'menu' likho."
        state["response"] = response
        return state
    
    # 9. Handle off-topic/unknown
    if intent in ["unknown", "off_topic"]:
        state["response"] = get_off_topic_response()
        return state
    
    # 10. LLM fallback for complex cases
    messages = state.get("messages", [])
    last_message = ""
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "content"):
            last_message = last_msg.content
        elif isinstance(last_msg, dict):
            last_message = last_msg.get("content", str(last_msg))
    
    # Compact prompt - shopkeeper context
    prompt = f"""You are Munimji, a helpful shopkeeper assistant. 
Respond in Hindi/English mix (Hinglish). Be brief and friendly.
Only help with shop/business tasks.

User: "{last_message}"
Intent: {intent}
Data: {entities}

Generate a helpful response. If unsure, offer to show menu."""

    response = groq_chat(prompt, temperature=0, max_tokens=150)
    
    if not response:
        response = "Samajh nahi aaya. 'menu' likho options dekhne ke liye."
    
    # Add menu prompt if show_menu flag is set
    if show_menu:
        response += "\n\n" + get_main_menu()
    
    state["response"] = response
    return state 