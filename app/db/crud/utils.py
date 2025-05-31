"""
Utilities for CRUD operations.
Provides helper functions for common database operations.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from db.models.workout import Workout
from db.session import db_session
from db.models.workout import Category, MuscleGroup
from db.crud.workout_inference import infer_workout_type_from_first_exercise
from db.schemas.workout import WorkoutCreate

# Time limit to consider a workout as active
WORKOUT_TIMEOUT_MINUTES = 90

async def get_or_create_workout_id(user_id: int, exercise_log_data=None, llm=None) -> int:
    """
    Gets the ID of the user's active workout or creates a new one if it doesn't exist.
    
    If this is the first exercise log of a new workout, tries to infer the workout type
    based on the exercise and historical data.
    
    A new workout will be created if:
    - There are no previous workouts
    - The last workout is older than WORKOUT_TIMEOUT_MINUTES
    - The last workout is marked as finished (is_finished=True)
    
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
            (now - last_workout.created_at) > timedelta(minutes=WORKOUT_TIMEOUT_MINUTES) or
            last_workout.is_finished
        )
        
        if create_new_workout:
            # Default values
            muscle_group = MuscleGroup.FULL_BODY
            category = Category.HYPERTROPHY
            
            # If we have exercise data, use it to infer workout type
            if exercise_log_data and exercise_log_data.get('exercise_name') and llm:
                # Infer workout type using LLM
                inference_result = await infer_workout_type_from_first_exercise(
                    db=db,
                    user_id=user_id,
                    exercise_name=exercise_log_data.get('exercise_name'),
                    reps=exercise_log_data.get('reps'),
                    weight=exercise_log_data.get('weight'),
                    rir=exercise_log_data.get('rir'),
                    llm=llm
                )
                
                muscle_group = MuscleGroup(inference_result.muscle_group)
                category = Category(inference_result.category)
            
            # Create the new workout with the determined type
            new_workout = Workout(
                user_id=user_id, 
                category=category, 
                muscle_group=muscle_group, 
                start_time=now,
                is_finished=False
            )
            db.add(new_workout)
            await db.commit()
            await db.refresh(new_workout)
            return new_workout.id

        # If there is a recent one, reuse that workout_id
        return last_workout.id
