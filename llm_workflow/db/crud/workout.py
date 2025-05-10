from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from ..models.workout import Workout
from ..schemas.workout import WorkoutCreate, WorkoutUpdate

async def get_workout(db: AsyncSession, workout_id: int) -> Optional[Workout]:
    """Obtener un entrenamiento por ID"""
    result = await db.execute(select(Workout).where(Workout.id == workout_id))
    return result.scalar_one_or_none()

async def get_user_workouts(db: AsyncSession, user_id: int) -> List[Workout]:
    """Obtener entrenamientos de un usuario"""
    result = await db.execute(
        select(Workout)
        .where(Workout.user_id == user_id)
        .order_by(Workout.created_at.desc())
    )
    return result.scalars().all()

async def create_workout(db: AsyncSession, workout_data: WorkoutCreate) -> Workout:
    """Crear un nuevo entrenamiento"""
    db_workout = Workout(**workout_data.dict())
    db.add(db_workout)
    await db.commit()
    await db.refresh(db_workout)
    return db_workout

async def update_workout(db: AsyncSession, workout_id: int, update_data: WorkoutUpdate) -> Optional[Workout]:
    """Actualizar un entrenamiento"""
    db_workout = await get_workout(db, workout_id)
    if not db_workout:
        return None

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_workout, key, value)

    await db.commit()
    await db.refresh(db_workout)
    return db_workout

async def delete_workout(db: AsyncSession, workout_id: int) -> bool:
    """Eliminar un entrenamiento"""
    db_workout = await get_workout(db, workout_id)
    if not db_workout:
        return False

    await db.delete(db_workout)
    await db.commit()
    return True
