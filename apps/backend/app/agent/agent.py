"""
LangGraph agent implementation for FitCoach AI.

This module contains the core agent logic using LangGraph, including state management,
message handling, and tool integration for the fitness coaching assistant.
"""

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import trim_messages
from typing_extensions import TypedDict
from typing import Annotated, Union
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages.utils import count_tokens_approximately
from agent.prompts import SYSTEM_MESSAGE

def get_agent(llm, checkpointer, tools):
    """
    Constructs a LangGraph agent using an LLM, a checkpointer, and a set of tools.

    Args:
        llm: A language model object that supports async invocation via `ainvoke`.
        checkpointer: An object used to manage state checkpointing.
        tools: A list of tools to be used by the ToolNode.

    Returns:
        A compiled LangGraph agent.
    """
    def manage_list(existing: list, updates: Union[list, dict]):
        """
        Manages the conversation message list, either appending new messages or trimming
        them based on token constraints.

        Args:
            existing: The current list of messages.
            updates: Either a list of new messages or a dict signaling context management.

        Returns:
            The updated message list.
        """
        if isinstance(updates, dict):
            if updates.get("type") == "manage_context":
                return trim_messages(
                    existing,
                    strategy="last",
                    token_counter=count_tokens_approximately,
                    max_tokens=10000,
                    start_on="human",
                    end_on=("human", "tool"),
                    include_system=True,
                )
            elif updates.get("type") == "replace_all":
                # Reemplazar completamente los mensajes
                return updates.get("messages", [])
        
        # Por defecto, agregamos los mensajes
        return existing + updates if isinstance(updates, list) else existing

    class State(TypedDict):
        messages: Annotated[list, manage_list]
    
    async def chatbot(state: State):
        """
        Invokes the LLM asynchronously using the message history in the state.

        Args:
            state: A dictionary containing the message history.

        Returns:
            A dictionary with the LLM's response appended to the message list.
        """
        return {"messages": [await llm.ainvoke(state["messages"])]}
    
    async def prepare_llm_context(state: State):
        """
        Triggers the context management logic before sending messages to the LLM.

        Args:
            state: A dictionary containing the message history.

        Returns:
            A dictionary signaling that context should be managed.
        """
        if len(state["messages"]) == 1:
            # Para el primer mensaje, reemplazamos completamente el estado
            # con el mensaje del sistema seguido del mensaje del usuario
            return {
                "messages": {
                    "type": "replace_all",
                    "messages": [SYSTEM_MESSAGE] + state["messages"]
                }
            }
        
        # Verificamos si necesitamos gestionar el contexto por longitud
        if len(state["messages"]) > 10:
            return {"messages": {"type": "manage_context"}}
            
        # Si no se necesita hacer nada, devolvemos los mensajes sin cambios
        return {"messages": []}

    tool_node = ToolNode(tools=tools)

    graph_builder = StateGraph(State)
    graph_builder.add_node("prepare_llm_context", prepare_llm_context)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_edge(START, "prepare_llm_context")
    graph_builder.add_edge("prepare_llm_context", "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    agent = graph_builder.compile(checkpointer=checkpointer)
    return agent
