"""
CRUD operations for cardio logs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from db.models.discipline_exercise_logs.cardio import CardioLog
from db.schemas.discipline_exercise_logs.cardio import CardioLogCreate, CardioLogUpdate

async def create_cardio_log(
    db: AsyncSession, 
    log_data: CardioLogCreate, 
    user_id: int
) -> CardioLog:
    """Create a new cardio log entry."""
    db_log = CardioLog(**log_data.model_dump(), user_id=user_id)
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_cardio_log(db: AsyncSession, log_id: int) -> Optional[CardioLog]:
    """Get a cardio log by ID."""
    result = await db.execute(select(CardioLog).where(CardioLog.id == log_id))
    return result.scalar_one_or_none()

async def get_user_cardio_logs(
    db: AsyncSession, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[CardioLog]:
    """Get all cardio logs for a user."""
    result = await db.execute(
        select(CardioLog)
        .where(CardioLog.user_id == user_id)
        .order_by(CardioLog.exercise_date.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def get_workout_cardio_logs(
    db: AsyncSession, 
    workout_id: int
) -> List[CardioLog]:
    """Get all cardio logs for a specific workout."""
    result = await db.execute(
        select(CardioLog)
        .where(CardioLog.workout_id == workout_id)
        .order_by(CardioLog.exercise_date)
    )
    return list(result.scalars().all())

async def update_cardio_log(
    db: AsyncSession, 
    log_id: int, 
    log_update: CardioLogUpdate
) -> Optional[CardioLog]:
    """Update a cardio log."""
    result = await db.execute(select(CardioLog).where(CardioLog.id == log_id))
    db_log = result.scalar_one_or_none()
    
    if db_log:
        update_data = log_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_log, field, value)
        
        await db.commit()
        await db.refresh(db_log)
    
    return db_log

async def delete_cardio_log(db: AsyncSession, log_id: int) -> bool:
    """Delete a cardio log."""
    result = await db.execute(select(CardioLog).where(CardioLog.id == log_id))
    db_log = result.scalar_one_or_none()
    
    if db_log:
        await db.delete(db_log)
        await db.commit()
        return True
    
    return False 