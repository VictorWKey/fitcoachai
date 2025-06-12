"""CRUD operations for ChatHistory model."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from db.models.chat_history import ChatHistory
from db.schemas.chat_history import ChatHistoryCreate


async def create_chat_history(db: AsyncSession, chat_data: ChatHistoryCreate) -> ChatHistory:
    """Create a new chat history record."""
    db_chat = ChatHistory(**chat_data.dict())
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    return db_chat


async def get_user_chat_history(db: AsyncSession, user_id: int, limit: int = 50) -> List[ChatHistory]:
    """Retrieve recent chat history for a user."""
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_user_chat_history_after(db: AsyncSession, user_id: int, after_id: int, limit: int = 50) -> List[ChatHistory]:
    """Retrieve chat messages for a user with id greater than a given message id."""
    result = await db.execute(
        select(ChatHistory)
        .where(ChatHistory.user_id == user_id, ChatHistory.id > after_id)
        .order_by(ChatHistory.created_at)
        .limit(limit)
    )
    return list(result.scalars().all())
