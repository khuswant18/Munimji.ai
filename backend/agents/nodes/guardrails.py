"""
Safety Guardrails for Munimji - Professional Shopkeeper Assistant

This module filters inappropriate content and ensures the bot only handles
shop/business related queries.
"""
import re
from typing import Tuple

# Blocked topics - the bot should NOT engage with these
BLOCKED_PATTERNS = [
    # Adult/inappropriate content
    r'\b(sex|porn|nude|naked|xxx|adult|erotic|hot\s*girl|hot\s*boy|dating|hookup)\b',
    r'\b(sexy|horny|fuck|dick|pussy|boob|breast|ass|butt)\b',
    
    # Violence/illegal
    r'\b(kill|murder|bomb|terrorist|hack|drug|cocaine|heroin|weed|ganja)\b',
    r'\b(weapon|gun|pistol|rifle|knife\s*attack)\b',
    
    # Scams/fraud
    r'\b(lottery|jackpot|free\s*money|get\s*rich|mlm|ponzi|scam)\b',
    
    # Personal/romantic
    r'\b(girlfriend|boyfriend|date\s*me|marry\s*me|love\s*you|kiss)\b',
    
    # Gambling
    r'\b(satta|matka|betting|gamble|casino|poker)\b',
    
    # Political/religious sensitive
    r'\b(vote\s*for|election|party\s*politics)\b',
    
    # Medical advice (redirect to doctor)
    r'\b(medicine\s*for|cure\s*for|treatment\s*for|diagnosis)\b',
    
    # Legal advice (redirect to lawyer)
    r'\b(sue|lawsuit|legal\s*action|court\s*case)\b',
]

# Compile patterns for efficiency
BLOCKED_REGEX = re.compile('|'.join(BLOCKED_PATTERNS), re.IGNORECASE)

# Business-related keywords that indicate valid queries
BUSINESS_KEYWORDS = [
    # Money/transactions
    'rupee', 'rupay', 'rupiya', 'paisa', 'rs', '₹', 'amount', 'price', 'cost',
    'payment', 'paid', 'received', 'udhaar', 'udhar', 'credit', 'debit',
    'hisab', 'khata', 'baki', 'baaki', 'loan', 'lena', 'dena',
    
    # Actions
    'add', 'jod', 'daal', 'entry', 'record', 'note', 'likh', 'save',
    'show', 'dikhao', 'batao', 'list', 'summary', 'total', 'report',
    'delete', 'edit', 'update', 'change', 'cancel',
    
    # Business entities
    'customer', 'grahak', 'supplier', 'vendor', 'party', 'shop', 'dukaan',
    'stock', 'inventory', 'maal', 'item', 'product', 'sale', 'bikri',
    'purchase', 'khareed', 'expense', 'kharcha', 'profit', 'loss',
    
    # Quantities
    'kg', 'gram', 'liter', 'piece', 'packet', 'dozen', 'box', 'carton',
    
    # Time references
    'today', 'aaj', 'yesterday', 'kal', 'week', 'month', 'mahina',
    
    # Greetings (allowed)
    'hello', 'hi', 'hey', 'namaste', 'namaskar', 'good morning', 'good evening',
    
    # Help/menu
    'help', 'madad', 'menu', 'options', 'kya kar', 'kaise', 'how',
]

# Menu selection patterns
MENU_PATTERNS = {
    '1': 'menu_add_customer',
    '2': 'menu_add_expense', 
    '3': 'menu_show_ledger',
    '4': 'menu_show_summary',
    '5': 'menu_udhaar_list',
    '6': 'menu_help',
    'a': 'menu_add_customer',
    'b': 'menu_add_expense',
    'c': 'menu_show_ledger',
    'd': 'menu_show_summary',
    'e': 'menu_udhaar_list',
    'f': 'menu_help',
}


def is_blocked_content(text: str) -> Tuple[bool, str]:
    """
    Check if the text contains blocked/inappropriate content.
    
    Returns:
        (is_blocked, reason)
    """
    if BLOCKED_REGEX.search(text):
        return True, "inappropriate_content"
    return False, ""


def is_business_related(text: str) -> bool:
    """
    Check if the text is related to business/shop operations.
    """
    text_lower = text.lower()
    
    # Check for business keywords
    for keyword in BUSINESS_KEYWORDS:
        if keyword in text_lower:
            return True
    
    # Check for numbers (amounts, quantities)
    if re.search(r'\d+', text):
        return True
    
    # Short messages might be menu selections or follow-ups
    if len(text.strip()) < 30:
        return True
    
    return False


def is_menu_selection(text: str) -> Tuple[bool, str]:
    """
    Check if the text is a menu selection (1-6 or a-f).
    
    Returns:
        (is_menu, menu_intent)
    """
    text = text.strip().lower()
    
    # Direct number/letter selection
    if text in MENU_PATTERNS:
        return True, MENU_PATTERNS[text]
    
    # "Option 1", "1 select", etc.
    match = re.match(r'^(?:option\s*)?([1-6a-f])(?:\s*select)?$', text)
    if match:
        key = match.group(1)
        if key in MENU_PATTERNS:
            return True, MENU_PATTERNS[key]
    
    return False, ""


def get_blocked_response() -> str:
    """Get standard response for blocked content."""
    return """🚫 Main sirf dukaan ke kaam mein madad kar sakta hoon."""


def get_off_topic_response() -> str:
    """Get response for off-topic but not blocked content."""
    return """🤔 Yeh meri expertise mein nahi hai. Main ek shopkeeper assistant hoon.

Main aapki madad kar sakta hoon:
• Hisab-kitab (ledger entries)
• Udhaar manage karna  
• Sale/purchase record
• Expense tracking"""


MAIN_MENU = """📋 *Munimji Menu*

Kya karna hai? Number ya option choose karo:

1️⃣ *Naya Customer/Udhaar Add* - "Ramesh ke 500 udhaar"
2️⃣ *Expense Add* - "100 ka petrol"  
3️⃣ *Ledger Dikhao* - Aaj ki entries
4️⃣ *Summary* - Total hisab
5️⃣ *Udhaar List* - Kaun kitna dena hai
6️⃣ *Help* - Kaise use kare

Ya seedha likh do jaise: "Mohan ko 200 ki cheeni bechi"
"""


def get_main_menu() -> str:
    """Get the main menu text."""
    return MAIN_MENU


# Quick action patterns for direct commands
QUICK_ACTION_PATTERNS = [
    # Direct udhaar: "Ramesh ke 500 udhaar"
    (r'(\w+)\s+(?:ke|ka|ki)\s+(\d+)\s*(?:rs|rupee|rupay|₹)?\s*(?:udhaar|udhar|credit)', 'add_udhaar'),
    
    # Direct sale: "Mohan ko 200 ki cheeni bechi"
    (r'(\w+)\s+ko\s+(\d+).*(?:bech|sold|sale)', 'add_sale'),
    
    # Direct expense: "100 ka petrol"
    (r'(\d+)\s*(?:rs|rupee|₹|ka|ki)?\s*(petrol|diesel|rent|bijli|electricity)', 'add_expense'),
    
    # Add entry: "5 pen add karo"
    (r'(\d+)\s+(\w+)\s+(?:add|jod|daal)', 'add_inventory'),
]


def detect_quick_action(text: str) -> Tuple[bool, str, dict]:
    """
    Detect if message is a direct command that can be processed immediately.
    
    Returns:
        (is_quick_action, intent, extracted_entities)
    """
    text_lower = text.lower()
    
    for pattern, intent in QUICK_ACTION_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            return True, intent, {"match": match.groups()}
    
    return False, "", {}
