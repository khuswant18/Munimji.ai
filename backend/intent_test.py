from backend.agents.nodes.classify import classify_intent
from backend.agents.state import AgentState 

state = AgentState(text="fuel 200")
output = classify_intent(state)
print(output["intent"])  