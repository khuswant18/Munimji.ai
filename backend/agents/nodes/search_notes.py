"""
Optimized search_notes node with caching and efficient queries.
"""
from ..state import AgentState
from backend.vectorstore.search import search_vectorstore
from backend.chatbot_backend.db.session import get_db
from backend.chatbot_backend.db.queries import get_daily_summary, get_detailed_daily_summary, get_all_udhaar_list, get_inventory_stock
from backend.decorators.timeit import time_node, timed_context


def format_detailed_summary(summary: dict) -> str:
    """Format detailed summary for WhatsApp display."""
    lines = ["📊 *Aaj Ka Hisab*\n"]
    
    # Calculate totals
    total_in = summary["sale"]["total"] + summary["payment"]["total"]
    total_out = summary["purchase"]["total"] + summary["expense"]["total"] + summary["udhaar"]["total"]
    
    # Sales
    if summary["sale"]["total"] > 0:
        lines.append(f"🛒 *Sale:* ₹{summary['sale']['total']:,.0f} ({summary['sale']['count']} entries)")
    
    # Purchases
    if summary["purchase"]["total"] > 0:
        lines.append(f"📦 *Purchase:* ₹{summary['purchase']['total']:,.0f} ({summary['purchase']['count']} entries)")
    
    # Expenses
    if summary["expense"]["total"] > 0:
        lines.append(f"💸 *Expense:* ₹{summary['expense']['total']:,.0f} ({summary['expense']['count']} entries)")
    
    # Payments received
    if summary["payment"]["total"] > 0:
        lines.append(f"💰 *Payment Received:* ₹{summary['payment']['total']:,.0f}")
    
    # Udhaar given
    if summary["udhaar"]["total"] > 0:
        lines.append(f"📝 *Udhaar Diya:* ₹{summary['udhaar']['total']:,.0f} ({summary['udhaar']['count']} entries)")
        
        # Show who took udhaar
        if summary.get("udhaar_details"):
            lines.append("\n👥 *Udhaar Details:*")
            for item in summary["udhaar_details"][:5]:
                lines.append(f"  • {item['name']}: ₹{item['amount']:,.0f}")
    
    # Net summary
    lines.append("\n" + "─" * 20)
    lines.append(f"📥 *Total In:* ₹{total_in:,.0f}")
    lines.append(f"📤 *Total Out:* ₹{total_out:,.0f}")
    
    net = total_in - total_out
    if net >= 0:
        lines.append(f"✅ *Net Profit:* ₹{net:,.0f}")
    else:
        lines.append(f"⚠️ *Net Loss:* ₹{abs(net):,.0f}")
    
    # Recent entries
    if summary.get("recent"):
        lines.append("\n📋 *Recent Entries:*")
        for entry in summary["recent"][:3]:
            type_emoji = {"sale": "🛒", "purchase": "📦", "expense": "💸", "udhaar": "📝", "payment": "💰"}.get(entry["type"], "•")
            desc = entry["description"][:20] + "..." if len(entry["description"]) > 20 else entry["description"]
            lines.append(f"  {type_emoji} ₹{entry['amount']:,.0f} - {desc}")
    
    return "\n".join(lines)


def format_udhaar_list(udhaar_list: list) -> str:
    """Format udhaar list for WhatsApp display."""
    if not udhaar_list:
        return "✅ *Kisi ka bhi udhaar pending nahi hai!*\n\nSab clear hai! 🎉"
    
    lines = ["📋 *Udhaar List - Kaun Kitna Dena Hai*\n"]
    
    total = 0
    for i, item in enumerate(udhaar_list[:15], 1):
        lines.append(f"{i}. *{item['name']}*: ₹{item['balance']:,.0f}")
        total += item['balance']
    
    if len(udhaar_list) > 15:
        lines.append(f"\n... aur {len(udhaar_list) - 15} log")
    
    lines.append("\n" + "─" * 20)
    lines.append(f"💰 *Total Pending:* ₹{total:,.0f}")
    
    return "\n".join(lines)


@time_node
def search_notes(state: AgentState) -> AgentState:
    entities = state.get("entities", {})
    intent = state["intent"]
    user_id = state.get("user_id") or 1
    
    # Initialize context if not present
    if "context" not in state or state["context"] is None:
        state["context"] = {}

    db = next(get_db())
    try:
        with timed_context("db_query"):
            if intent == "query_summary" or intent == "menu_show_summary":
                # Get detailed summary
                summary = get_detailed_daily_summary(db, user_id)
                result = format_detailed_summary(summary)
                    
            elif intent == "query_udhaar" or intent == "menu_udhaar_list":
                # Get full udhaar list
                udhaar_list = get_all_udhaar_list(db, user_id)
                result = format_udhaar_list(udhaar_list)
                    
            elif intent == "query_ledger" or intent == "menu_show_ledger":
                # Get today's entries
                from sqlalchemy import func
                from backend.dashboard.models import LedgerEntry
                
                today = func.current_date()
                entries = db.query(LedgerEntry).filter(
                    LedgerEntry.user_id == user_id,
                    func.date(LedgerEntry.created_at) == today
                ).order_by(LedgerEntry.created_at.desc()).limit(20).all()
                
                if entries:
                    lines = ["📒 *Aaj Ki Entries*\n"]
                    for entry in entries:
                        type_emoji = {"sale": "🛒", "purchase": "📦", "expense": "💸", "udhaar": "📝", "payment": "💰"}.get(entry.type, "•")
                        desc = entry.description or entry.counterparty_name or entry.type
                        desc = desc[:25] + "..." if len(desc) > 25 else desc
                        lines.append(f"{type_emoji} ₹{entry.amount:,.0f} - {desc}")
                    result = "\n".join(lines)
                else:
                    result = "📒 Aaj ki koi entry nahi hai. Pehli entry add karo!"
                    
            else:
                # Fallback to vectorstore search
                try:
                    last_msg = state["messages"][-1]
                    if hasattr(last_msg, "content"):
                        default_query = last_msg.content
                    elif isinstance(last_msg, dict) and "content" in last_msg:
                        default_query = last_msg["content"]
                    else:
                        default_query = str(last_msg)
                except:
                    default_query = ""
                
                query = entities.get("query", default_query) if entities else default_query
                
                with timed_context("vectorstore_search"):
                    results = search_vectorstore(query)
                    
                if results:
                    result = "; ".join([r.page_content for r in results[:3]])
                else:
                    result = "No matching records found."

        state["context"]["search_results"] = result
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        state["context"]["search_results"] = f"Search error: {str(e)}"
    finally:
        db.close()

    return state

