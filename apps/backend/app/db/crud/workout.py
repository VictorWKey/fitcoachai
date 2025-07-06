"""
CRUD operations for the Workout model.
Provides functions to create, read, update, and delete workouts.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from ..models.workout import Workout
from ..schemas.workout import WorkoutCreate, WorkoutUpdate
from typing import cast

async def get_workout(db: AsyncSession, workout_id: int) -> Optional[Workout]:
    """
    Gets a workout by its ID.
    
    Args:
        db: Database session
        workout_id: ID of the workout to find
        
    Returns:
        Workout: Workout instance or None if it doesn't exist
    """
    result = await db.execute(select(Workout).where(Workout.id == workout_id))
    return result.scalar_one_or_none()

async def get_user_workouts(db: AsyncSession, user_id: int) -> List[Workout]:
    """
    Gets all workouts for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        List[Workout]: List of workouts for the user
    """
    result = await db.execute(
        select(Workout)
        .where(Workout.user_id == user_id)
        .order_by(Workout.start_time.desc())
    )
    return list(result.scalars().all())

async def get_active_workout(db: AsyncSession, user_id: int) -> Optional[Workout]:
    """
    Gets the user's active (most recent unfinished) workout.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        Workout: Active workout or None if not found
    """
    result = await db.execute(
        select(Workout)
        .where(
            Workout.user_id == user_id,
            Workout.is_finished == False
        )
        .order_by(Workout.start_time.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

async def create_workout(db: AsyncSession, workout_data: WorkoutCreate) -> Workout:
    """
    Creates a new workout in the database.
    
    Args:
        db: Database session
        workout_data: Workout data to create
        
    Returns:
        Workout: The created workout
    """
    db_workout = Workout(**workout_data.dict())
    db.add(db_workout)
    await db.commit()
    await db.refresh(db_workout)
    return db_workout

async def update_workout(db: AsyncSession, workout_id: int, update_data: WorkoutUpdate) -> Optional[Workout]:
    """
    Updates an existing workout's data.
    
    Args:
        db: Database session
        workout_id: ID of the workout to update
        update_data: Updated workout data
        
    Returns:
        Workout: The updated workout or None if it doesn't exist
    """
    db_workout = await get_workout(db, workout_id)
    if not db_workout:
        return None

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_workout, key, value)

    await db.commit()
    await db.refresh(db_workout)
    return db_workout

async def delete_workout(db: AsyncSession, workout_id: int) -> bool:
    """
    Deletes a workout from the database.
    
    Args:
        db: Database session
        workout_id: ID of the workout to delete
        
    Returns:
        bool: True if the workout was deleted, False if it didn't exist
    """
    db_workout = await get_workout(db, workout_id)
    if not db_workout:
        return False

    await db.delete(db_workout)
    await db.commit()
    return True


