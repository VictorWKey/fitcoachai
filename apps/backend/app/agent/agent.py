"""
LangGraph agent implementation for fitness coaching.
Manages conversation flow, system message updates, and tool interactions for personalized training assistance.
"""

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import trim_messages, SystemMessage
from typing_extensions import TypedDict
from typing import Annotated, Union
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages.utils import count_tokens_approximately
from db.session import db_session
from db.crud.user import reset_system_message_update_flag, get_user_training_discipline
from agent.prompts import get_system_message
from db.models.workout import TrainingDiscipline
from langchain_core.runnables import RunnableConfig



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
        if isinstance(updates, list):
            return existing + updates
        elif isinstance(updates, dict) and updates["type"] == "manage_context":
            return trim_messages(
                existing,
                strategy="last",
                token_counter=count_tokens_approximately,
                max_tokens=10000,
                start_on="human",
                end_on=("human", "tool"),
                include_system=True,
            )

    class State(TypedDict):
        messages: Annotated[list, manage_list]
    
    async def update_system_message(state: State, config: RunnableConfig):
        """
        Updates the system message with the user's current discipline and resets the flag.
        
        Args:
            state: Current state containing message information
            config: Configuration containing user_id and other settings
            
        Returns:
            Updated state with new system message
        """
        user_id = config.get("configurable", {}).get("user_id")
        if not user_id:
            return state
        
        async with db_session() as db:
            # Get user's current discipline
            user_discipline = await get_user_training_discipline(db, user_id)
            if not user_discipline:
                user_discipline = TrainingDiscipline.HYPERTROPHY
            
            # Generate new system message based on current discipline
            new_system_message = get_system_message(user_discipline)
            
            # Update the messages list - replace existing system message or add if none exists
            messages = state.get("messages", [])
            updated_messages = []
            
            # Skip existing system message if present
            for msg in messages:
                if not isinstance(msg, SystemMessage):
                    updated_messages.append(msg)
            
            # Add new system message at the beginning
            updated_messages.insert(0, new_system_message)
            
            # Reset the flag
            await reset_system_message_update_flag(db, user_id)
        
        return {"messages": updated_messages}
    
    def should_update_system_message(state: State, config: RunnableConfig) -> str:
        """
        Conditional edge function to determine if system message should be updated.
        
        Args:
            state: Current state
            config: Configuration containing the system_message_needs_update flag
            
        Returns:
            Next node name based on whether system message needs update
        """
        needs_update = config.get("configurable", {}).get("system_message_needs_update", False)
        return "update_system_message" if needs_update else "prepare_llm_context"
    
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
        return {"messages": {"type": "manage_context"}}

    tool_node = ToolNode(tools=tools)

    graph_builder = StateGraph(State)
    
    # Add nodes (without redundant node)
    graph_builder.add_node("update_system_message", update_system_message)
    graph_builder.add_node("prepare_llm_context", prepare_llm_context)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    
    # Define edges (directly from START)
    graph_builder.add_conditional_edges(
        START,
        should_update_system_message,
        {
            "update_system_message": "update_system_message",
            "prepare_llm_context": "prepare_llm_context"
        }
    )
    graph_builder.add_edge("update_system_message", "prepare_llm_context")
    graph_builder.add_edge("prepare_llm_context", "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge("chatbot", END)
    
    agent = graph_builder.compile(checkpointer=checkpointer)
    return agent
