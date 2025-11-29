import sys
from backend.agents.graph import compiled_graph
from langchain_core.messages import HumanMessage

message = sys.argv[1] if len(sys.argv) > 1 else input("Enter message: Add 200 rs as udhaar")

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

result = compiled_graph.invoke(initial_state)

print("Intent:", result["intent"])
print("Entities:", result["entities"])
print("Context:", result["context"])
print("Response:", result["response"])