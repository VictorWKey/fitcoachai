"""
CRUD operations for hypertrophy logs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from db.models.discipline_exercise_logs.hypertrophy import HypertrophyLog
from db.schemas.discipline_exercise_logs.hypertrophy import HypertrophyLogCreate, HypertrophyLogUpdate

async def create_hypertrophy_log(
    db: AsyncSession, 
    log_data: HypertrophyLogCreate, 
    user_id: int
) -> HypertrophyLog:
    """Create a new hypertrophy log entry."""
    db_log = HypertrophyLog(**log_data.model_dump(), user_id=user_id)
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_hypertrophy_log(db: AsyncSession, log_id: int) -> Optional[HypertrophyLog]:
    """Get a hypertrophy log by ID."""
    result = await db.execute(select(HypertrophyLog).where(HypertrophyLog.id == log_id))
    return result.scalar_one_or_none()

async def get_user_hypertrophy_logs(
    db: AsyncSession, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[HypertrophyLog]:
    """Get all hypertrophy logs for a user."""
    result = await db.execute(
        select(HypertrophyLog)
        .where(HypertrophyLog.user_id == user_id)
        .order_by(HypertrophyLog.exercise_date.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())

async def get_workout_hypertrophy_logs(
    db: AsyncSession, 
    workout_id: int
) -> List[HypertrophyLog]:
    """Get all hypertrophy logs for a specific workout."""
    result = await db.execute(
        select(HypertrophyLog)
        .where(HypertrophyLog.workout_id == workout_id)
        .order_by(HypertrophyLog.set_number)
    )
    return list(result.scalars().all())

async def update_hypertrophy_log(
    db: AsyncSession, 
    log_id: int, 
    log_update: HypertrophyLogUpdate
) -> Optional[HypertrophyLog]:
    """Update a hypertrophy log."""
    result = await db.execute(select(HypertrophyLog).where(HypertrophyLog.id == log_id))
    db_log = result.scalar_one_or_none()
    
    if db_log:
        update_data = log_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_log, field, value)
        
        await db.commit()
        await db.refresh(db_log)
    
    return db_log

async def delete_hypertrophy_log(db: AsyncSession, log_id: int) -> bool:
    """Delete a hypertrophy log."""
    result = await db.execute(select(HypertrophyLog).where(HypertrophyLog.id == log_id))
    db_log = result.scalar_one_or_none()
    
    if db_log:
        await db.delete(db_log)
        await db.commit()
        return True
    
    return False 