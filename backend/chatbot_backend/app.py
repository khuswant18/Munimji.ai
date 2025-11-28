from typing import TypedDict, Annotated
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")


model = ChatGoogleGenerativeAI(model="gemini-2.5-pro", api_key=google_api_key)


class State(TypedDict):
    messages: Annotated[list[BaseMessage], "Chat history"]


def call_model(state: State) -> State:
    response = model.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}


graph = StateGraph(State)

graph.add_node("model", call_model)

graph.add_edge(START, "model")
graph.add_edge("model", END)


graph = graph.compile() 



