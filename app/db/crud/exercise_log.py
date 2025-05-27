"""
CRUD operations for the ExerciseLog model.
Provides functions to create, read, update, and delete exercise logs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from typing import Optional, List
from db.models.exercise_log import ExerciseLog
from db.schemas.exercise_log import ExerciseLogCreate, ExerciseLogUpdate

async def get_exercise_log(db: AsyncSession, log_id: int) -> Optional[ExerciseLog]:
    """
    Gets an exercise log by its ID.
    
    Args:
        db: Database session
        log_id: ID of the exercise log to find
        
    Returns:
        ExerciseLog: Exercise log instance or None if it doesn't exist
    """
    result = await db.execute(select(ExerciseLog).where(ExerciseLog.id == log_id))
    return result.scalar_one_or_none()

async def get_workout_logs(db: AsyncSession, workout_id: int) -> List[ExerciseLog]:
    """
    Gets all exercise logs for a workout.
    
    Args:
        db: Database session
        workout_id: ID of the workout
        
    Returns:
        List[ExerciseLog]: List of exercise logs for the workout
    """
    result = await db.execute(
        select(ExerciseLog)
        .where(ExerciseLog.workout_id == workout_id)
        .order_by(ExerciseLog.set_number)
    )
    return result.scalars().all()

async def create_exercise_log(db: AsyncSession, log_data: ExerciseLogCreate) -> ExerciseLog:
    """
    Creates a new exercise log in the database.
    
    Args:
        db: Database session
        log_data: Exercise log data to create
        
    Returns:
        ExerciseLog: The created exercise log
    """
    db_log = ExerciseLog(**log_data.dict())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def update_exercise_log(db: AsyncSession, log_id: int, update_data: ExerciseLogUpdate) -> Optional[ExerciseLog]:
    """
    Updates an existing exercise log's data.
    
    Args:
        db: Database session
        log_id: ID of the exercise log to update
        update_data: Updated exercise log data
        
    Returns:
        ExerciseLog: The updated exercise log or None if it doesn't exist
    """
    db_log = await get_exercise_log(db, log_id)
    if not db_log:
        return None

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_log, key, value)

    await db.commit()
    await db.refresh(db_log)
    return db_log

async def delete_exercise_log(db: AsyncSession, log_id: int) -> bool:
    """
    Deletes an exercise log from the database.
    
    Args:
        db: Database session
        log_id: ID of the exercise log to delete
        
    Returns:
        bool: True if the exercise log was deleted, False if it didn't exist
    """
    db_log = await get_exercise_log(db, log_id)
    if not db_log:
        return False

    await db.delete(db_log)
    await db.commit()
    return True
