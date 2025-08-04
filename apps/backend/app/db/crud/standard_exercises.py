"""
CRUD operations for the StandardExercise model.
Provides functions to create, read, update, and delete standard exercises.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Optional, List
from db.models.standard_exercises import StandardExercise
from db.schemas.standard_exercises import StandardExerciseCreate, StandardExerciseUpdate

async def get_standard_exercise(db: AsyncSession, exercise_id: int) -> Optional[StandardExercise]:
    """
    Gets a standard exercise by its ID.
    Args:
        db: Database session
        exercise_id: ID of the standard exercise
    Returns:
        StandardExercise: Instance or None if not found
    """
    result = await db.get(StandardExercise, exercise_id)
    return result

async def get_standard_exercise_by_name(db: AsyncSession, standard_name: str) -> Optional[StandardExercise]:
    """
    Gets a standard exercise by its unique name.
    Args:
        db: Database session
        standard_name: Name of the standard exercise
    Returns:
        StandardExercise: Instance or None if not found
    """
    result = await db.execute(
        select(StandardExercise).where(func.lower(StandardExercise.standard_name) == func.lower(standard_name))
    )
    return result.scalar_one_or_none()

async def get_standard_exercises(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[StandardExercise]:
    """
    Gets a paginated list of standard exercises.
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Max number of records to return
    Returns:
        List[StandardExercise]: List of standard exercises
    """
    result = await db.execute(
        select(StandardExercise).offset(skip).limit(limit)
    )
    return list(result.scalars().all())

async def get_standard_exercises_by_equipment_and_muscle_group(
    db: AsyncSession,
    equipment: Optional[str] = None,
    main_muscle_group: Optional[str] = None
) -> List[StandardExercise]:
    """
    Gets all standard exercises that match the given equipment and main muscle group.
    If either parameter is None, it is not used as a filter (returns all that match the filters present).
    Args:
        db: Database session
        equipment: EquipmentEnum value as string (exact match) or None
        main_muscle_group: MuscleGroupEnum value as string (exact match) or None
    Returns:
        List[StandardExercise]: List of matching standard exercises
    """
    stmt = select(StandardExercise)
    if equipment is not None:
        stmt = stmt.where(StandardExercise.equipment == equipment)
    if main_muscle_group is not None:
        stmt = stmt.where(StandardExercise.main_muscle_group == main_muscle_group)
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_standard_exercise(db: AsyncSession, exercise: StandardExerciseCreate) -> StandardExercise:
    """
    Creates a new standard exercise in the database.
    Args:
        db: Database session
        exercise: Data for the new standard exercise
    Returns:
        StandardExercise: The created standard exercise
    """
    db_exercise = StandardExercise(**exercise.model_dump())
    db.add(db_exercise)
    await db.commit()
    await db.refresh(db_exercise)
    return db_exercise

async def update_standard_exercise(db: AsyncSession, exercise_id: int, update_data: StandardExerciseUpdate) -> Optional[StandardExercise]:
    """
    Updates an existing standard exercise.
    Args:
        db: Database session
        exercise_id: ID of the standard exercise to update
        update_data: Data to update
    Returns:
        StandardExercise: The updated standard exercise or None if not found
    """
    db_exercise = await get_standard_exercise(db, exercise_id)
    if not db_exercise:
        return None
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(db_exercise, key, value)
    await db.commit()
    await db.refresh(db_exercise)
    return db_exercise

async def delete_standard_exercise(db: AsyncSession, exercise_id: int) -> bool:
    """
    Deletes a standard exercise from the database.
    Args:
        db: Database session
        exercise_id: ID of the standard exercise to delete
    Returns:
        bool: True if deleted, False if not found
    """
    db_exercise = await get_standard_exercise(db, exercise_id)
    if not db_exercise:
        return False
    await db.delete(db_exercise)
    await db.commit()
    return True 