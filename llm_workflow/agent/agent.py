# agent_builder.py (o como lo tengas)
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection
from typing_extensions import TypedDict
from typing import Annotated
from agent.tools import log_exercise
from langchain_ollama import ChatOllama
import os
from typing import Optional
from langchain_core.messages import trim_messages

from typing import Union


agents = {}

async def get_agent():
    DATABASE_URL = os.getenv("DATABASE_URL") + "?sslmode=disable"
    OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
    MODEL_NAME = os.getenv("MODEL_NAME")

    connection_kwargs = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    conn = await AsyncConnection.connect(DATABASE_URL, **connection_kwargs)
    checkpointer = AsyncPostgresSaver(conn)
    await checkpointer.setup()
    
    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=0,
        base_url=OLLAMA_API_BASE_URL,
    )
    
    def manage_list(existing: list, updates: Union[list, dict]):
        if isinstance(updates, list):
            return existing + updates
        elif isinstance(updates, dict) and updates["type"] == "keep":
            return trim_messages(
                existing,
                strategy="last",
                token_counter=llm,
                max_tokens=500,
                start_on="human",
                end_on=("human", "tool"),
                include_system=True,
            )

    class State(TypedDict):
        messages: Annotated[list, manage_list]
    
    async def chatbot(state: State):
        return {"messages": [await llm.ainvoke(state["messages"])]}
    
    async def prepare_llm_context(state: State):
        return {"messages": {"type": "keep"}}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("prepare_llm_context", prepare_llm_context)
    graph_builder.add_edge(START, "prepare_llm_context")
    graph_builder.add_edge("prepare_llm_context", "chatbot")
    graph_builder.add_edge("chatbot", END)
    agent = graph_builder.compile(checkpointer=checkpointer)
    print(agent.get_graph().draw_mermaid())    
    
    return agent

