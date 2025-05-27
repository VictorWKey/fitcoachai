"""
Utilities for CRUD operations.
Provides helper functions for common database operations.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from db.models.workout import Workout
from db.session import db_session
from db.models.workout import Category, MuscleGroup

# Time limit to consider a workout as active
WORKOUT_TIMEOUT_MINUTES = 90

async def get_or_create_workout_id(user_id: int) -> int:
    """
    Gets the ID of the user's active workout or creates a new one if it doesn't exist.
    
    A workout is considered active if it was created within the last WORKOUT_TIMEOUT_MINUTES.
    If there is no active workout, a new one is created of strength type for full body.
    
    Args:
        user_id: ID of the user
        
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

        if last_workout is None or (now - last_workout.created_at) > timedelta(minutes=WORKOUT_TIMEOUT_MINUTES):
            new_workout = Workout(user_id=user_id, category=Category.STRENGTH, muscle_group=MuscleGroup.FULL_BODY, start_time=now)
            db.add(new_workout)
            await db.flush()
            await db.refresh(new_workout)
            return new_workout.id

        # If there is a recent one, reuse that workout_id
        return last_workout.id
