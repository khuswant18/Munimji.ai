from fastapi import Request, BackgroundTasks, HTTPException, Header
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from .utils import send_text_message_async, verify_signature, mark_as_read, send_interactive_buttons
from .media import process_downloaded_image, process_downloaded_audio, process_downloaded_video, process_invoice_confirmation, get_pending_invoice
from .chatbot import call_chatbot_and_respond, send_interactive_menu
from backend.chatbot_backend.db.session import SessionLocal
from backend.chatbot_backend.db.models import User, Conversation
from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
import os
import time

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Simple in-memory cache for message deduplication (prevents processing same message twice)
# WhatsApp can send duplicate webhooks
_processed_messages = {}
_CACHE_TTL = 60  # seconds

def _is_duplicate_message(message_id: str) -> bool:
    """Check if message was already processed (deduplication)."""
    if not message_id:
        return False
    
    now = time.time()
    
    # Clean old entries
    expired = [k for k, v in _processed_messages.items() if now - v > _CACHE_TTL]
    for k in expired:
        del _processed_messages[k]
    
    # Check if already processed
    if message_id in _processed_messages:
        print(f"Duplicate message ignored: {message_id}")
        return True
    
    # Mark as processed
    _processed_messages[message_id] = now
    return False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def webhook_verify(
    hub_mode,
    hub_verify_token,
    hub_challenge
):
    if hub_mode == "subscribe" and hub_verify_token:
        from .config import WEBHOOK_VERIFY_TOKEN
        if hub_verify_token == WEBHOOK_VERIFY_TOKEN:
            print("Webhook verified")
            return PlainTextResponse(content=hub_challenge or "", status_code=200)
        else:
            print("Invalid verify token")
            raise HTTPException(status_code=403, detail="Forbidden")
    raise HTTPException(status_code=404, detail="Not Found")

async def webhook_receiver(request: Request, background_tasks: BackgroundTasks, x_hub_signature_256, db: Session):
    raw_body = await request.body()
    if not verify_signature(raw_body, x_hub_signature_256):
        print("Invalid signature")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        body = await request.json() 
    except Exception: 
        print("Invalid JSON") 
        raise HTTPException(status_code=400, detail="Invalid JSON") 

    if body.get("object") and body.get("entry"):
        for entry in body.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {}) or {}
                contacts = value.get("contacts", []) or []
                messages = value.get("messages", []) or []
                for message in messages:
                    sender = message.get("from")
                    mtype = message.get("type")
                    message_id = message.get("id")  # Get message ID for read receipts
                    print(f"Incoming message from={sender} type={mtype} id={message_id}")

                    # Skip duplicate messages (WhatsApp can send same webhook multiple times)
                    if _is_duplicate_message(message_id):
                        continue

                    user = db.query(User).filter(User.phone_number == sender).first()
                    if not user:
                        user = User(phone_number=sender)
                        db.add(user)
                        db.commit()
                        db.refresh(user)

                    # Handle interactive button/list responses
                    if mtype == "interactive":
                        interactive = message.get("interactive", {})
                        interactive_type = interactive.get("type")
                        
                        if interactive_type == "button_reply":
                            # Button click response
                            button_reply = interactive.get("button_reply", {})
                            text = button_reply.get("id", "")  # e.g., "menu_add_customer"
                            print(f"Button clicked: {text}")
                        elif interactive_type == "list_reply":
                            # List selection response
                            list_reply = interactive.get("list_reply", {})
                            text = list_reply.get("id", "")  # e.g., "menu_add_expense"
                            print(f"List item selected: {text}")
                        else:
                            text = ""
                        
                        if text:
                            # Update existing conversation or create new one
                            conv = db.query(Conversation).filter(Conversation.user_id == user.id).first()
                            if conv:
                                conv.last_message = text
                                # Preserve existing context, just add interaction type marker
                                if isinstance(conv.context, dict):
                                    conv.context["last_interaction_type"] = "interactive"
                            else:
                                conv = Conversation(user_id=user.id, last_message=text, context={"type": "interactive"})
                                db.add(conv)
                            db.commit()
                            
                            # Handle invoice confirmation buttons
                            if text in ["invoice_confirm", "confirm_yes"]:
                                if get_pending_invoice(sender):
                                    background_tasks.add_task(process_invoice_confirmation, sender, True)
                                    continue
                            elif text in ["invoice_cancel", "confirm_no"]:
                                if get_pending_invoice(sender):
                                    background_tasks.add_task(process_invoice_confirmation, sender, False)
                                    continue
                            elif text == "retry_image":
                                await send_text_message_async(sender, "📷 Theek hai! Apni photo dobara bhejo.")
                                continue
                            
                            # Handle category selection buttons
                            category_mapping = {
                                "cat_sale": "sale",
                                "cat_purchase": "purchase", 
                                "cat_expense": "expense",
                                "cat_udhaar": "udhaar"
                            }
                            if text in category_mapping:
                                # Map button ID to category and pass to chatbot
                                category = category_mapping[text]
                                background_tasks.add_task(call_chatbot_and_respond, sender, category, message_id)
                                continue
                            
                            background_tasks.add_task(call_chatbot_and_respond, sender, text, message_id)
                        continue

                    if mtype == "text":
                        text = (message.get("text") or {}).get("body", "").strip()
                        text_lower = text.lower()

                        # Update existing conversation instead of creating new (preserves context)
                        conv = db.query(Conversation).filter(Conversation.user_id == user.id).first()
                        if conv:
                            conv.last_message = text
                            # Preserve existing context, just add interaction type marker
                            if isinstance(conv.context, dict):
                                conv.context["last_interaction_type"] = "text"
                        else:
                            conv = Conversation(user_id=user.id, last_message=text, context={"type": "text"})
                            db.add(conv)
                        db.commit()

                        # Check for pending invoice confirmation first
                        if get_pending_invoice(sender):
                            # Check if user is confirming or cancelling
                            if text_lower in ["haan", "ha", "yes", "confirm", "add", "ok", "theek hai", "theek", "kar do", "✅"]:
                                background_tasks.add_task(process_invoice_confirmation, sender, True)
                                continue
                            elif text_lower in ["nahi", "na", "no", "cancel", "nhi", "mat karo", "❌"]:
                                background_tasks.add_task(process_invoice_confirmation, sender, False)
                                continue

                        # Skip vector store for speed on simple messages
                        # Only embed for longer, meaningful messages
                        if len(text) > 20:
                            try:
                                vector_store = PGVector(
                                    connection=os.getenv("DATABASE_URL"),
                                    embeddings=embeddings,
                                    collection_name="message_embeddings",
                                    use_jsonb=True
                                )
                                vector_store.add_texts([text], metadatas=[{"user_id": user.id, "key": "message"}])
                            except Exception as vec_err:
                                print(f"Vector store error (non-blocking): {vec_err}")


                        if user.state == "new" and text_lower == "hi":
                            user.state = "onboarding_name"
                            db.commit()
                            await send_text_message_async(sender, "🙏 Welcome to MunimJi!\n\nAapka naam kya hai?")
                        elif user.state == "onboarding_name":
                            user.name = text.title()
                            user.state = "onboarding_shop"
                            db.commit()
                            await send_text_message_async(sender, f"Namaste {user.name}! 🙏\n\nAapki dukaan ka naam kya hai?")
                        elif user.state == "onboarding_shop":
                            user.shop_name = text.title()
                            user.state = "menu"
                            db.commit()
                            # Send welcome with interactive menu
                            welcome_msg = f"🎉 Shandar! '{user.shop_name}' register ho gayi!\n\n{user.name}, ab main aapka hisab-kitab rakh sakta hoon."
                            await send_interactive_menu(sender, welcome_msg)
                        elif user.state == "menu":
                            background_tasks.add_task(call_chatbot_and_respond, sender, text, message_id)
                        else:
                            background_tasks.add_task(call_chatbot_and_respond, sender, text, message_id)

                    elif mtype == "image":
                        media_obj = message.get("image", {}) or {}
                        media_id = media_obj.get("id")
                        mime = media_obj.get("mime_type")
                        background_tasks.add_task(process_downloaded_image, media_id, sender, mime)

                        conv = Conversation(user_id=user.id, last_message=f"Image: {media_id}", context={"type": mtype, "media_id": media_id})
                        db.add(conv)
                        db.commit()

                    elif mtype == "audio":
                        media_obj = message.get("audio", {}) or {}
                        media_id = media_obj.get("id")
                        mime = media_obj.get("mime_type")
                        background_tasks.add_task(process_downloaded_audio, media_id, sender, mime)
                        conv = Conversation(user_id=user.id, last_message=f"Audio: {media_id}", context={"type": mtype, "media_id": media_id})
                        db.add(conv)
                        db.commit()

                    elif mtype == "video":
                        media_obj = message.get("video", {}) or {}
                        media_id = media_obj.get("id")
                        mime = media_obj.get("mime_type")
                        background_tasks.add_task(process_downloaded_video, media_id, sender, mime)
                        conv = Conversation(user_id=user.id, last_message=f"Video: {media_id}", context={"type": mtype, "media_id": media_id})
                        db.add(conv)
                        db.commit()

                    elif mtype == "document":
                        media_obj = message.get("document", {}) or {}
                        media_id = media_obj.get("id")
                        mime = media_obj.get("mime_type")

                        background_tasks.add_task(process_downloaded_image, media_id, sender, mime)
                        conv = Conversation(user_id=user.id, last_message=f"Document: {media_id}", context={"type": mtype, "media_id": media_id})
                        db.add(conv)
                        db.commit()

                    elif mtype == "sticker":

                        pass

                    else:
                        await send_text_message_async(sender, "Sorry, I don't support this message type yet.")

        return JSONResponse({"status": "EVENT_RECEIVED"}, status_code=200)

    return JSONResponse({"status": "ignored"}, status_code=200)

class SendTextBody(BaseModel):
    to: str
    text: str

async def send_text_demo(body: SendTextBody):
    if not body.to:
        raise HTTPException(status_code=400, detail="missing 'to'")
    return await send_text_message_async(body.to, body.text)