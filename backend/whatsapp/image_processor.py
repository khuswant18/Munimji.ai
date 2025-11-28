import json
import logging
import os
import re
import asyncio
import subprocess
import sys

LOG = logging.getLogger(__name__)

# Check if docstrange is available via subprocess
def _check_docstrange_available() -> bool:
    """Check if docstrange is installed in a separate venv or system."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "from docstrange import DocumentExtractor; print('ok')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0 and "ok" in result.stdout
    except Exception:
        return False

DOCSTRANGE_AVAILABLE = _check_docstrange_available()
if not DOCSTRANGE_AVAILABLE:
    LOG.warning("docstrange not available in current environment")


def _extract_with_docstrange_subprocess(file_path: str) -> dict:
    """Run DocStrange extraction via subprocess to avoid dependency conflicts."""
    try:
        # Use the image_ocr_model.py script which has docstrange
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "image_ocr_model.py")
        
        if not os.path.exists(script_path):
            LOG.error(f"image_ocr_model.py not found at {script_path}")
            return {}
        
        # Run docstrange via uv which has it installed separately
        result = subprocess.run(
            ["uv", "run", "--with", "docstrange[local-llm]", "python", script_path, file_path],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout for OCR
            cwd=os.path.dirname(script_path)
        )
        
        if result.returncode != 0:
            LOG.error(f"DocStrange subprocess failed: {result.stderr}")
            return {}
        
        # Parse JSON output from script
        output = result.stdout.strip()
        
        # Find the JSON part (skip any auth/info messages)
        json_start = output.find('{')
        if json_start == -1:
            LOG.error(f"No JSON found in DocStrange output: {output[:200]}")
            return {}
        
        json_str = output[json_start:]
        return json.loads(json_str)
        
    except subprocess.TimeoutExpired:
        LOG.error("DocStrange subprocess timed out")
        return {}
    except json.JSONDecodeError as e:
        LOG.error(f"Failed to parse DocStrange JSON output: {e}")
        return {}
    except Exception as e:
        LOG.exception(f"DocStrange subprocess error: {e}")
        return {}


async def extract_image_data_with_docstrange(file_path: str) -> dict:
    """
    Extract structured data from image using DocStrange.
    Returns a dictionary with extracted fields.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _extract_with_docstrange_subprocess, file_path)


async def extract_invoice_data(file_path: str) -> dict:
    """
    Extract invoice/bill data and return as structured dict.
    Used for confirmation flow before adding to records.
    """
    try:
        raw_data = await extract_image_data_with_docstrange(file_path)
        if not raw_data:
            return {}
        
        # Extract key fields for invoice
        doc_type = raw_data.get("document_type", "").lower()
        
        invoice_data = {
            "type": "invoice" if "invoice" in doc_type else "bill" if "bill" in doc_type else "receipt",
            "supplier": raw_data.get("company_name", ""),
            "customer": raw_data.get("sold_to_name", ""),
            "date": raw_data.get("invoice_date") or raw_data.get("date", ""),
            "invoice_number": raw_data.get("invoice_number", ""),
            "items": [],
            "total_amount": None,
            "raw_data": raw_data
        }
        
        # Extract line items
        for i in range(1, 20):
            qty = raw_data.get(f"item_{i}_qty")
            desc = raw_data.get(f"item_{i}_description")
            amount = raw_data.get(f"item_{i}_amount")
            unit_price = raw_data.get(f"item_{i}_unit_price")
            
            if desc:
                invoice_data["items"].append({
                    "qty": qty,
                    "description": desc,
                    "unit_price": unit_price,
                    "amount": amount
                })
        
        # Get total amount
        invoice_data["total_amount"] = (
            raw_data.get("total_amount_due") or 
            raw_data.get("amount_due") or 
            raw_data.get("total_sales_vat_inclusive") or
            raw_data.get("total")
        )
        
        return invoice_data
        
    except Exception as e:
        LOG.exception(f"Error extracting invoice data: {e}")
        return {}


def format_invoice_for_display(invoice_data: dict) -> str:
    """
    Format invoice data for display to user (without buttons - buttons sent separately).
    """
    if not invoice_data:
        return ""
    
    lines = ["📋 *INVOICE DETAILS*\n"]
    
    if invoice_data.get("supplier"):
        lines.append(f"🏢 *Supplier:* {invoice_data['supplier']}")
    
    if invoice_data.get("date"):
        lines.append(f"📅 *Date:* {invoice_data['date']}")
    
    if invoice_data.get("invoice_number"):
        lines.append(f"🔢 *Invoice #:* {invoice_data['invoice_number']}")
    
    # Items
    if invoice_data.get("items"):
        lines.append("\n📦 *Items:*")
        for item in invoice_data["items"][:10]:  # Limit to 10 items for display
            qty = item.get("qty", "")
            desc = item.get("description", "")[:50]  # Truncate long descriptions
            amount = item.get("amount", "")
            if qty and desc:
                lines.append(f"  • {qty}x {desc}")
                if amount:
                    lines.append(f"    ₹{amount}")
    
    if invoice_data.get("total_amount"):
        lines.append(f"\n💰 *Total Amount:* ₹{invoice_data['total_amount']}")
    
    return "\n".join(lines)


def format_docstrange_result(data: dict) -> str:
    """
    Convert DocStrange extracted data to a readable format for the chatbot.
    Handles bills, invoices, receipts, and handwritten notes.
    """
    if not data:
        return ""
    
    result_parts = []
    
    # Check for invoice/bill type documents
    doc_type = data.get("document_type", "").lower()
    
    if "invoice" in doc_type or "bill" in doc_type or "receipt" in doc_type:
        # Format as bill/invoice
        if data.get("company_name"):
            result_parts.append(f"Company: {data['company_name']}")
        
        if data.get("sold_to_name"):
            result_parts.append(f"Customer: {data['sold_to_name']}")
        
        if data.get("date"):
            result_parts.append(f"Date: {data['date']}")
        
        if data.get("invoice_number"):
            result_parts.append(f"Invoice #: {data['invoice_number']}")
        
        # Extract line items
        items = []
        for i in range(1, 20):  # Check up to 20 items
            qty_key = f"item_{i}_qty"
            desc_key = f"item_{i}_description"
            amount_key = f"item_{i}_amount"
            
            if qty_key in data and desc_key in data:
                qty = data.get(qty_key, "")
                desc = data.get(desc_key, "")
                amount = data.get(amount_key, "")
                items.append(f"  - {qty}x {desc}: ₹{amount}")
        
        if items:
            result_parts.append("Items:")
            result_parts.extend(items)
        
        # Total amount
        total = data.get("total_amount_due") or data.get("amount_due") or data.get("total_sales_vat_inclusive")
        if total:
            result_parts.append(f"Total Amount: ₹{total}")
        
        return "\n".join(result_parts)
    
    # For other documents or handwritten notes - extract all meaningful fields
    meaningful_fields = []
    for key, value in data.items():
        if value and str(value).strip():
            # Skip empty or whitespace-only values
            clean_key = key.replace("_", " ").title()
            meaningful_fields.append(f"{clean_key}: {value}")
    
    return "\n".join(meaningful_fields) if meaningful_fields else ""


async def extract_image_data(file_path: str) -> str:
    """
    Extracts text/data from image using DocStrange via subprocess.
    Returns formatted text suitable for the chatbot.
    """
    try:
        # Extract structured data with DocStrange (via subprocess)
        data = await extract_image_data_with_docstrange(file_path)
        
        if data:
            formatted = format_docstrange_result(data)
            if formatted:
                return formatted
            # If formatting failed but we have data, return as JSON
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        return "Could not extract text from image. Please send as text message instead."
        
    except Exception as e:
        LOG.exception("Image extraction failed: %s", e)
        return f"Error processing image: {str(e)}"


def parse_extracted_to_command(extracted_text: str) -> str:
    """
    Parse extracted text and convert to a chatbot command if possible.
    Works with both DocStrange formatted output and raw text.
    """
    text_lower = extracted_text.lower()
    original = extracted_text
    
    # If it looks like structured DocStrange output, extract key info
    if "Total Amount:" in extracted_text or "Amount Due:" in extracted_text:
        # Extract total amount from formatted output
        amount_match = re.search(r'(?:Total Amount|Amount Due)[:\s]*₹?\s*(\d+(?:\.\d+)?)', extracted_text)
        if amount_match:
            amount = amount_match.group(1)
            
            # Try to find customer name
            customer_match = re.search(r'Customer[:\s]*([^\n]+)', extracted_text)
            if customer_match:
                customer = customer_match.group(1).strip()
                return f"{customer} ke {amount} rupay ka bill"
            
            return f"{amount} rupay ka bill received"
    
    # Try to find a command-like pattern directly
    # Pattern: "Name ke/ka/ne X rupay/rs udhaar/diye"
    command_patterns = [
        r'([A-Z][a-z]+)\s+ke\s+(\d+)\s*(?:rupay|rs|rupees?)?\s*udhaar',
        r'([A-Z][a-z]+)\s+ka\s+(\d+)\s*(?:rupay|rs|rupees?)?\s*(?:udhaar|baaki)',
        r'([A-Z][a-z]+)\s+ne\s+(\d+)\s*(?:rupay|rs|rupees?)?\s*diye?',
        r'(\d+)\s*(?:rupay|rs|₹)?\s*ka\s+(petrol|diesel|chai|rent|electricity)',
    ]
    
    for pattern in command_patterns:
        match = re.search(pattern, original, re.IGNORECASE)
        if match:
            groups = match.groups()
            if pattern.startswith(r'(\d+)'):  # Expense pattern
                return f"{groups[0]} ka {groups[1]}"
            elif 'ne' in pattern:
                return f"{groups[0]} ne {groups[1]} rupay diye"
            else:
                return f"{groups[0]} ke {groups[1]} rupay udhaar"
    
    # Fallback: Try to extract quoted text (model often puts extracted text in quotes)
    quoted_matches = re.findall(r'"([^"]+)"', extracted_text)
    for quoted in quoted_matches:
        # Check if it looks like a command
        if any(kw in quoted.lower() for kw in ['udhaar', 'rupay', 'diye', 'baaki', 'petrol']):
            return quoted
    
    # Try to find amount patterns
    amount_match = re.search(r'(?:rs\.?|₹|rupees?|rupay)\s*(\d+)', text_lower)
    if not amount_match:
        amount_match = re.search(r'(\d+)\s*(?:rs|rupees?|rupay)', text_lower)
    if not amount_match:
        amount_match = re.search(r'\b(\d{3,})\b', text_lower)  # 3+ digit number
    
    # Try to find name patterns (capitalized words, excluding common words)
    excluded_names = {'the', 'this', 'that', 'can', 'will', 'has', 'have', 'text', 'image', 
                      'however', 'translated', 'extracted', 'format', 'command', 'alternative',
                      'company', 'customer', 'date', 'invoice', 'items', 'total', 'amount'}
    name_match = None
    for word in re.findall(r'\b([A-Z][a-z]+)\b', original):
        if word.lower() not in excluded_names:
            name_match = word
            break
    
    # If we found both name and amount, create a command
    if amount_match and name_match:
        amount = amount_match.group(1)
        name = name_match
        
        # Determine if it's payment received or udhaar given
        if any(kw in text_lower for kw in ['received', 'paid', 'mila', 'diye']):
            return f"{name} ne {amount} rupay diye"
        else:
            return f"{name} ke {amount} rupay udhaar"
    
    # If just amount found (expense/purchase)
    if amount_match:
        amount = amount_match.group(1)
        # Look for expense keywords
        for kw in ['petrol', 'diesel', 'fuel', 'rent', 'electricity', 'chai', 'food']:
            if kw in text_lower:
                return f"{amount} ka {kw}"
        return f"{amount} rupay expense"
    
    # Return first meaningful line
    lines = [l.strip() for l in extracted_text.split('\n') if l.strip()]
    for line in lines:
        if any(c.isdigit() for c in line) and len(line) > 5:
            return line[:100]
    
    return lines[0][:100] if lines else extracted_text[:100]