# api/routes/chat_router.py
"""
Routes for chatting with the LLM agent.
"""

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated
from db.schemas.user import User
from api.services import get_current_verified_user, process_agent
from db.session import get_db
from db.models.user import User
from db.crud.chat_history import create_chat_history, get_user_chat_history, get_user_chat_history_after
from db.schemas.chat_history import ChatHistoryCreate
from typing import cast

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
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_input: ChatInput
):
    """
    Endpoint to process chat messages with the LLM agent.

    Args:
        request (Request): FastAPI request object.
        current_user (User): Authenticated and verified user.
        chat_input (ChatInput): Chat message input from user.
        db (AsyncSession): Database session.

    Returns:
        dict: Assistant's response.
    """
    
    config = {
        "configurable": {
            "thread_id": str(current_user.id),
            "user_id": current_user.id,
            "llm": request.app.state.llm
        }
    }   

    agent = request.app.state.agent
    
    response = await process_agent(
        chat_input.input, 
        config, 
        agent
    )
    
    # Extract the assistant's reply (last AI message)
    assistant_reply = None
    for msg in reversed(response["messages"]):
        if getattr(msg, "type", "") == "ai" or msg.__class__.__name__ == "AIMessage":
            assistant_reply = msg.content
            break

    # Store user and assistant messages in persistent chat history
    await create_chat_history(db, ChatHistoryCreate(
        user_id=cast(int, current_user.id),
        message=chat_input.input,
        is_user_message=True
    ))
    assistant_msg_obj = None
    if assistant_reply:
        assistant_msg_obj = await create_chat_history(db, ChatHistoryCreate(
            user_id=cast(int, current_user.id),
            message=assistant_reply,
            is_user_message=False
        ))

    return {
        "id": assistant_msg_obj.id if assistant_msg_obj else None,
        "role": "assistant",
        "content": assistant_reply,
        "created_at": assistant_msg_obj.created_at.isoformat() if assistant_msg_obj else None
    }

@chat_router.delete("/delete-memory")
async def delete_memory(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request
):
    """Delete all memory for the current user."""

    checkpointer = request.app.state.checkpointer

    await checkpointer.adelete_thread(str(current_user.id))

    return {"message": "Memory deleted successfully"}

@chat_router.get("/history")
async def get_chat_history(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    after_id: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Retrieve chat history for current user.

    If *after_id* > 0, only messages with id greater than *after_id* are returned
    (incremental fetch). Otherwise, returns the most recent *limit* messages.
    """
    if after_id > 0:
        history = await get_user_chat_history_after(db, cast(int, current_user.id), after_id, limit)
    else:
        history = await get_user_chat_history(db, cast(int, current_user.id), limit)

    # Map to simple dict format expected by frontend
    messages = [
        {
            "id": m.id,
            "role": "user" if cast(bool, m.is_user_message) else "assistant",
            "content": m.message,
            "created_at": m.created_at.isoformat() if cast(bool, m.created_at) else None
        }
        for m in history
    ]
    return messages
