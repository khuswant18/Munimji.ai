"""
Optimized search_notes node with caching and efficient queries.
"""
from ..state import AgentState
from ...vectorstore.search import search_vectorstore
from ...chatbot_backend.db.session import get_db
from ...chatbot_backend.db.queries import get_daily_summary, get_inventory_stock
from ...decorators.timeit import time_node, timed_context

@time_node
def search_notes(state: AgentState) -> AgentState:
    entities = state.get("entities", {})
    intent = state["intent"]
    user_id = state["user_id"] or 1
    
    # Initialize context if not present
    if "context" not in state or state["context"] is None:
        state["context"] = {}

    db = next(get_db())
    try:
        with timed_context("db_query"):
            if intent == "query_summary":
                query_type = entities.get("query_type", "daily")
                if "daily" in str(query_type):
                    total = get_daily_summary(db, user_id)
                    result = f"📊 Today's total: ₹{total}"
                else:
                    result = "Summary not available for this period."
                    
            elif intent == "query_udhaar":
                # TODO: Implement efficient udhaar query
                customer = entities.get("customer") if entities else None
                if customer:
                    result = f"Udhaar for {customer}: Checking..."
                else:
                    result = "📋 Udhaar list: Use 'udhaar [name]' for specific customer."
                    
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
        state["context"]["search_results"] = f"Search error: {str(e)}"
    finally:
        db.close()

    return state 

