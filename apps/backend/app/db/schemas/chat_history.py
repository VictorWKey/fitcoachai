"""Pydantic schemas for chat history."""

from pydantic import BaseModel
from typing import Optional

class ChatHistoryBase(BaseModel):
    user_id: int
    message: str
    is_user_message: bool


class ChatHistoryCreate(ChatHistoryBase):
    pass


class ChatHistory(ChatHistoryBase):
    id: int

    class Config:
        from_attributes = True
