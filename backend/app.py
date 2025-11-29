from fastapi import FastAPI
from pydantic import BaseModel
from .agents.graph import compiled_graph as graph  # Import the compiled graph
from langchain_core.messages import HumanMessage
from .chatbot_backend.db.session import get_db
from .chatbot_backend.db.models import Conversation
from sqlalchemy.orm import Session

class ChatRequest(BaseModel):
    message: str
    user_id: int = 1

app = FastAPI(title="Munimji Backend", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Welcome to Munimji Backend"}

# Add your API endpoints here
# For example, a chatbot endpoint that uses the LangGraph agent

@app.post("/chat")
async def chat(request: ChatRequest):
    message = request.message
    user_id = request.user_id
    db: Session = next(get_db())
    try:
        # Get or create conversation
        conversation = db.query(Conversation).filter(Conversation.user_id == user_id).first()
        if not conversation:
            conversation = Conversation(user_id=user_id, context={})
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # Load previous state from context
        previous_state = conversation.context or {}

        # Prepare initial state
        initial_state = {
            "messages": previous_state.get("messages", []) + [HumanMessage(content=message)],
            "intent": previous_state.get("intent", ""),
            "entities": previous_state.get("entities", {}),
            "context": previous_state.get("context", {}),
            "response": "",
            "user_id": user_id,
            "missing_slots": previous_state.get("missing_slots", []),
            "needs_followup": previous_state.get("needs_followup", False),
            "route": ""
        }

        # Invoke the graph
        result = graph.invoke(initial_state)

        # Save the new state to conversation
        conversation.context = {
            "messages": [m.dict() if hasattr(m, 'dict') else str(m) for m in result["messages"]],
            "intent": result["intent"],
            "entities": result["entities"],
            "context": result["context"],
            "missing_slots": result["missing_slots"],
            "needs_followup": result["needs_followup"]
        }
        conversation.last_message = message
        db.commit()

        return {"response": result["response"]}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.whatsapp.app:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
    )
