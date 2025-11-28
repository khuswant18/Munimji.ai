from starlette.concurrency import run_in_threadpool
from .utils import send_text_message_async, mark_as_read, send_interactive_list, send_typing_indicator, remove_typing_indicator

try:
    from backend.agents.graph import compiled_graph as chatbot
except Exception:
    chatbot = None


# Interactive menu for WhatsApp
MENU_SECTIONS = [
    {
        "title": "📝 Entry Add Karo",
        "rows": [
            {"id": "menu_add_customer", "title": "Customer/Udhaar", "description": "Naya customer ya udhaar add karo"},
            {"id": "menu_add_expense", "title": "Expense Add", "description": "Petrol, bijli, rent etc."},
        ]
    },
    {
        "title": "📊 Dekhna Hai",
        "rows": [
            {"id": "menu_show_ledger", "title": "Ledger Dikhao", "description": "Aaj ki saari entries"},
            {"id": "menu_show_summary", "title": "Summary", "description": "Total hisab kitab"},
            {"id": "menu_udhaar_list", "title": "Udhaar List", "description": "Kaun kitna dena hai"},
        ]
    },
    {
        "title": "❓ Help",
        "rows": [
            {"id": "menu_help", "title": "Help/Madad", "description": "Kaise use kare"},
        ]
    }
]


async def send_interactive_menu(sender: str, intro_text: str = None):
    """Send interactive menu with clickable options."""
    body = intro_text or "Kya karna hai? Neeche se choose karo ya seedha likh do!"
    try:
        await send_interactive_list(
            to=sender,
            body_text=body,
            button_text="Menu Dekho 📋",
            sections=MENU_SECTIONS,
            header="🙏 Munimji",
            footer="Ya type karo: 'Ramesh ke 500 udhaar'"
        )
    except Exception as e:
        # Fallback to text menu if interactive fails
        print(f"Interactive menu failed, using text: {e}")
        from .utils import send_text_message_async
        await send_text_message_async(sender, get_text_menu(intro_text))


def get_text_menu(intro: str = None) -> str:
    """Fallback text menu."""
    menu = """📋 *Munimji Menu*

Kya karna hai? Number ya option choose karo:

1️⃣ *Naya Customer/Udhaar Add*
2️⃣ *Expense Add*
3️⃣ *Ledger Dikhao*
4️⃣ *Summary*
5️⃣ *Udhaar List*
6️⃣ *Help*

Ya seedha likh do jaise: "Mohan ko 200 ki cheeni bechi\""""
    if intro:
        return f"{intro}\n\n{menu}"
    return menu

async def call_chatbot_and_respond(sender: str, user_text: str, message_id: str = None):
    """
    Runs in background. Calls your chatbot and sends reply back to the WhatsApp user.
    Optimized for speed with typing indicators.
    """
    # Mark message as read immediately (shows blue ticks)
    if message_id:
        await mark_as_read(message_id)
        # Show typing indicator (⏳ reaction on their message)
        await send_typing_indicator(sender, message_id)
    
    if chatbot is None:
        print("chatbot object not found. Make sure backend.chatbot_backend.chatbot is importable.")
        if message_id:
            await remove_typing_indicator(sender, message_id)
        await send_text_message_async(sender, "Sorry — AI backend not available.")
        return

    try:
        from langchain_core.messages import HumanMessage
        from backend.agents.state import AgentState
        from backend.chatbot_backend.db.session import get_db
        from backend.chatbot_backend.db.models import User, Conversation
        
        # Quick DB lookup
        db = next(get_db())
        try:
            user = db.query(User).filter(User.phone_number == sender).first()
            user_id = user.id if user else 1  
            
            conversation = db.query(Conversation).filter(Conversation.user_id == user_id).first()
            previous_context = conversation.context if conversation else {}
        finally:
            db.close()

        # Build messages (keep minimal for speed)
        messages = []
        if previous_context.get("messages"):
            # Only load last 3 messages for context (faster)
            for msg_data in previous_context["messages"][-3:]:
                if isinstance(msg_data, dict):
                    content = msg_data.get("content", str(msg_data))
                    msg_type = msg_data.get("type", "HumanMessage")
                    if msg_type == "HumanMessage":
                        messages.append(HumanMessage(content=content))
                    else:
                        from langchain_core.messages import AIMessage
                        messages.append(AIMessage(content=content))
        
        messages.append(HumanMessage(content=user_text)) 

        initial_state: AgentState = {
            "messages": messages,
            "intent": "",
            "entities": {},
            "context": previous_context.get("context", {}),
            "response": "",
            "user_id": user_id,
            "missing_slots": [],
            "needs_followup": False,
            "route": ""
        } 

        # Run the chatbot
        result = chatbot.invoke(initial_state)
        ai_text = result.get("response", "")
        show_menu = result.get("show_menu", False)
        intent = result.get("intent", "")

        if not ai_text:
            ai_text = "Sorry, I couldn't generate a reply."

        if len(ai_text) > 4096:
            ai_text = ai_text[:4093] + "..."

        # Save context asynchronously (don't block response)
        try:
            db = next(get_db())
            try:
                conversation = db.query(Conversation).filter(Conversation.user_id == user_id).first()
                
                new_context = {
                    "context": result.get("context", {}),
                    "messages": [{"content": m.content, "type": type(m).__name__} for m in result.get("messages", [])[-5:]],
                }
                
                if conversation:
                    conversation.context = new_context
                    conversation.last_message = user_text
                else:
                    conversation = Conversation(
                        user_id=user_id,
                        last_message=user_text,
                        context=new_context
                    )
                    db.add(conversation)
                
                db.commit()
            finally:
                db.close()
        except Exception as ctx_error:
            print(f"Error saving context: {ctx_error}")

        # Remove typing indicator before sending response
        if message_id:
            await remove_typing_indicator(sender, message_id)

        # Send response - use interactive menu for greeting/menu intents
        if intent in ["greeting", "menu_request", "casual_chat"] or show_menu:
            # Extract intro text (before the menu part)
            intro = ai_text.split("📋")[0].strip() if "📋" in ai_text else ai_text
            if intro and len(intro) > 10:
                await send_interactive_menu(sender, intro)
            else:
                await send_interactive_menu(sender)
        else:
            await send_text_message_async(sender, ai_text)

    except Exception as e:
        print(f"Error calling chatbot or sending response: {e}")
        import traceback
        traceback.print_exc()
        # Remove typing indicator on error
        if message_id:
            try:
                await remove_typing_indicator(sender, message_id)
            except:
                pass
        try:
            await send_text_message_async(sender, "Sorry, something went wrong. Try again!")
        except Exception as send_error:
            print(f"Failed to send error message: {send_error}")