from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from .tools import TrainingLogTool
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import Annotated
from utils import save_graph_image
import os

def Agent():
    LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT = "fitcoachai"
    LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"

    OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
    MODEL_NAME = os.getenv("MODEL_NAME")

    class State(TypedDict):
        messages: Annotated[list, add_messages]

    tools = [TrainingLogTool]
    
    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=0,
        base_url=OLLAMA_API_BASE_URL
    ).bind_tools(tools)

    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    graph = graph_builder.compile()
    save_graph_image(graph, "./images/graph.png")

    return graph
