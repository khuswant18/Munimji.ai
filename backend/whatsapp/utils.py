import hmac
import hashlib
import logging
import httpx
import aiofiles
from pathlib import Path
from typing import Optional
from .config import APP_SECRET, ACCESS_TOKEN, GRAPH_API_BASE, DOWNLOAD_DIR, PHONE_NUMBER_ID

LOG = logging.getLogger("munimji.whatsapp_adapter")


def verify_signature(raw_body: bytes, signature_header: Optional[str]) -> bool:
    if not APP_SECRET:
        LOG.warning("APP_SECRET not set; skipping signature verification (dev only)")
        return True
    if not signature_header:
        return False
    prefix = "sha256="
    if not signature_header.startswith(prefix):
        return False
    received = signature_header[len(prefix):]
    computed = hmac.new(APP_SECRET.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, received)


async def fetch_media_url(media_id: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{GRAPH_API_BASE}/{media_id}", params={"access_token": ACCESS_TOKEN}, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        url = data.get("url")
        if not url:
            raise RuntimeError("Media URL not provided by Graph API")
        return url

async def download_media_to_disk(media_id: str, sender: str, mime_hint: Optional[str] = None) -> str:
    media_url = await fetch_media_url(media_id)
    async with httpx.AsyncClient() as client:
        resp = await client.get(media_url, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}, timeout=60.0)
        resp.raise_for_status()
        content_type = (resp.headers.get("Content-Type") or mime_hint or "").lower()
        ext = guess_ext_from_content_type(content_type) or "bin"
        fname = f"{media_id}_{sender}.{ext}"
        out_path = DOWNLOAD_DIR / fname
        async with aiofiles.open(out_path, "wb") as f:
            await f.write(resp.content)
    LOG.info("Saved media to %s", out_path)
    return str(out_path)

def guess_ext_from_content_type(content_type: str) -> Optional[str]:
    ct = (content_type or "").lower()
    if "jpeg" in ct or "jpg" in ct:
        return "jpg"
    if "png" in ct:
        return "png"
    if "gif" in ct:
        return "gif"
    if "webp" in ct:
        return "webp"
    if "pdf" in ct:
        return "pdf"
    if "ogg" in ct:
        return "ogg"
    if "mpeg" in ct or "mp3" in ct or "audio" in ct:
        return "mp3"
    if "mp4" in ct or "video" in ct:
        return "mp4"
    return None


async def send_text_message_async(to: str, text: str) -> dict:
    url = f"{GRAPH_API_BASE}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    LOG.info(f"Sending message to {to}: {text[:100]}...")
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=20.0)
        LOG.info(f"WhatsApp API response: {resp.status_code} - {resp.text}")
        resp.raise_for_status()
        return resp.json()


async def send_typing_indicator(to: str, message_id: str) -> dict:
    """
    Send a reaction emoji to indicate bot is processing/typing.
    Shows ⏳ on the user's message while we process.
    """
    if not message_id:
        return {}
    
    url = f"{GRAPH_API_BASE}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "reaction",
        "reaction": {
            "message_id": message_id,
            "emoji": "⏳"  # Hourglass to show processing
        }
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=5.0)
            LOG.info(f"Typing indicator sent: {resp.status_code}")
            return resp.json()
    except Exception as e:
        LOG.warning(f"Failed to send typing indicator: {e}")
        return {}


async def remove_typing_indicator(to: str, message_id: str) -> dict:
    """
    Remove the typing reaction by sending empty emoji.
    """
    if not message_id:
        return {}
    
    url = f"{GRAPH_API_BASE}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "reaction",
        "reaction": {
            "message_id": message_id,
            "emoji": ""  # Empty emoji removes the reaction
        }
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=5.0)
            return resp.json()
    except Exception as e:
        LOG.warning(f"Failed to remove typing indicator: {e}")
        return {}


async def mark_as_read(message_id: str) -> dict:
    """Mark message as read to show blue ticks."""
    url = f"{GRAPH_API_BASE}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=5.0)
            return resp.json()
    except Exception as e:
        LOG.warning(f"Failed to mark as read: {e}")
        return {}


async def send_interactive_buttons(to: str, body_text: str, buttons: list, header: str = None, footer: str = None) -> dict:
    """
    Send interactive button message.
    
    Args:
        to: Recipient phone number
        body_text: Main message body
        buttons: List of dicts with 'id' and 'title' (max 3 buttons, title max 20 chars)
        header: Optional header text
        footer: Optional footer text
    """
    url = f"{GRAPH_API_BASE}/{PHONE_NUMBER_ID}/messages"
    
    # Build button rows (max 3 buttons)
    button_rows = []
    for btn in buttons[:3]:  # WhatsApp limits to 3 buttons
        button_rows.append({
            "type": "reply",
            "reply": {
                "id": btn["id"],
                "title": btn["title"][:20]  # Max 20 chars
            }
        })
    
    interactive = {
        "type": "button",
        "body": {"text": body_text},
        "action": {"buttons": button_rows}
    }
    
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": interactive
    }
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    LOG.info(f"Sending interactive buttons to {to}")
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=20.0)
        LOG.info(f"Interactive API response: {resp.status_code} - {resp.text}")
        resp.raise_for_status()
        return resp.json()


async def send_interactive_list(to: str, body_text: str, button_text: str, sections: list, header: str = None, footer: str = None) -> dict:
    """
    Send interactive list message (for more than 3 options).
    
    Args:
        to: Recipient phone number
        body_text: Main message body
        button_text: Text on the list button (max 20 chars)
        sections: List of section dicts with 'title' and 'rows'
        header: Optional header text
        footer: Optional footer text
    """
    url = f"{GRAPH_API_BASE}/{PHONE_NUMBER_ID}/messages"
    
    interactive = {
        "type": "list",
        "body": {"text": body_text},
        "action": {
            "button": button_text[:20],
            "sections": sections
        }
    }
    
    if header:
        interactive["header"] = {"type": "text", "text": header}
    if footer:
        interactive["footer"] = {"text": footer}
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "interactive",
        "interactive": interactive
    }
    
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    LOG.info(f"Sending interactive list to {to}")
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, headers=headers, timeout=20.0)
        LOG.info(f"Interactive list API response: {resp.status_code} - {resp.text}")
        resp.raise_for_status()
        return resp.json()