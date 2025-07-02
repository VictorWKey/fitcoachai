"""
CRUD operations for max strength logs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from db.models.discipline_exercise_logs.max_strength import MaxStrengthLog
from db.schemas.discipline_exercise_logs.max_strength import MaxStrengthLogCreate, MaxStrengthLogUpdate

async def create_max_strength_log(
    db: AsyncSession, 
    log_data: MaxStrengthLogCreate, 
    user_id: int
) -> MaxStrengthLog:
    """Create a new max strength log entry."""
    db_log = MaxStrengthLog(**log_data.model_dump(), user_id=user_id)
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_max_strength_log(db: AsyncSession, log_id: int) -> Optional[MaxStrengthLog]:
    """Get a max strength log by ID."""
    result = await db.execute(select(MaxStrengthLog).where(MaxStrengthLog.id == log_id))
    return result.scalar_one_or_none()

async def get_user_max_strength_logs(
    db: AsyncSession, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[MaxStrengthLog]:
    """Get all max strength logs for a user."""
    result = await db.execute(
        select(MaxStrengthLog)
        .where(MaxStrengthLog.user_id == user_id)
        .order_by(MaxStrengthLog.exercise_date.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def get_workout_max_strength_logs(
    db: AsyncSession, 
    workout_id: int
) -> List[MaxStrengthLog]:
    """Get all max strength logs for a specific workout."""
    result = await db.execute(
        select(MaxStrengthLog)
        .where(MaxStrengthLog.workout_id == workout_id)
        .order_by(MaxStrengthLog.set_number)
    )
    return list(result.scalars().all())

async def update_max_strength_log(
    db: AsyncSession, 
    log_id: int, 
    log_update: MaxStrengthLogUpdate
) -> Optional[MaxStrengthLog]:
    """Update a max strength log."""
    result = await db.execute(select(MaxStrengthLog).where(MaxStrengthLog.id == log_id))
    db_log = result.scalar_one_or_none()
    
    if db_log:
        update_data = log_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_log, field, value)
        
        await db.commit()
        await db.refresh(db_log)
    
    return db_log

async def delete_max_strength_log(db: AsyncSession, log_id: int) -> bool:
    """Delete a max strength log."""
    result = await db.execute(select(MaxStrengthLog).where(MaxStrengthLog.id == log_id))
    db_log = result.scalar_one_or_none()
    
    if db_log:
        await db.delete(db_log)
        await db.commit()
        return True
    
    return False 