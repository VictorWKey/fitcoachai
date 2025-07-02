"""
CRUD operations for flexibility logs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from db.models.discipline_exercise_logs.flexibility import FlexibilityLog
from db.schemas.discipline_exercise_logs.flexibility import FlexibilityLogCreate, FlexibilityLogUpdate

async def create_flexibility_log(
    db: AsyncSession, 
    log_data: FlexibilityLogCreate, 
    user_id: int
) -> FlexibilityLog:
    """Create a new flexibility log entry."""
    db_log = FlexibilityLog(**log_data.model_dump(), user_id=user_id)
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_flexibility_log(db: AsyncSession, log_id: int) -> Optional[FlexibilityLog]:
    """Get a flexibility log by ID."""
    result = await db.execute(select(FlexibilityLog).where(FlexibilityLog.id == log_id))
    return result.scalar_one_or_none()

async def get_user_flexibility_logs(
    db: AsyncSession, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[FlexibilityLog]:
    """Get all flexibility logs for a user."""
    result = await db.execute(
        select(FlexibilityLog)
        .where(FlexibilityLog.user_id == user_id)
        .order_by(FlexibilityLog.exercise_date.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def get_workout_flexibility_logs(
    db: AsyncSession, 
    workout_id: int
) -> List[FlexibilityLog]:
    """Get all flexibility logs for a specific workout."""
    result = await db.execute(
        select(FlexibilityLog)
        .where(FlexibilityLog.workout_id == workout_id)
        .order_by(FlexibilityLog.exercise_date)
    )
    return list(result.scalars().all())

async def update_flexibility_log(
    db: AsyncSession, 
    log_id: int, 
    log_update: FlexibilityLogUpdate
) -> Optional[FlexibilityLog]:
    """Update a flexibility log."""
    result = await db.execute(select(FlexibilityLog).where(FlexibilityLog.id == log_id))
    db_log = result.scalar_one_or_none()
    
    if db_log:
        update_data = log_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_log, field, value)
        
        await db.commit()
        await db.refresh(db_log)
    
    return db_log

async def delete_flexibility_log(db: AsyncSession, log_id: int) -> bool:
    """Delete a flexibility log."""
    result = await db.execute(select(FlexibilityLog).where(FlexibilityLog.id == log_id))
    db_log = result.scalar_one_or_none()
    
    if db_log:
        await db.delete(db_log)
        await db.commit()
        return True
    
    return False 