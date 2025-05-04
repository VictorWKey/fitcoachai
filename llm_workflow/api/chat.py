from fastapi import APIRouter
from agent import Agent
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatInput(BaseModel):
    input: str

@router.post("/")
async def chat(chat_input: ChatInput):
    agent = Agent()
    response = agent.invoke({"messages": [{"role": "user", "content": chat_input.input}]})
    return response["messages"]