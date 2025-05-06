# agent_builder.py (o como lo tengas)
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from typing_extensions import TypedDict
from typing import Annotated
from agent.tools import log_exercise
from langchain_ollama import ChatOllama
import os

DATABASE_URL = os.getenv("DATABASE_URL") + "?sslmode=disable"
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

conn = Connection.connect(DATABASE_URL, **connection_kwargs)
checkpointer = PostgresSaver(conn)
checkpointer.setup()

class State(TypedDict):
    messages: Annotated[list, add_messages]

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
    base_url=OLLAMA_API_BASE_URL,
)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

tools = [log_exercise]  # si usas herramientas

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
agent = graph_builder.compile(checkpointer=checkpointer)

def get_agent():
    return agent
