"""
Chat service for FitCoach AI API.

Provides AI agent interaction services including user input processing,
context retrieval, and response generation. Interfaces between API routes
and the LangChain agent.
"""

from langchain_core.messages import SystemMessage
from agent.prompts import SYSTEM_MESSAGE, USER_MESSAGE

async def process_agent(
    user_input: str, 
    config: dict, 
    agent
) -> dict:
    """
    Processes the user's input and gets a response from the agent.
    
    Args:
        user_input: The user's input text.
        config: Configuration for the agent.
        agent: Instance of the LLM agent.
        user_chat_history_exists: Indicates whether there is existing chat history.
        
    Returns:
        dict: The agent's response.
    """
    user_messages = USER_MESSAGE.format_messages(
        input=user_input
    )

    response = await agent.ainvoke(
        {"messages": user_messages},
        config=config
    )

    return response
