"""
CRUD operations for the CardioLog model.
Provides functions to create, read, update, and delete cardio training logs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from typing import Optional, List
from db.models.cardio_log import CardioLog
from db.schemas.cardio_log import CardioLogCreate, CardioLogUpdate

async def get_cardio_log(db: AsyncSession, log_id: int) -> Optional[CardioLog]:
    """
    Gets a cardio log by its ID.
    
    Args:
        db: Database session
        log_id: ID of the cardio log to find
        
    Returns:
        CardioLog: Cardio log instance or None if it doesn't exist
    """
    result = await db.execute(select(CardioLog).where(CardioLog.id == log_id))
    return result.scalar_one_or_none()

async def get_session_cardio_logs(db: AsyncSession, session_id: int) -> List[CardioLog]:
    """
    Gets all cardio logs for a training session.
    
    Args:
        db: Database session
        session_id: ID of the training session
        
    Returns:
        List[CardioLog]: List of cardio logs for the session
    """
    result = await db.execute(
        select(CardioLog)
        .where(CardioLog.training_session_id == session_id)
        .order_by(CardioLog.exercise_date)
    )
    return list(result.scalars().all())

async def create_cardio_log(db: AsyncSession, log_data: CardioLogCreate) -> CardioLog:
    """
    Creates a new cardio log in the database.
    
    Args:
        db: Database session
        log_data: Cardio log data to create
        
    Returns:
        CardioLog: The created cardio log
    """
    db_log = CardioLog(**log_data.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def update_cardio_log(db: AsyncSession, log_id: int, update_data: CardioLogUpdate) -> Optional[CardioLog]:
    """
    Updates an existing cardio log's data.
    
    Args:
        db: Database session
        log_id: ID of the cardio log to update
        update_data: Updated cardio log data
        
    Returns:
        CardioLog: The updated cardio log or None if it doesn't exist
    """
    db_log = await get_cardio_log(db, log_id)
    if not db_log:
        return None

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(db_log, key, value)

    await db.commit()
    await db.refresh(db_log)
    return db_log

async def delete_cardio_log(db: AsyncSession, log_id: int) -> bool:
    """
    Deletes a cardio log from the database.
    
    Args:
        db: Database session
        log_id: ID of the cardio log to delete
        
    Returns:
        bool: True if the cardio log was deleted, False if it didn't exist
    """
    db_log = await get_cardio_log(db, log_id)
    if not db_log:
        return False

    await db.delete(db_log)
    await db.commit()
    return True 