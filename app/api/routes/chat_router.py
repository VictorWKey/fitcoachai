# api/routes/chat_router.py
"""
Routes for chatting with the LLM agent.
"""

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated
from db.schemas.user import User
from api.services import get_current_verified_user, process_agent
from db.session import get_db
from db.models.user import User

chat_router = APIRouter(prefix="/chat", tags=["chat"])

class ChatInput(BaseModel):
    """
    Model for user chat input.

    Attributes:
        input (str): User's message to the LLM agent.
    """
    input: str

@chat_router.post("/")
async def chat(
    request: Request,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    chat_input: ChatInput
):
    """
    Endpoint to process chat messages with the LLM agent.

    Args:
        request (Request): FastAPI request object.
        current_user (User): Authenticated and verified user.
        chat_input (ChatInput): Chat message input from user.

    Returns:
        dict: Conversation messages including the agent's response.
    """
    config = {
        "configurable": {
            "thread_id": str(current_user.id),
            "user_id": current_user.id,
            "llm": request.app.state.llm
        }
    }   

    agent = request.app.state.agent

    user_chat_history = await request.app.state.checkpointer.aget_tuple(
        config=config
    )

    user_chat_history_exists = True if user_chat_history else False

    response = await process_agent(
        chat_input.input, 
        config, 
        agent,
        user_chat_history_exists
    )
    
    return response["messages"]
