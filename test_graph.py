import sys
from backend.agents.graph import compiled_graph
from langchain_core.messages import HumanMessage

# Get message from command line or prompt
message = sys.argv[1] if len(sys.argv) > 1 else input("Enter message: Add 200 rs as udhaar")

# Prepare initial state (same as in app.py)
initial_state = {
    "messages": [HumanMessage(content=message)],
    "intent": "",
    "entities": {},
    "context": {},
    "response": "",
    "user_id": 1,
    "missing_slots": [],
    "needs_followup": False,
    "route": ""
}

# Invoke the graph
result = compiled_graph.invoke(initial_state)

# Print the response and key details
print("Intent:", result["intent"])
print("Entities:", result["entities"])
print("Context:", result["context"])
print("Response:", result["response"])