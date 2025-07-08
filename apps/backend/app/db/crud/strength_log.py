"""
CRUD operations for the StrengthLog model.
Provides functions to create, read, update, and delete strength training logs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from typing import Optional, List, Union
from datetime import datetime
from db.models.strength_log import StrengthLog
from db.models.cardio_log import CardioLog
from db.schemas.strength_log import StrengthLogCreate, StrengthLogUpdate

async def get_strength_log(db: AsyncSession, log_id: int) -> Optional[StrengthLog]:
    """
    Gets a strength log by its ID.
    
    Args:
        db: Database session
        log_id: ID of the strength log to find
        
    Returns:
        StrengthLog: Strength log instance or None if it doesn't exist
    """
    result = await db.execute(select(StrengthLog).where(StrengthLog.id == log_id))
    return result.scalar_one_or_none()

async def get_all_workout_logs(db: AsyncSession, workout_id: int) -> List[Union[StrengthLog, CardioLog]]:
    """
    Gets all exercise logs (both strength and cardio) for a workout.
    
    Args:
        db: Database session
        workout_id: ID of the workout
        
    Returns:
        List[Union[StrengthLog, CardioLog]]: List of all exercise logs for the workout, ordered by exercise_date
    """
    # Get strength logs
    strength_result = await db.execute(
        select(StrengthLog)
        .where(StrengthLog.workout_id == workout_id)
        .order_by(StrengthLog.exercise_date)
    )
    strength_logs = list(strength_result.scalars().all())
    
    # Get cardio logs
    cardio_result = await db.execute(
        select(CardioLog)
        .where(CardioLog.workout_id == workout_id)
        .order_by(CardioLog.exercise_date)
    )
    cardio_logs = list(cardio_result.scalars().all())
    
    # Combine logs and sort by exercise_date
    all_logs = strength_logs + cardio_logs
    
    # Sort by exercise_date, handling potential None values
    def get_exercise_date(log):
        date = getattr(log, 'exercise_date', None)
        return date if date is not None else datetime.min
    
    all_logs.sort(key=get_exercise_date)
    
    return all_logs

async def get_workout_logs(db: AsyncSession, workout_id: int) -> List[StrengthLog]:
    """
    Gets all strength logs for a workout.
    
    Args:
        db: Database session
        workout_id: ID of the workout
        
    Returns:
        List[StrengthLog]: List of strength logs for the workout
    """
    result = await db.execute(
        select(StrengthLog)
        .where(StrengthLog.workout_id == workout_id)
        .order_by(StrengthLog.set_number)
    )
    return list(result.scalars().all())

async def create_strength_log(db: AsyncSession, log_data: StrengthLogCreate) -> StrengthLog:
    """
    Creates a new strength log in the database.
    
    Args:
        db: Database session
        log_data: Strength log data to create
        
    Returns:
        StrengthLog: The created strength log
    """
    db_log = StrengthLog(**log_data.model_dump())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def update_strength_log(db: AsyncSession, log_id: int, update_data: StrengthLogUpdate) -> Optional[StrengthLog]:
    """
    Updates an existing strength log's data.
    
    Args:
        db: Database session
        log_id: ID of the strength log to update
        update_data: Updated strength log data
        
    Returns:
        StrengthLog: The updated strength log or None if it doesn't exist
    """
    db_log = await get_strength_log(db, log_id)
    if not db_log:
        return None

    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(db_log, key, value)

    await db.commit()
    await db.refresh(db_log)
    return db_log

async def delete_strength_log(db: AsyncSession, log_id: int) -> bool:
    """
    Deletes a strength log from the database.
    
    Args:
        db: Database session
        log_id: ID of the strength log to delete
        
    Returns:
        bool: True if the strength log was deleted, False if it didn't exist
    """
    db_log = await get_strength_log(db, log_id)
    if not db_log:
        return False

    await db.delete(db_log)
    await db.commit()
    return True
