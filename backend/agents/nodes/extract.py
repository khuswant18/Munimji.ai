"""
Entity extraction with rule-based fast path and LLM fallback.

Optimizations:
- Rule-based extraction for common patterns (numbers, names, amounts)
- LLM only called when rule-based extraction is incomplete
- Cached LLM responses via groq_client
"""
import json
import re
from typing import Dict, Any, Optional, List
from backend.llm.groq_client import groq_chat
from backend.agents.state import AgentState
from backend.decorators.timeit import time_node

HINDI_STOPWORDS = [
    "wali", "wale", "wale*", "rs", "rupiya", "rupay", "rupees", 
    "ka", "ki", "add", "karo", "entry", "bas", "ko", "se", "mein",
    "hai", "tha", "thi", "the", "aur", "bhi", "ne", "par", "pe"
]

# Common units for quantity extraction
UNITS = [
    "kg", "kilo", "kilogram", "gram", "gm", "g",
    "liter", "litre", "l", "ml",
    "packet", "packets", "pkt", "pc", "pcs", "piece", "pieces",
    "box", "boxes", "carton", "cartons", "bag", "bags", "sack",
    "dozen", "bottle", "bottles", "can", "cans",
    "meter", "metre", "m", "cm", "feet", "ft",
]

# Common item categories
EXPENSE_CATEGORIES = {
    "fuel": ["petrol", "diesel", "fuel", "gas", "cng"],
    "utility": ["electricity", "water", "internet", "phone", "mobile"],
    "rent": ["rent", "kiraya"],
    "salary": ["salary", "wages", "labour", "labor"],
    "transport": ["auto", "taxi", "cab", "uber", "ola", "fare"],
    "food": ["food", "lunch", "dinner", "breakfast", "chai", "tea", "coffee", "snack"],
    "office": ["stationary", "stationery", "office", "packing"],
}


def clean_item(text: str) -> str:
    """Remove stopwords and clean item text."""
    words = text.split()
    words = [w for w in words if w.lower() not in HINDI_STOPWORDS]
    return " ".join(words).strip()


def extract_amount(text: str) -> Optional[int]:
    """Extract amount/price from text using common patterns."""
    t = text.lower()
    
    # Pattern: ₹500, Rs 500, Rs.500, 500 rupees, 500rs
    patterns = [
        r'[₹]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # ₹500
        r'rs\.?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Rs 500, Rs.500
        r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:rs|rupees?|rupiya)',  # 500rs, 500 rupees
        r'(\d+(?:,\d{3})*)\s*(?:ka|ki|ke)\b',  # 500 ka
        r'\b(\d+(?:,\d{3})*)\b',  # Plain number (last resort)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, t)
        if match:
            try:
                # Remove commas and convert to int
                return int(match.group(1).replace(',', '').split('.')[0])
            except:
                continue
    return None


def extract_quantity_and_unit(text: str) -> tuple[Optional[int], Optional[str]]:
    """Extract quantity and unit from text."""
    t = text.lower()
    
    # Pattern: 10 kg, 5 packets, 2 dozen
    # Try to match plural forms and normalize to singular
    unit_map = {
        "packets": "packet", "pkts": "packet", "pkt": "packet",
        "pieces": "piece", "pcs": "piece", "pc": "piece",
        "boxes": "box", "cartons": "carton", "bags": "bag",
        "bottles": "bottle", "cans": "can", "sacks": "sack",
        "kilos": "kg", "kilogram": "kg", "kilograms": "kg",
        "liters": "liter", "litres": "liter", "litre": "liter",
        "grams": "gram", "gm": "gram",
        "meters": "meter", "metres": "meter", "metre": "meter",
    }
    
    for unit in UNITS:
        pattern = rf'(\d+)\s*{re.escape(unit)}s?\b'  # Allow optional 's' for plurals
        match = re.search(pattern, t)
        if match:
            matched_unit = unit
            # Check if we matched a plural and normalize
            full_match = match.group(0).lower()
            for plural, singular in unit_map.items():
                if plural in full_match:
                    matched_unit = singular
                    break
            return int(match.group(1)), matched_unit
    
    # Fallback: just get first number as quantity
    match = re.search(r'\b(\d+)\b', t)
    if match:
        return int(match.group(1)), None
    
    return None, None


def extract_name(text: str) -> Optional[str]:
    """Extract person/business name from text."""
    original = text  # Keep original case
    
    # Pattern: "to Ramesh", "from Mohan", "ko Suresh", "se Amit"
    patterns = [
        r'\b(?:to|from|ko|se)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:ko|se|ne)',
        r'customer\s+([A-Z][a-z]+)',
        r'supplier\s+([A-Z][a-z]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, original)
        if match:
            name = match.group(1).strip()
            # Filter out common non-names
            if name.lower() not in ['the', 'a', 'an', 'for', 'with', 'and']:
                return name
    
    # Fallback: find capitalized words that look like names
    words = re.findall(r'\b([A-Z][a-z]{2,})\b', original)
    excluded = {'Fuel', 'Petrol', 'Diesel', 'Rent', 'Salary', 'Stock', 'Invoice', 
                'Sale', 'Purchase', 'Udhaar', 'Payment', 'Received', 'Sold', 'Bought'}
    for word in words:
        if word not in excluded:
            return word
    
    return None


def extract_expense_category(text: str) -> Optional[str]:
    """Determine expense category from text."""
    t = text.lower()
    for category, keywords in EXPENSE_CATEGORIES.items():
        for kw in keywords:
            if kw in t:
                return category
    return None


def extract_item_for_inventory(text: str) -> Optional[str]:
    """
    Extract item name for inventory additions.
    Patterns like: "pen add karo", "add karo pen", "2 pen add kar do"
    """
    t = text.lower()
    
    # Pattern 1: "X add karo" - item before add
    match = re.match(r'^(\d*\s*)?(\w+)\s+(?:add|jod|daal)\s+(?:karo|kar\s+do)', t)
    if match:
        item = match.group(2)
        if item and item not in HINDI_STOPWORDS:
            return item.title()
    
    # Pattern 2: "add karo X" - item after add
    match = re.search(r'(?:add|jod|daal)\s+(?:karo|kar\s+do)\s+(\w+)', t)
    if match:
        item = match.group(1)
        if item and item not in HINDI_STOPWORDS:
            return item.title()
    
    # Pattern 3: quantity + item, e.g., "5 pen", "10 kg rice"
    match = re.search(r'\b(\d+)\s*(?:kg|g|pcs?|packets?)?\s*(\w{2,})', t)
    if match:
        item = match.group(2)
        if item and item not in HINDI_STOPWORDS and item not in ['add', 'karo', 'kar']:
            return item.title()
    
    # Fallback: First meaningful word that's not a number or stopword
    words = text.split()
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word.lower())
        if clean_word and clean_word not in HINDI_STOPWORDS and not clean_word.isdigit():
            if clean_word not in ['add', 'karo', 'kar', 'do', 'jod', 'daal']:
                return clean_word.title()
    
    return None


def rule_based_entity_extraction(text: str, intent: str) -> Dict[str, Any]:
    """
    Extract entities using rule-based patterns.
    Returns dict with extracted fields and confidence.
    """
    entities: Dict[str, Any] = {"entries": [{}]}
    entry = entities["entries"][0]
    confidence = 0.0
    fields_found = 0
    
    # Extract amount (common to all intents)
    amount = extract_amount(text)
    if amount:
        entry["amount"] = amount
        fields_found += 1
    
    # Extract quantity and unit
    quantity, unit = extract_quantity_and_unit(text)
    if quantity:
        entry["quantity"] = quantity
        fields_found += 1
    if unit:
        entry["unit"] = unit
    
    # Extract name (customer/supplier)
    name = extract_name(text)
    if name:
        if intent in ["add_sale", "add_udhaar", "add_payment"]:
            entry["customer"] = name
        else:
            entry["supplier"] = name
        fields_found += 1
    
    # Intent-specific extraction
    if intent == "add_expense":
        category = extract_expense_category(text)
        if category:
            entry["category"] = category
            entry["description"] = f"{category.capitalize()} expense"
            fields_found += 1
        else:
            # Use first significant word as description
            words = clean_item(text).split()
            if words:
                entry["description"] = " ".join(words[:3])
    
    elif intent == "add_sale":
        # Try to extract item name
        item = clean_item(text)
        if item and len(item) > 2:
            entry["item"] = item
            fields_found += 1
        # Calculate total if we have quantity and price
        if entry.get("quantity") and entry.get("amount"):
            if not entry.get("price"):
                entry["price"] = entry["amount"] // entry["quantity"]
    
    elif intent == "add_purchase":
        item = clean_item(text)
        if item and len(item) > 2:
            entry["item"] = item
            fields_found += 1
    
    elif intent in ["add_inventory", "add_entry"]:
        # Extract item name for inventory additions like "pen add karo"
        item = extract_item_for_inventory(text)
        if item:
            entry["item"] = item
            fields_found += 1
        # If we have price and no quantity, assume quantity=1
        if entry.get("amount") and not entry.get("quantity"):
            entry["quantity"] = 1
            entry["price"] = entry["amount"]
    
    elif intent == "add_udhaar":
        # Determine udhaar type (given vs taken)
        t = text.lower()
        if any(kw in t for kw in ["diya", "given", "lent", "de diya"]):
            entry["type"] = "given"
        elif any(kw in t for kw in ["liya", "taken", "borrowed", "le liya"]):
            entry["type"] = "taken"
        else:
            entry["type"] = "given"  # Default
        entry["payment_status"] = "pending"
    
    elif intent == "add_payment":
        t = text.lower()
        if any(kw in t for kw in ["received", "mila", "got"]):
            entry["type"] = "received"
        else:
            entry["type"] = "paid"
    
    # Calculate confidence based on fields found
    confidence = min(1.0, fields_found * 0.25)
    entities["_extraction_confidence"] = confidence
    entities["_fields_found"] = fields_found
    
    return entities


# Minimum confidence to skip LLM extraction
EXTRACTION_CONFIDENCE_THRESHOLD = 0.5

# Required fields per intent for complete extraction
REQUIRED_FIELDS = {
    "add_sale": ["amount"],
    "add_purchase": ["amount"],
    "add_expense": ["amount"],
    "add_udhaar": ["customer", "amount"],
    "add_payment": ["amount"],
}


@time_node
def extract_entities(state: AgentState) -> AgentState:
    """
    Extract entities with rule-based fast path and LLM fallback.
    """
    # Extract text from last message
    try:
        msgs = state["messages"]
        if msgs:
            last_msg = msgs[-1]
            if hasattr(last_msg, "content"):
                text = last_msg.content
            elif isinstance(last_msg, dict) and "content" in last_msg:
                text = last_msg["content"]
            else:
                text = str(last_msg)
        else:
            text = ""
    except:
        text = ""
    
    intent = state["intent"]
    missing_slots = state.get("missing_slots", [])

    # Get existing entities (may have been pre-filled by classify.py from context)
    entities = state.get("entities") or {"entries": [{}]}
    entry = entities["entries"][0] if entities.get("entries") else {}
    
    # Save pre-filled entities before extraction (so we can merge later)
    pre_filled_entry = dict(entry) if entry else {}

    if missing_slots:
        # Quick slot filling from follow-up message
        for slot in missing_slots:
            if slot == "quantity":
                numbers = re.findall(r"(\d+)", text)
                if numbers:
                    entry["quantity"] = int(numbers[0])
            elif slot == "price":
                amount = extract_amount(text)
                if amount:
                    entry["price"] = amount
            elif slot == "amount":
                amount = extract_amount(text)
                if amount:
                    entry["amount"] = amount
            elif slot == "customer":
                name = extract_name(text)
                if name:
                    entry["customer"] = name
            elif slot == "supplier":
                name = extract_name(text)
                if name:
                    entry["supplier"] = name
        
        # Remove filled slots
        state["missing_slots"] = [s for s in missing_slots if s not in entry]
        if not state["missing_slots"]:
            state["needs_followup"] = False
        
        if entities.get("entries"):
            entities["entries"][0] = entry
        state["entities"] = entities
        return state

    # 1. Try rule-based extraction first
    rule_entities = rule_based_entity_extraction(text, intent)
    confidence = rule_entities.get("_extraction_confidence", 0)
    
    # Check if we have all required fields
    required = REQUIRED_FIELDS.get(intent, [])
    rule_entry = rule_entities["entries"][0] if rule_entities.get("entries") else {}
    
    # IMPORTANT: Merge pre-filled entities from classify.py with extracted entities
    # Pre-filled values take precedence (don't overwrite context-aware classification)
    merged_entry = dict(rule_entry)  # Start with extracted
    for key, value in pre_filled_entry.items():
        if value is not None and value != "":
            merged_entry[key] = value  # Pre-filled overrides
    
    # Update rule_entry and rule_entities with merged data
    rule_entry = merged_entry
    rule_entities["entries"] = [merged_entry]
    
    has_required = all(merged_entry.get(field) for field in required)
    
    # If rule-based extraction is sufficient, skip LLM
    if has_required or confidence >= EXTRACTION_CONFIDENCE_THRESHOLD:
        # Clean up internal fields
        if "_extraction_confidence" in rule_entities:
            del rule_entities["_extraction_confidence"]
        if "_fields_found" in rule_entities:
            del rule_entities["_fields_found"]
        state["entities"] = rule_entities
        return state

    # 2. LLM fallback for complex cases
    field_prompts = {
        "add_sale": "Extract: item, quantity, unit, price, customer, payment_status, amount",
        "add_purchase": "Extract: item, quantity, unit, price, supplier, payment_mode, amount",
        "add_udhaar": "Extract: customer, amount, description, type (given/taken)",
        "add_expense": "Extract: amount, supplier, payment_mode, description",
        "add_payment": "Extract: customer, amount, description, type (received/paid)",
        "query_summary": "Extract: query_type (daily/weekly/monthly)",
        "query_ledger": "Extract: filter, date_range",
        "query_udhaar": "Extract: customer (if specific)",
    }

    prompt_text = field_prompts.get(intent, "Extract relevant entities.")

    # Compact prompt for faster LLM response
    prompt = f"""Message: "{text}"
Intent: {intent}
{prompt_text}
Return JSON: {{"entries": [{{...}}]}}"""

    response = groq_chat(prompt, temperature=0, max_tokens=256)
    
    try:
        llm_entities = json.loads(response)
        # Merge: pre-filled → rule-based → LLM (in priority order)
        if llm_entities.get("entries"):
            llm_entry = llm_entities["entries"][0]
            # First, apply rule-based extractions
            for key, value in rule_entry.items():
                if value is not None:
                    llm_entry[key] = value
            # Then, apply pre-filled (highest priority - from context)
            for key, value in pre_filled_entry.items():
                if value is not None and value != "":
                    llm_entry[key] = value
            llm_entities["entries"][0] = llm_entry
            state["entities"] = llm_entities
        else:
            state["entities"] = rule_entities
    except:
        # LLM parsing failed, use rule-based results (already merged with pre-filled)
        state["entities"] = rule_entities

    return state
