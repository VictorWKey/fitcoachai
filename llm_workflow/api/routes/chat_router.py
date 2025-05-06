# api/routes/chat_router.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Annotated
from db.schemas.user import User
from api.services.auth_service import get_current_user
from agent.agent import get_agent
from langgraph.graph import StateGraph


chat_router = APIRouter(prefix="/chat", tags=["chat"])

class ChatInput(BaseModel):
    input: str

@chat_router.post("/")
async def chat(current_user: Annotated[User, Depends(get_current_user)], chat_input: ChatInput, agent: StateGraph = Depends(get_agent)):
    config = {"configurable": {"thread_id": current_user.id}}
    response = agent.invoke({"messages": [{"role": "user", "content": chat_input.input}]}, config)
    return response["messages"]
