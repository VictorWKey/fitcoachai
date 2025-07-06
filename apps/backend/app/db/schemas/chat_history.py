"""
Chat history schemas for the FitCoach AI application.

This module contains Pydantic schemas for chat conversation history including:
- Base schema with common chat message fields
- Create schema for creating new chat history entries
- Response schema for returning chat history data

Used to store and retrieve conversation history between users and the AI coach.
"""

from pydantic import BaseModel
from typing import Optional

class ChatHistoryBase(BaseModel):
    """
    Base schema for chat history entries.
    
    Contains common fields for all chat messages.
    """
    user_id: int
    message: str
    is_user_message: bool


class ChatHistoryCreate(ChatHistoryBase):
    """
    Schema for creating a new chat history entry.
    
    Inherits all fields from the base schema.
    """
    pass


class ChatHistory(ChatHistoryBase):
    """
    Schema for chat history response data.
    
    Includes database-generated ID field.
    """
    id: int

    class Config:
        from_attributes = True
