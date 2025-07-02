"""
Utilities for CRUD operations.
Provides helper functions for common database operations.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.workout import Workout
from db.session import db_session
from db.models.workout import TrainingDiscipline, MuscleGroup
# from db.crud.workout_inference import infer_workout_type_from_first_exercise
from db.crud.workout import finalize_workout, get_workout
from db.schemas.workout import WorkoutCreate
from db.crud.user import get_user_training_discipline
from .exercise_log_factory import ExerciseLogCRUDFactory
from typing import Optional, List, Any

# Time limit to consider a workout as active
WORKOUT_TIMEOUT_MINUTES = 90

async def get_or_create_workout_id(user_id: int, llm=None) -> int:
    """
    Gets the ID of the user's active workout or creates a new one if it doesn't exist.
    
    If this is the first exercise log of a new workout, tries to infer the workout type
    based on the exercise and historical data.
    
    A new workout will be created if:
    - There are no previous workouts
    - The last workout is older than WORKOUT_TIMEOUT_MINUTES
    - The last workout is marked as finished (is_finished=True)
    
    If the last workout is not finished but older than WORKOUT_TIMEOUT_MINUTES,
    it will be automatically finalized before creating a new one.
    
    Args:
        user_id: ID of the user
        exercise_log_data: Optional data for the current exercise log
        llm: Optional language model for inference
        
    Returns:
        int: ID of the active or newly created workout
    """
    now = datetime.now(timezone.utc)

    async with db_session() as db:
        # Find the user's last workout
        result = await db.execute(
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
            .limit(1)
        )
        last_workout = result.scalar_one_or_none()

        # Check if we need to create a new workout
        create_new_workout = (
            last_workout is None or 
            last_workout.is_finished
        )
        
        # Check if the last workout is inactive (older than timeout)
        inactive_workout = (
            last_workout is not None and
            not last_workout.is_finished and
            (now - last_workout.created_at) > timedelta(minutes=WORKOUT_TIMEOUT_MINUTES)
        )
        
        # If the last workout is inactive but not finished, finalize it
        if inactive_workout:
            await finalize_workout(db, last_workout.id, llm)
            create_new_workout = True
        
        if create_new_workout:
            discipline = await get_user_training_discipline(db, user_id) or TrainingDiscipline.HYPERTROPHY
            
            # Create the new workout with the determined type
            workout_data = WorkoutCreate(
                user_id=user_id,
                discipline=discipline,
                start_time=now,
                is_finished=False
            )
            
            # Create workout using the CRUD function
            from db.crud.workout import create_workout
            new_workout = await create_workout(db, workout_data)
            return getattr(new_workout, 'id')

        # If there is a recent one, reuse that workout_id
        return getattr(last_workout, 'id')

async def get_exercise_log_by_workout_discipline(
    db: AsyncSession, 
    exercise_id: int, 
    workout_id: int
) -> Optional[Any]:
    """
    Gets an exercise log by ID, using the workout's discipline to determine 
    which specific CRUD function to call.
    
    Args:
        db: Database session
        exercise_id: ID of the exercise log
        workout_id: ID of the workout to determine discipline
        
    Returns:
        Exercise log of the appropriate discipline or None if not found
    """
    # Get the workout to determine its discipline
    workout = await get_workout(db, workout_id)
    if not workout:
        return None
    
    # Call the factory method
    return await ExerciseLogCRUDFactory.get_exercise_log(
        db, exercise_id, getattr(workout, 'discipline')
    )

async def get_workout_logs_by_discipline(
    db: AsyncSession, 
    workout_id: int
) -> List[Any]:
    """
    Gets all exercise logs for a workout, using the workout's discipline 
    to determine which specific CRUD function to call.
    
    Args:
        db: Database session
        workout_id: ID of the workout
        
    Returns:
        List of exercise logs of the appropriate discipline
    """
    # Get the workout to determine its discipline
    workout = await get_workout(db, workout_id)
    if not workout:
        return []
    
    # Call the factory method
    return await ExerciseLogCRUDFactory.get_workout_logs(
        db, workout_id, getattr(workout, 'discipline')
    )
