# agent/agent.py
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import trim_messages
from typing_extensions import TypedDict
from typing import Annotated, Union

def get_agent(llm, checkpointer):
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
        return {"messages": {"type": "keep", "from": -3, "to": None}}

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("prepare_llm_context", prepare_llm_context)
    graph_builder.add_edge(START, "prepare_llm_context")
    graph_builder.add_edge("prepare_llm_context", "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    agent = graph_builder.compile(checkpointer=checkpointer)
    return agent
