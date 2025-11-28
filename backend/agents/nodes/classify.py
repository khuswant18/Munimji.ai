import json
import re
from typing import Any, Dict, List

from backend.llm.groq_client import groq_chat
from backend.agents.state import AgentState
from backend.decorators.timeit import time_node
from .guardrails import (
    is_blocked_content, 
    is_menu_selection, 
    is_business_related,
    detect_quick_action
)

INTENTS = [
    "add_sale",
    "add_purchase",
    "add_expense",
    "add_udhaar",
    "add_payment",
    "add_note",
    "add_inventory",  # For generic item additions like "pen add karo"
    "add_customer",   # Add new customer
    "query_summary",
    "query_ledger",
    "query_udhaar",
    "query_customer", # Show customer details
    "query_profile",  # User asking about their own info (name, shop, etc.)
    "greeting",
    "casual_chat",    # General conversation
    "menu_request",   # User asked for menu
    "blocked",        # Inappropriate content
    "off_topic",      # Not business related
    "unknown",
]

# --- Minimal helpers ---
def _extract_text_from_state(state: AgentState) -> str:
    # Try a few common shapes, return first found text
    try:
        msgs = state.get("messages", None)
        if msgs:
            for m in reversed(msgs):
                if hasattr(m, "content"):
                    return m.content
                if isinstance(m, dict) and "content" in m:
                    return m["content"]
    except Exception:
        pass
    try:
        return state.get("text", "")
    except Exception:
        pass
    return ""

def _extract_json_from_text(text: str) -> Dict[str, Any]:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text, flags=re.IGNORECASE).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"(\{(?:[^{}]|(?1))*\})", text, flags=re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # last-resort simple extraction
    obj: Dict[str, Any] = {}
    for key in ("intent", "confidence", "reason"):
        mm = re.search(rf'{key}\s*[:=]\s*"([^"]+)"', text, flags=re.IGNORECASE)
        if mm:
            obj[key] = mm.group(1)
        elif key == "confidence":
            mmn = re.search(rf'{key}\s*[:=]\s*([0-9]*\.?[0-9]+)', text, flags=re.IGNORECASE)
            if mmn:
                try:
                    obj[key] = float(mmn.group(1))
                except Exception:
                    obj[key] = mmn.group(1)
    return obj

# --- Enhanced Deterministic rule-based mapping (high coverage) ---
RULE_KEYWORDS = {
    "add_expense": [
        # Fuel related
        "fuel", "petrol", "diesel", "gas", "cng", "petrolpump", "petrol pump",
        # Bills & utilities
        "rent", "electricity", "power bill", "maintenance", "repair", "bill paid",
        "water bill", "phone bill", "internet", "wifi", "mobile recharge",
        # Salary & wages
        "salary", "wages", "labour", "labor", "worker", "staff",
        # Food & consumables
        "grocery", "grocer", "groceries", "food", "snack", "dinner", "lunch", 
        "chai", "tea", "coffee", "breakfast", "khana",
        # Transport
        "auto fare", "taxi", "cab", "uber", "ola", "travel", "transport", "fare",
        # Shop expenses
        "packing material", "expense", "kharcha", "miscellaneous", "misc",
        "stationary", "stationery", "office supplies",
        # Common OCR/voice variations
        "bijli", "bijli ka bill", "paani", "paani ka bill", "kiraya",
        "labour charge", "mistri", "mechanic", "cleaning",
    ],
    "add_purchase": [
        # Stock & inventory
        "stock", "inventory", "resale", "wholesale", "bought for resale",
        "bought for shop", "materials", "raw material", "purchase", "purchased",
        "kharida", "maal kharida", "buy for shop", "bought stock",
        # Specific materials
        "cement", "sand", "iron", "steel", "wood", "plastic",
        # Quantity indicators often with purchase
        "packet", "packets", "box", "boxes", "carton", "cartons", "sack", "bags",
        # Voice/OCR variations
        "maal liya", "saman liya", "maal mangaya", "order kiya",
        "wholesale se", "dealer se",
    ],
    "add_sale": [
        # Sale terms
        "sold", "sale", "sold to", "bill to", "invoice to", "invoiced",
        "becha", "maal gaya", "becha hua", "bech diya", "bikri", "bechi",
        # Customer indicators
        "customer bought", "given to customer",
        # Voice/OCR variations
        "saman diya", "maal diya", "bill banaya", "customer ko diya",
        "bikri hui", "bik gaya", "customer ko",
    ],
    "add_udhaar": [
        # Udhaar/credit terms
        "udhaar", "loan", "borrowed", "lend", "lent", "liya udhaar", "udhaar liya",
        "udhar", "udhar liya", "udhar diya", "udhaar diya", "credit",
        # Debit/credit parties
        "debtor", "creditor", "owes", "owe",
        # Common phrases for adding udhaar (not viewing)
        "baaki", "baki", "udhaar add", "khata add",
        # Voice/OCR variations - common handwritten notes
        "ka baaki", "ka baki", "baaki hai", "udhaar hai", 
        "dena hai", "lena hai", "khata mein",
    ],
    "add_payment": [
        # Payment received
        "gave back", "paid back", "repaid", "paid to", "received payment",
        "received", "returned", "got back", "settled", "payment received", "payment",
        "mila", "received from", "paid by", "payment done",
        # Payment made
        "paid", "diya", "diye", "de diya", "given", "cleared",
        # Voice/OCR variations
        "paisa mila", "paise mile", "rupay mile", "payment aaya",
        "wapas diya", "wapas mila", "chuka diya", "clear kiya",
        # Common misspellings
        "recieved", "recived", "recevied",
    ],
    "add_note": [
        "add a note", "add note", "note about", "save note", "reminder note",
        "remember", "yaad rakh", "note kar", "likh le",
    ],
    "query_summary": [
        "summary", "today's summary", "monthly summary", "how much earned", "total profit",
        "kitna kama", "total", "report", "aaj ka", "today's", "earnings",
        "profit", "loss", "balance sheet", "aaj ka hisab", "hisab dekhna",
        "hisab dekho", "hisab dikhana", "hisab batao", "hisaab", "hisaab dekhna",
        # Voice/OCR variations
        "kitna hua", "kul kitna", "total kitna", "din bhar ka", "mahine ka",
        "kamai", "nafa", "nuksan", "fayda",
    ],
    "query_ledger": [
        "ledger", "show ledger", "transactions list", "history", "transaction history",
        "record", "entries", "log", "show entries", "dikhao", "list karo",
        "hisab dikhao", "khata dikhao", "dekhna hai", "dekho",
        # Voice/OCR variations
        "sab entries", "saari entries", "record dikhao", "kya kya hua",
    ],
    "query_udhaar": [
        "who owes", "udhaar list", "who owes me", "outstanding udhaar", "show udhaar", 
        "due amounts", "kitna dena hai", "kitna lena hai", "pending", "outstanding",
        "baaki list", "kaun kitna dena", "kaun kitna lena",
        "udhaar dikhao", "pending udhaar",
        # Voice/OCR variations
        "sabka hisab", "sabka udhaar", "baaki wale", "pending list",
    ],
    "greeting": [
        "hi", "hello", "hey", "good morning", "good evening", "namaste", "pranam",
        "assalam", "salaam", "namaskar", "good afternoon", "good night",
        # Voice variations
        "hallo", "helo", "namashkar", "namasthe",
    ],
    "add_customer": [
        "new customer", "naya customer", "naya grahak", "add customer", "customer add",
        "party add", "naya party",
    ],
    "query_customer": [
        "customer detail", "customer ka hisab", "party ka khata", "show customer",
        "grahak ka hisab", "customer ledger",
    ],
    "menu_request": [
        "menu", "help", "madad", "options", "kya kar sakta", "what can you do",
    ],
    "query_profile": [
        # Name questions
        "mera naam", "my name", "naam kya hai", "what is my name", "who am i",
        "main kaun", "main kon", "mera name",
        # Shop questions
        "meri dukaan", "my shop", "shop name", "dukaan ka naam", "meri shop",
        # Profile questions
        "mera account", "my account", "my profile", "meri profile",
        "mera number", "my number", "phone number",
    ],
}

# Priority patterns - these override keyword matching
PRIORITY_PATTERNS = [
    # Profile/personal questions (highest priority for user queries about themselves)
    (r"\b(mera|my|apna)\s*(naam|name)\b", "query_profile", 1.0),
    (r"\b(naam|name)\s*(kya|what)\s*(hai|is)\b", "query_profile", 1.0),
    (r"\b(who\s+am\s+i|main\s+kaun|main\s+kon)\b", "query_profile", 1.0),
    (r"\b(meri|my)\s*(dukaan|shop)\b", "query_profile", 0.95),
    (r"\b(mera|my)\s*(account|profile|number)\b", "query_profile", 0.95),
    
    # ===== QUERY patterns - check before add patterns =====
    # Devanagari Hindi patterns for "देखना" (to see), "हिसाब" (accounts)
    (r"(हिसाब|खाता|लेजर).*(देखना|दिखाओ|बताओ|देखो)", "query_summary", 1.0),
    (r"(देखना|दिखाओ|बताओ|देखो).*(है|हैं)?.*(हिसाब|खाता)", "query_summary", 1.0),
    (r"(आज|today).*(हिसाब|खाता|summary)", "query_summary", 0.98),
    (r"(मुझे|मुझको).*(देखना|दिखाओ|बताओ)", "query_summary", 0.95),
    
    # Romanized Hindi "dekhna" = to see
    # "aaj ka hisab dekhna hai" / "hisab dekho" / "hisab dikhao" etc.
    # BUT "sabka hisab" = query_udhaar (everyone's accounts = who owes)
    (r"\b(sabka|sab\s*ka|sabke|sab\s*ke)\s+(hisab|udhaar|baaki)\b", "query_udhaar", 1.0),  # Must be before generic hisab patterns
    (r"\b(sabka|sab\s*ka)\s+.*\b(dikhao|batao|dekhna)\b", "query_udhaar", 1.0),
    (r"\b(hisab|hisaab|khata)\s*(dekhna|dekho|dikhao|dikhana|batao)\b", "query_summary", 0.99),
    (r"\b(dekhna|dekho|dikhao|dikhana)\s*(hai|hain)?\s*(hisab|hisaab|khata)\b", "query_summary", 0.99),
    (r"\b(aaj|today).*(hisab|hisaab|khata|summary)\b", "query_summary", 0.98),
    (r"\b(hisab|hisaab|khata).*(aaj|today)\b", "query_summary", 0.98),
    # Hindi query pattern: "mujhe ... dekhna hai" (I want to see ...)
    (r"\b(mujhe|mujhey|muje).*\b(dekhna|dikhao|batao)\b", "query_summary", 0.95),
    # "ledger dikhao", "entries dikhao"
    (r"\b(ledger|entries|record)\s*(dikhao|dekhna|dekho|batao)\b", "query_ledger", 0.98),
    # Query variations from voice messages
    (r"\b(kitna|total|kul)\s+(hua|hai|the)\b", "query_summary", 0.95),
    (r"\b(din|aaj|kal)\s+(ka|ki|ke)\s+(total|hisab|summary)\b", "query_summary", 0.98),
    
    # ===== IMAGE OCR patterns - common handwritten note formats =====
    # Bill/receipt patterns from OCR - check for total first (higher priority)
    (r"^(total|amount)\s*[:=-]?\s*\d+", "add_sale", 0.98),  # Total at start of line
    (r"\b(total|grand\s*total|bill\s*amount|subtotal)\s*[:=-]?\s*\d+", "add_sale", 0.97),
    (r"\b(total\s+bill|bill\s+total)\b.*\d+", "add_sale", 0.97),  # "Total bill - Rs 3500"
    (r"\b(item|qty|quantity|rate|amount)\s*[:=]", "add_sale", 0.85),
    # "Name - Amount" or "Name = Amount" format (common in handwritten notes)
    # Must be a proper name (capitalized, 3+ chars) and not common words
    (r"^[A-Z][a-z]{2,}\s*[-=:]\s*\d+\s*(rs|₹|rupay)?$", "add_udhaar", 0.95),
    # Simple "Name Amount" pattern - only for proper nouns (exclude common words)
    # Excluded: expense/purchase/sale related words that might be capitalized + common typos
    (r"^(?!Fuel|Rent|Bill|Total|Sale|Stock|Purchase|Purchese|Kiraya|Petrol|Petol|Patrol|Diesel|Disel|Salary|Expense|Recieved)[A-Z][a-z]{2,}\s+\d{3,}\s*$", "add_udhaar", 0.90),
    # "Name ke 500" format from OCR
    (r"\b[A-Z][a-z]+\s+ke\s+\d+\b", "add_udhaar", 0.95),
    # Date + amount pattern (common in notes)
    (r"\b\d{1,2}[/-]\d{1,2}[/-]?\d{0,4}\s*[-:]\s*\d+", "add_expense", 0.85),    # ===== AUDIO TRANSCRIPTION patterns - spoken Hindi/Hinglish =====
    # Voice message common patterns
    (r"\b(bol|bolo|bata|batao)\s+(na|de|do)\b", "query_summary", 0.85),
    (r"\b(sun|suno)\s+", "query_summary", 0.80),  # "sun kitna hua"
    # Natural speech patterns
    (r"\bkitna\s+(paisa|rupay|rs)\s+(hua|laga|diya|mila)\b", "query_summary", 0.95),
    (r"\b(aaj|kal|abhi)\s+kitna\b", "query_summary", 0.90),
    # Voice corrections/typos
    (r"\b(udar|udaar|udhr|udr)\b", "add_udhaar", 0.90),  # Common Whisper transcription variations
    (r"\b(petol|patrol|patral)\b", "add_expense", 0.90),  # Petrol variations
    (r"\b(selry|salri|salery)\b", "add_expense", 0.90),  # Salary variations
    
    # ===== Generic inventory addition patterns =====
    (r"(\w+)\s+(add|jod|daal)\s+karo", "add_inventory", 0.95),
    (r"(add|jod|daal)\s+karo\s+(\w+)", "add_inventory", 0.95),
    (r"(\w+)\s+add\s+kar\s+do", "add_inventory", 0.95),
    
    # ===== Expense patterns (most common) =====
    (r"\b(fuel|petrol|diesel|rent|electricity|salary|wages|bijli|kiraya)\b.*\d+", "add_expense", 1.0),
    (r"\d+.*\b(fuel|petrol|diesel|rent|electricity|bijli|kiraya)\b", "add_expense", 1.0),
    (r"\b(kharcha|expense|kharch)\b.*\d+", "add_expense", 0.95),
    # Voice patterns for expense
    (r"\b\d+\s*(ka|ki|ke)\s*(petrol|diesel|chai|khana|auto|taxi)\b", "add_expense", 0.98),
    # Common typos in expense words
    (r"\b(fule|fuell|patrol|petol|petrl|disel|diesal|kiray|kirya)\b.*\d+", "add_expense", 0.95),
    
    # ===== Purchase patterns - include common typos =====
    (r"\b(kharida|bought|purchase|purchese|purchse|stock)\b.*\d+", "add_purchase", 0.95),
    (r"\d+.*\b(packet|carton|box|kg|liter)\b.*\b(kharida|bought)\b", "add_purchase", 0.95),
    # Voice patterns for purchase
    (r"\b(maal|saman)\s+(liya|mangaya|aaya)\b.*\d+", "add_purchase", 0.95),
    (r"\b(dealer|wholesale)\s+se\b.*\d+", "add_purchase", 0.95),
    
    # ===== Sale patterns =====
    (r"\b(sold|becha|sale|invoice)\b.*\d+", "add_sale", 0.95),
    (r"\b(sold|becha)\b.*\b(to|ko)\b", "add_sale", 0.95),
    # Voice patterns for sale
    (r"\b(maal|saman)\s+(diya|gaya|becha)\b.*\d+", "add_sale", 0.95),
    (r"\b(customer|grahak)\s+ko\b.*\d+", "add_sale", 0.90),
    
    # ===== Udhaar patterns (name + amount + udhaar keyword) =====
    (r"\b[A-Z][a-z]+\b.*\b(udhaar|udhar|credit|loan)\b.*\d+", "add_udhaar", 0.95),
    (r"\b(udhaar|udhar)\b.*\b(diya|liya)\b", "add_udhaar", 0.95),
    (r"\d+.*\b(udhaar|udhar)\b", "add_udhaar", 0.90),
    # "Mohan ka 1000 baaki" - name + amount + baaki = add_udhaar
    (r"\b[A-Z][a-z]+\b.*\d+.*\b(baaki|baki)\b", "add_udhaar", 0.95),
    (r"\b[A-Z][a-z]+\b.*\b(ka|ke|ki)\b.*\d+.*\b(baaki|baki|hai)\b", "add_udhaar", 0.95),
    # Voice patterns for udhaar - natural speech
    (r"\b[A-Z][a-z]+\s+(ne|ko)\s+(udhaar|udhar)\s+(liya|diya)\b", "add_udhaar", 0.98),
    (r"\b(uska|iska|unka)\s+\d+\s+(baaki|baki)\b", "add_udhaar", 0.95),
    
    # ===== Payment patterns =====
    (r"\b(received|mila|paid back|repaid|settled)\b.*\d+", "add_payment", 0.95),
    (r"\b(recieved|recived|recevied)\b.*\d+", "add_payment", 0.95),  # Common misspellings
    (r"\d+.*\b(received|mila)\b", "add_payment", 0.90),
    # "Ramesh ne 200 diye" patterns
    (r"\b[A-Z][a-z]+\b.*\bne\b.*\d+.*\b(diye|diya)\b", "add_payment", 0.95),
    (r"\d+.*\b(rupay|rupees|rs)\b.*\b(diye|diya)\b", "add_payment", 0.95),
    # Voice patterns for payment
    (r"\b(paisa|paise|payment)\s+(aa\s*gaya|mil\s*gaya|aaya)\b", "add_payment", 0.95),
    (r"\b[A-Z][a-z]+\s+ne\s+(payment|paisa)\s+(diya|kiya)\b", "add_payment", 0.98),
    
    # ===== Query patterns - ledger first (more specific) =====
    (r"\b(show|dikhao)\b.*\bledger\b", "query_ledger", 0.98),
    (r"\bledger\b", "query_ledger", 0.95),
    (r"\b(show|dikhao|list|kitna)\b.*\bsummary\b", "query_summary", 0.95),
    (r"\bwho\s+owes\b", "query_udhaar", 1.0),
    # "kaun kitna dena/lena hai" patterns for query_udhaar
    (r"\bkaun\s+kitna\s+(dena|lena)\b", "query_udhaar", 0.98),
    (r"\bkitna\s+(dena|lena)\s+hai\b", "query_udhaar", 0.95),
    (r"\budhaar\s+(list|dikhao)\b", "query_udhaar", 0.95),
    # Voice patterns for queries
    (r"\b(sabka|sab\s*ka)\s+(hisab|udhaar|baaki)\b", "query_udhaar", 0.98),
    (r"\b(sabka|sab\s*ka)\s+.*\b(dikhao|batao|dekhna)\b", "query_udhaar", 0.98),
]


def rule_based_classifier(text: str) -> tuple[str, float]:
    """
    Enhanced rule-based classifier with confidence scores.
    
    Returns (intent, confidence) tuple.
    Returns (None, 0.0) if no rule matches.
    """
    t = text.lower()
    original = text  # Keep original for case-sensitive patterns
    
    # 1. Check priority patterns first (high confidence matches)
    for pattern, intent, confidence in PRIORITY_PATTERNS:
        if re.search(pattern, t, re.IGNORECASE):
            return (intent, confidence)
    
    # 2. Keyword scoring
    scores = {}
    for intent, keywords in RULE_KEYWORDS.items():
        score = 0.0
        matched_keywords = []
        for k in keywords:
            if k in t:
                score += 1.0
                matched_keywords.append(k)
                # Bonus for exact word matches (with word boundaries)
                if re.search(rf'\b{re.escape(k)}\b', t):
                    score += 0.5
        if score > 0:
            scores[intent] = (score, matched_keywords)

    if not scores:
        return (None, 0.0)

    # 3. Resolve conflicts with heuristics
    
    # Special logic for udhaar vs sale
    if "add_udhaar" in scores and "add_sale" in scores:
        # If text contains customer name + amount + date indicators, prefer udhaar
        has_name = bool(re.search(r'\b[A-Z][a-z]{2,}\b', original))
        has_amount = bool(re.search(r'\d+', t))
        # Explicit udhaar keyword is stronger
        if any(kw in t for kw in ["udhaar", "udhar", "credit", "loan", "baaki"]):
            return ("add_udhaar", 0.95)
        if has_name and has_amount:
            return ("add_udhaar", 0.85)
    
    # Sale vs purchase disambiguation
    if "add_sale" in scores and "add_purchase" in scores:
        # "to" indicates sale, "from" indicates purchase
        if " to " in t or " ko " in t:
            return ("add_sale", 0.90)
        if " from " in t or " se " in t:
            return ("add_purchase", 0.90)
    
    # Payment vs udhaar disambiguation  
    if "add_payment" in scores and "add_udhaar" in scores:
        # "received", "mila", "paid back" indicate payment
        if any(kw in t for kw in ["received", "mila", "paid back", "repaid", "settled", "cleared"]):
            return ("add_payment", 0.95)
    
    # Expense vs purchase disambiguation
    if "add_expense" in scores and "add_purchase" in scores:
        # Fuel, rent, salary are always expenses
        expense_keywords = ["fuel", "petrol", "diesel", "rent", "salary", "wages", "electricity"]
        if any(kw in t for kw in expense_keywords):
            return ("add_expense", 0.95)
        # Stock, inventory, resale indicate purchase
        purchase_keywords = ["stock", "inventory", "resale", "wholesale"]
        if any(kw in t for kw in purchase_keywords):
            return ("add_purchase", 0.95)
    
    # 4. Return highest scoring intent with normalized confidence
    best_intent = max(scores, key=lambda x: scores[x][0])
    max_score = scores[best_intent][0]
    
    # Normalize confidence (cap at 0.95 for keyword-only matches)
    confidence = min(0.95, 0.5 + (max_score * 0.15))
    
    return (best_intent, confidence)


# Confidence threshold for skipping LLM
RULE_CONFIDENCE_THRESHOLD = 0.85


# --- Main classify function (optimized) ---
@time_node
def classify_intent(state: AgentState) -> AgentState:
    text = _extract_text_from_state(state)
    if not text:
        state["intent"] = "unknown"
        state["intent_confidence"] = 0.0
        state["intent_reason"] = "no text"
        return state

    # 0) DIRECT BUTTON ID CHECK - Interactive button clicks come as their ID
    # These are direct menu button IDs from WhatsApp interactive messages
    direct_button_intents = [
        "menu_add_customer", "menu_add_expense", "menu_show_ledger",
        "menu_show_summary", "menu_udhaar_list", "menu_help", "menu_request"
    ]
    text_stripped = text.strip()
    if text_stripped in direct_button_intents:
        state["intent"] = text_stripped
        state["intent_confidence"] = 1.0
        state["intent_reason"] = "button_click"
        # Set conversation mode for follow-up context
        if text_stripped == "menu_add_customer":
            state["context"] = state.get("context", {})
            state["context"]["last_menu"] = "add_customer"
        elif text_stripped == "menu_add_expense":
            state["context"] = state.get("context", {})
            state["context"]["last_menu"] = "add_expense"
        return state

    # 0.5) CHECK CONTEXT FROM PREVIOUS MENU SELECTION
    # If user just selected a menu option and now types something short,
    # interpret it based on the menu context
    context = state.get("context", {})
    last_menu = context.get("last_menu", "")
    text_lower = text.lower().strip()
    
    if last_menu and len(text_stripped) < 50:
        # User selected "add_customer" menu and now typed a name
        if last_menu == "add_customer":
            # Check if it looks like a name (not a number, not a command)
            if not text_stripped.isdigit() and not any(kw in text_lower for kw in ["menu", "help", "ledger", "summary"]):
                # Treat as customer name for udhaar
                state["intent"] = "add_udhaar"
                state["intent_confidence"] = 0.9
                state["intent_reason"] = "context_menu_add_customer"
                # Pre-populate customer name
                state["entities"] = {"entries": [{"customer": text_stripped.title()}]}
                # Clear the menu context
                context["last_menu"] = ""
                state["context"] = context
                return state
        
        # User selected "add_expense" menu and now typed something
        elif last_menu == "add_expense":
            # Check if it's a number (amount)
            amount_match = re.search(r'(\d+)', text_stripped)
            if amount_match:
                state["intent"] = "add_expense"
                state["intent_confidence"] = 0.9
                state["intent_reason"] = "context_menu_add_expense"
                state["entities"] = {"entries": [{"amount": float(amount_match.group(1))}]}
                context["last_menu"] = ""
                state["context"] = context
                return state

    # Clear menu context if user types something else
    if last_menu:
        context["last_menu"] = ""
        state["context"] = context

    # 1) GUARDRAILS CHECK - Safety and topic filtering
    
    # Check for blocked content (inappropriate)
    is_blocked, block_reason = is_blocked_content(text)
    if is_blocked:
        state["intent"] = "blocked"
        state["intent_confidence"] = 1.0
        state["intent_reason"] = f"blocked: {block_reason}"
        state["is_blocked"] = True
        return state
    
    # Check for menu selection (1-6 or a-f)
    is_menu, menu_intent = is_menu_selection(text)
    if is_menu:
        state["intent"] = menu_intent
        state["intent_confidence"] = 1.0
        state["intent_reason"] = "menu_selection"
        state["conversation_mode"] = "menu"
        return state
    
    # Check for menu request
    if text_lower in ['menu', 'help', 'madad', 'options', 'kya kar sakta hai', 'what can you do']:
        state["intent"] = "menu_request"
        state["intent_confidence"] = 1.0
        state["intent_reason"] = "menu_request"
        state["show_menu"] = True
        return state
    
    # Check for casual chat indicators (short non-business messages)
    # BUT only if it's clearly casual (greetings, thanks, etc.) - not just short text
    casual_patterns = [
        r'^(hi|hello|hey|namaste|namaskar)(\s|$|\!)',
        r'^(thank|thanks|shukriya|dhanyavad)',
        r'^(bye|goodbye|alvida|tata|see you)',
        r'^(kya chal|kya haal|sab theek|how are)',
        r'^(ok|okay|theek|accha)(\s+hai)?$',
    ]
    for pattern in casual_patterns:
        if re.match(pattern, text_lower):
            state["intent"] = "casual_chat"
            state["intent_confidence"] = 0.9
            state["intent_reason"] = "casual_pattern"
            state["show_menu"] = True  # Show menu after casual response
            return state

    # 1) deterministic rules (returns tuple of intent, confidence)
    rb_intent, rb_confidence = rule_based_classifier(text)
    
    # If rule-based classifier has high confidence, skip LLM entirely
    if rb_intent and rb_confidence >= RULE_CONFIDENCE_THRESHOLD:
        state["intent"] = rb_intent
        state["intent_confidence"] = rb_confidence
        state["intent_reason"] = "rule-based"
        return state

    # 2) LLM fallback (only for low-confidence or no rule match)
    prompt = (
        f'Classify the message into ONE of {INTENTS}. '
        "Respond ONLY with JSON: {\"intent\":\"<label>\", \"confidence\":<0-1>, \"reason\":\"<short>\"}\n\n"
        f'User message: "{text}"\n'
    )
    try:
        response = groq_chat(prompt, temperature=0)
    except TypeError:
        response = groq_chat(prompt)
    parsed = _extract_json_from_text(response)

    intent = parsed.get("intent")
    confidence = parsed.get("confidence")
    reason = parsed.get("reason")

    if isinstance(intent, str):
        intent = intent.strip()
        mapping = {i.lower(): i for i in INTENTS}
        intent = mapping.get(intent.lower(), None)

    # If LLM failed but we had a rule-based result with lower confidence, use it
    if intent is None and rb_intent:
        state["intent"] = rb_intent
        state["intent_confidence"] = rb_confidence
        state["intent_reason"] = "rule-based-fallback"
        return state

    # final simple heuristics fallback if still None
    if intent is None:
        low = text.lower()
        if any(w in low for w in ("sold", "sale")):
            intent = "add_sale"
        elif any(w in low for w in ("buy", "bought", "purchase", "kharida")):
            intent = "add_purchase"
        elif any(w in low for w in ("udhaar", "udhar", "loan")):
            intent = "add_udhaar"
        elif any(w in low for w in ("paid back", "repaid", "received")):
            intent = "add_payment"
        elif any(w in low for w in ("summary", "total", "profit")):
            intent = "query_summary"
        elif any(w in low for w in ("ledger", "transactions")):
            intent = "query_ledger"
        elif any(w in low for w in ("hi", "hello", "namaste")):
            intent = "greeting"
        else:
            intent = "unknown"
        confidence = confidence if confidence is not None else 0.45
        reason = reason or "heuristic fallback"

    try:
        confidence = float(confidence)
        confidence = max(0.0, min(1.0, confidence))
    except Exception:
        confidence = 0.8 if intent != "unknown" else 0.45

    state["intent"] = intent
    state["intent_confidence"] = confidence
    state["intent_reason"] = reason or ""
    return state


EDGE_TESTS: List[Dict[str, str]] = [
    # === Basic text commands ===
    {"text": "Fuel 200", "expect": "add_expense"},
    {"text": "Petrol bharwaya 500", "expect": "add_expense"},
    {"text": "Bought 700 ka stock", "expect": "add_purchase"},
    {"text": "Sold 2500 to Ramesh", "expect": "add_sale"},
    {"text": "Aman ko udhaar 500 diya", "expect": "add_udhaar"},
    {"text": "Aman returned 300", "expect": "add_payment"},
    {"text": "Add a note about festival discount", "expect": "add_note"},
    {"text": "Show today's summary", "expect": "query_summary"},
    {"text": "Show ledger Ramesh", "expect": "query_ledger"},
    {"text": "Who owes me?", "expect": "query_udhaar"},
    {"text": "Hi", "expect": "greeting"},
    
    # === Typos and variations ===
    {"text": "fuell 200", "expect": "add_expense"}, 
    {"text": "purchese 300", "expect": "add_purchase"},
    {"text": "udhar 500", "expect": "add_udhaar"},
    {"text": "Paid 500 😂😂", "expect": "add_payment"},
    
    # === Voice transcription patterns ===
    {"text": "मुझे आज का हिसाब देखना है", "expect": "query_summary"},
    {"text": "aaj ka hisab dikhao", "expect": "query_summary"},
    {"text": "mujhe hisab dekhna hai", "expect": "query_summary"},
    {"text": "kitna hua aaj", "expect": "query_summary"},
    {"text": "total kitna hai", "expect": "query_summary"},
    {"text": "Ramesh ne udhaar liya 500", "expect": "add_udhaar"},
    {"text": "paisa aa gaya 1000", "expect": "add_payment"},
    {"text": "maal liya 2000 ka", "expect": "add_purchase"},
    {"text": "saman diya customer ko 500", "expect": "add_sale"},
    
    # === Image OCR patterns ===
    {"text": "Ramesh - 500", "expect": "add_udhaar"},
    {"text": "Mohan ke 1000", "expect": "add_udhaar"},
    {"text": "Total: 2500", "expect": "add_sale"},
    {"text": "Bill Amount = 1500", "expect": "add_sale"},
    
    # === Hindi/Hinglish variations ===
    {"text": "bijli ka bill 500", "expect": "add_expense"},
    {"text": "kiraya 5000", "expect": "add_expense"},
    {"text": "Maal kharida 2000", "expect": "add_purchase"},
    {"text": "Invoice 900 to Mohan", "expect": "add_sale"},
    {"text": "Packing material expense 100", "expect": "add_expense"},
    {"text": "Received 500 from Ramesh", "expect": "add_payment"},
    {"text": "uska 500 baaki hai", "expect": "add_udhaar"},
    {"text": "sabka hisab dikhao", "expect": "query_udhaar"},
    {"text": "kaun kitna dena hai", "expect": "query_udhaar"},
    
    # === Edge cases ===
    {"text": "200", "expect": "unknown"},
    {"text": "Bhai kal ka jo tha na 400 wala usko add kar dena", "expect": "unknown"},
]

if __name__ == "__main__":
    for t in EDGE_TESTS:
        s = AgentState(messages=[{"content": t["text"]}])
        out = classify_intent(s)
        print(f'{t["text"]!r} => {out["intent"]} (expect: {t["expect"]}) reason: {out["intent_reason"]} conf: {out["intent_confidence"]}')
