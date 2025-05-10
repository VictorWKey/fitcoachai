from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sqlalchemy_update, delete as sqlalchemy_delete
from typing import Optional, List
from db.models.exercise_log import ExerciseLog
from db.schemas.exercise_log import ExerciseLogCreate, ExerciseLogUpdate

async def get_exercise_log(db: AsyncSession, log_id: int) -> Optional[ExerciseLog]:
    """Obtener un log de ejercicio por ID"""
    result = await db.execute(select(ExerciseLog).where(ExerciseLog.id == log_id))
    return result.scalar_one_or_none()

async def get_workout_logs(db: AsyncSession, workout_id: int) -> List[ExerciseLog]:
    """Obtener todos los logs de un entrenamiento"""
    result = await db.execute(
        select(ExerciseLog)
        .where(ExerciseLog.workout_id == workout_id)
        .order_by(ExerciseLog.set_number)
    )
    return result.scalars().all()

async def create_exercise_log(db: AsyncSession, log_data: ExerciseLogCreate) -> ExerciseLog:
    """Crear un nuevo log de ejercicio"""
    db_log = ExerciseLog(**log_data.dict())
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def update_exercise_log(db: AsyncSession, log_id: int, update_data: ExerciseLogUpdate) -> Optional[ExerciseLog]:
    """Actualizar un log de ejercicio"""
    db_log = await get_exercise_log(db, log_id)
    if not db_log:
        return None

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(db_log, key, value)

    await db.commit()
    await db.refresh(db_log)
    return db_log

async def delete_exercise_log(db: AsyncSession, log_id: int) -> bool:
    """Eliminar un log de ejercicio"""
    db_log = await get_exercise_log(db, log_id)
    if not db_log:
        return False

    await db.delete(db_log)
    await db.commit()
    return True
