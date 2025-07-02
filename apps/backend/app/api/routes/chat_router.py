# api/routes/chat_router.py
"""
Routes for chatting with the LLM agent.
"""

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated
from api.services import get_current_verified_user, process_agent
from db.session import get_db
from db.models.user import User as UserModel
from db.crud.chat_history import create_chat_history, get_user_chat_history, get_user_chat_history_after
from db.crud.user import update_user_chat_history_status
from db.schemas.chat_history import ChatHistoryCreate

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
    current_user: Annotated[UserModel, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    chat_input: ChatInput
):
    """
    Endpoint to process chat messages with the LLM agent.

    Args:
        request (Request): FastAPI request object.
        current_user (UserModel): Authenticated and verified user.
        chat_input (ChatInput): Chat message input from user.
        db (AsyncSession): Database session.

    Returns:
        dict: Assistant's response.
    """
    user_id = getattr(current_user, 'id')
    config = {
        "configurable": {
            "thread_id": str(user_id),
            "user_id": user_id,
        }
    }   

    # OPTIMIZACIÓN: Usar has_chat_history del usuario en lugar de consultar checkpointer
    user_chat_history_exists = getattr(current_user, 'has_chat_history', False)
    
    # OPTIMIZACIÓN: Verificar si el system message necesita actualización usando el current_user
    # para evitar consulta adicional a la base de datos en el grafo
    system_message_needs_update = getattr(current_user, 'system_message_needs_update', False)
    
    # Si es la primera vez que el usuario chatea, actualizar el estado
    if not user_chat_history_exists:
        await update_user_chat_history_status(db, user_id)

    response = await process_agent(
        chat_input.input, 
        config, 
        request.app.state.llm_base,  # LLM base sin tools
        request.app.state.checkpointer,
        user_chat_history_exists,
        system_message_needs_update  # Pasar el flag directamente
    )
    
    # Extract the assistant's reply (last AI message)
    assistant_reply = None
    for msg in reversed(response["messages"]):
        if getattr(msg, "type", "") == "ai" or msg.__class__.__name__ == "AIMessage":
            assistant_reply = msg.content
            break

    # Store user and assistant messages in persistent chat history
    await create_chat_history(db, ChatHistoryCreate(
        user_id=user_id,
        message=chat_input.input,
        is_user_message=True
    ))
    assistant_msg_obj = None
    if assistant_reply:
        assistant_msg_obj = await create_chat_history(db, ChatHistoryCreate(
            user_id=user_id,
            message=assistant_reply,
            is_user_message=False
        ))

    return {
        "id": getattr(assistant_msg_obj, 'id', None) if assistant_msg_obj else None,
        "role": "assistant",
        "content": assistant_reply,
        "created_at": created_at.isoformat() if assistant_msg_obj and (created_at := getattr(assistant_msg_obj, 'created_at', None)) is not None else None
    }

@chat_router.get("/history")
async def get_chat_history(
    current_user: Annotated[UserModel, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    after_id: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Retrieve chat history for current user.

    If *after_id* > 0, only messages with id greater than *after_id* are returned
    (incremental fetch). Otherwise, returns the most recent *limit* messages.
    """
    user_id = getattr(current_user, 'id')
    
    if after_id > 0:
        history = await get_user_chat_history_after(db, user_id, after_id, limit)
    else:
        history = await get_user_chat_history(db, user_id, limit)

    # Map to simple dict format expected by frontend
    messages = [
        {
            "id": getattr(m, 'id'),
            "role": "user" if getattr(m, 'is_user_message') else "assistant",
            "content": getattr(m, 'message'),
            "created_at": getattr(m, 'created_at').isoformat() if getattr(m, 'created_at', None) else None
        }
        for m in history
    ]
    return messages
