from .utils import send_text_message_async, download_media_to_disk, send_confirmation_buttons, send_success_with_menu
from .audio_processor import transcribe_audio
from .image_processor import extract_image_data, extract_invoice_data, format_invoice_for_display, parse_extracted_to_command
from .chatbot import call_chatbot_and_respond
from typing import Optional
import logging
import json

LOG = logging.getLogger(__name__)

# Store pending invoice confirmations (phone -> invoice_data)
_pending_invoices = {}


def store_pending_invoice(phone: str, invoice_data: dict):
    """Store invoice data pending user confirmation."""
    _pending_invoices[phone] = invoice_data


def get_pending_invoice(phone: str) -> Optional[dict]:
    """Get pending invoice for user."""
    return _pending_invoices.get(phone)


def clear_pending_invoice(phone: str):
    """Clear pending invoice after confirmation/cancellation."""
    if phone in _pending_invoices:
        del _pending_invoices[phone]


async def process_invoice_confirmation(sender: str, confirmed: bool) -> bool:
    """
    Process invoice confirmation response.
    Returns True if there was a pending invoice to process.
    """
    invoice_data = get_pending_invoice(sender)
    if not invoice_data:
        return False
    
    clear_pending_invoice(sender)
    
    if confirmed:
        # Add as purchase record
        supplier = invoice_data.get("supplier", "Unknown Supplier")
        total = invoice_data.get("total_amount", 0)
        invoice_num = invoice_data.get("invoice_number", "")
        date = invoice_data.get("date", "")
        
        # Create a purchase command for the chatbot
        items_summary = ""
        if invoice_data.get("items"):
            items_count = len(invoice_data["items"])
            items_summary = f" ({items_count} items)"
        
        # Format as purchase record command
        purchase_cmd = f"Purchase: {supplier} se ₹{total} ka bill{items_summary}"
        if invoice_num:
            purchase_cmd += f" (Invoice #{invoice_num})"
        if date:
            purchase_cmd += f" dated {date}"
        
        LOG.info(f"Adding purchase from invoice: {purchase_cmd}")
        
        # Send success with interactive menu buttons
        success_text = (
            f"✅ *Purchase Added!*\n\n"
            f"🏢 Supplier: {supplier}\n"
            f"💰 Amount: ₹{total}\n"
            f"📦 Items: {len(invoice_data.get('items', []))}\n"
            f"🔢 Invoice: {invoice_num or 'N/A'}\n\n"
            f"Record saved successfully! 📝"
        )
        
        try:
            await send_success_with_menu(sender, success_text)
        except Exception as e:
            LOG.warning(f"Interactive buttons failed, using text: {e}")
            await send_text_message_async(sender, success_text + "\n\n'menu' likho aur options ke liye.")
        
        # Process through chatbot to actually save
        await call_chatbot_and_respond(sender, purchase_cmd)
        
    else:
        # Send cancel message with menu options
        try:
            from .utils import send_interactive_buttons
            buttons = [
                {"id": "menu_request", "title": "📋 Menu"},
                {"id": "retry_image", "title": "📷 Retry Photo"}
            ]
            await send_interactive_buttons(
                sender,
                "❌ Invoice cancelled.\n\nDubara photo bhejo ya menu se option choose karo.",
                buttons
            )
        except Exception as e:
            LOG.warning(f"Interactive buttons failed: {e}")
            await send_text_message_async(sender, "❌ Invoice cancelled. Photo dubara bhejo ya 'menu' likho.")
    
    return True


async def process_image_and_respond(sender: str, file_path: str):
    """
    Process image: extract text using OCR, then pass to chatbot for processing.
    This allows shopkeepers to send photos of handwritten notes, bills, etc.
    """
    try:
        # Extract text from image
        await send_text_message_async(sender, "📷 Image mila... padh raha hoon...")
        
        # First try to extract as invoice (structured data)
        invoice_data = await extract_invoice_data(file_path)
        
        if invoice_data and invoice_data.get("total_amount"):
            # This looks like an invoice - show details and ask for confirmation with buttons
            display_text = format_invoice_for_display(invoice_data)
            
            if display_text:
                # Send invoice details with confirmation buttons
                try:
                    await send_confirmation_buttons(
                        sender,
                        display_text,
                        confirm_id="invoice_confirm",
                        cancel_id="invoice_cancel",
                        header="📋 Invoice Detected!"
                    )
                except Exception as e:
                    LOG.warning(f"Confirmation buttons failed, using text: {e}")
                    await send_text_message_async(sender, display_text + "\n\n✅ 'haan' - Add | ❌ 'nahi' - Cancel")
                
                store_pending_invoice(sender, invoice_data)
                return
        
        # Fallback to regular text extraction
        extracted_text = await extract_image_data(file_path)
        
        if not extracted_text or len(extracted_text.strip()) < 3:
            await send_text_message_async(
                sender, 
                "❌ Image se text nahi padh paya. Please clear photo bhejo ya text mein likho."
            )
            return
        
        # Show what was extracted
        preview = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        await send_text_message_async(sender, f"📝 Yeh padha image se:\n\n{preview}")
        
        # Parse to command and process through chatbot
        command = parse_extracted_to_command(extracted_text)
        LOG.info(f"Image extracted -> command: {command}")
        
        # Process the extracted text through chatbot
        await call_chatbot_and_respond(sender, command)
        
    except Exception as e:
        LOG.exception(f"Error processing image: {e}")
        await send_text_message_async(
            sender, 
            "❌ Image process nahi ho paya. Please text mein likho ya dubara try karo."
        )


async def process_downloaded_image(media_id: str, sender: str, mime_hint: Optional[str] = None):
    """
    Downloads the image and processes it.
    """
    try:
        file_path = await download_media_to_disk(media_id, sender, mime_hint)
        await process_image_and_respond(sender, file_path)
    except Exception as e:
        LOG.exception(f"Error downloading/processing image: {e}")
        await send_text_message_async(sender, "❌ Image download nahi ho paya. Dubara bhejo.")


async def process_audio_and_respond(sender: str, file_path: str):
    """
    Transcribe audio and process through chatbot.
    Allows shopkeepers to send voice messages with commands.
    """
    try:
        # Notify user we're processing
        await send_text_message_async(sender, "🎤 Voice message sun raha hoon...")
        
        # Transcribe
        transcription = await transcribe_audio(file_path)
        
        if not transcription or len(transcription.strip()) < 2:
            await send_text_message_async(
                sender, 
                "❌ Samajh nahi aaya. Please dobara bolo ya text mein likho."
            )
            return
        
        # Show what was heard
        await send_text_message_async(sender, f"👂 Yeh suna:\n\"{transcription}\"")
        
        LOG.info(f"Audio transcribed: {transcription}")
        
        # Process through chatbot
        await call_chatbot_and_respond(sender, transcription)
        
    except Exception as e:
        LOG.exception(f"Error transcribing audio: {e}")
        await send_text_message_async(
            sender, 
            "❌ Voice message samajh nahi aaya. Please text mein likho."
        )


async def process_downloaded_audio(media_id: str, sender: str, mime_hint: Optional[str] = None):
    """
    Downloads the audio and transcribes it.
    """
    try:
        file_path = await download_media_to_disk(media_id, sender, mime_hint)
        await process_audio_and_respond(sender, file_path)
    except Exception as e:
        LOG.exception(f"Error downloading/processing audio: {e}")
        await send_text_message_async(sender, "❌ Audio download nahi ho paya. Dubara bhejo.")


async def process_downloaded_video(media_id: str, sender: str, mime_hint: Optional[str] = None):
    """
    Downloads the video and transcribes audio track.
    """
    try:
        await send_text_message_async(sender, "🎥 Video mila... audio nikal raha hoon...")
        file_path = await download_media_to_disk(media_id, sender, mime_hint)
        await process_audio_and_respond(sender, file_path)
    except Exception as e:
        LOG.exception(f"Error downloading/processing video: {e}")
        await send_text_message_async(sender, "❌ Video process nahi ho paya. Audio bhejo instead.")