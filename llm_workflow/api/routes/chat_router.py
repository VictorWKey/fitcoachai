# api/routes/chat_router.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Annotated
from db.schemas.user import User
from api.services.auth_service import get_current_user
from langgraph.graph import StateGraph
from api.services.chat_service import process_agent
from fastapi import Body
chat_router = APIRouter(prefix="/chat", tags=["chat"])

class ChatInput(BaseModel):
    input: str

@chat_router.post("/")
async def chat(current_user: Annotated[User, Depends(get_current_user)], chat_input: ChatInput):
    config = {"configurable": {"thread_id": current_user.id}}
    response = await process_agent(chat_input.input, config)
    return response["messages"]
