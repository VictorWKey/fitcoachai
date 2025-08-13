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

async def get_all_session_logs(db: AsyncSession, session_id: int) -> List[Union[StrengthLog, CardioLog]]:
    """
    Gets all exercise logs (both strength and cardio) for a training session.
    
    Args:
        db: Database session
        session_id: ID of the training session
        
    Returns:
        List[Union[StrengthLog, CardioLog]]: List of all exercise logs for the session, ordered by exercise_date
    """
    # Get strength logs (now through programmed_exercise directly to session)
    from db.models.programmed_exercise import ProgrammedExercise
    
    strength_result = await db.execute(
        select(StrengthLog)
        .join(ProgrammedExercise, StrengthLog.programmed_exercise_id == ProgrammedExercise.id)
        .where(ProgrammedExercise.session_id == session_id)
        .order_by(StrengthLog.exercise_date)
    )
    strength_logs = list(strength_result.scalars().all())
    
    # Get cardio logs
    cardio_result = await db.execute(
        select(CardioLog)
        .where(CardioLog.training_session_id == session_id)
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

async def get_session_strength_logs(db: AsyncSession, session_id: int) -> List[StrengthLog]:
    """
    Gets all strength logs for a training session.
    
    Args:
        db: Database session
        session_id: ID of the training session
        
    Returns:
        List[StrengthLog]: List of strength logs for the session
    """
    from db.models.programmed_exercise import ProgrammedExercise
    
    result = await db.execute(
        select(StrengthLog)
        .join(ProgrammedExercise, StrengthLog.programmed_exercise_id == ProgrammedExercise.id)
        .where(ProgrammedExercise.session_id == session_id)
        .order_by(StrengthLog.set_number)
    )
    return list(result.scalars().all())

async def get_exercise_logs_in_session(
    db: AsyncSession, 
    session_id: int, 
    standard_exercise_id: int, 
    user_id: int
) -> List[StrengthLog]:
    """
    Gets all strength logs for a specific exercise in a training session.
    
    Args:
        db: Database session
        session_id: ID of the training session
        standard_exercise_id: ID of the standard exercise
        user_id: ID of the user
        
    Returns:
        List[StrengthLog]: List of strength logs for the exercise
    """
    from db.models.programmed_exercise import ProgrammedExercise
    
    result = await db.execute(
        select(StrengthLog)
        .join(ProgrammedExercise, StrengthLog.programmed_exercise_id == ProgrammedExercise.id)
        .where(
            ProgrammedExercise.session_id == session_id,
            StrengthLog.standard_exercise_id == standard_exercise_id,
            StrengthLog.user_id == user_id
        )
        .order_by(StrengthLog.set_number)
    )
    return list(result.scalars().all())

async def create_strength_log(db: AsyncSession, log_data: StrengthLogCreate, user_id: int, programmed_exercise_id: int) -> StrengthLog:
    """
    Creates a new strength log in the database.
    
    Args:
        db: Database session
        log_data: Strength log data to create
        user_id: ID of the user creating the log
        programmed_exercise_id: ID of the programmed exercise
        
    Returns:
        StrengthLog: The created strength log
        
    Raises:
        ValueError: If the programmed exercise doesn't exist
    """
    # Verificar que el ejercicio programado existe
    from db.models.programmed_exercise import ProgrammedExercise
    
    programmed_exercise = await db.execute(
        select(ProgrammedExercise)
        .where(ProgrammedExercise.id == programmed_exercise_id)
    )
    programmed_exercise = programmed_exercise.scalar_one_or_none()
    
    if not programmed_exercise:
        raise ValueError(f"Programmed exercise {programmed_exercise_id} not found")
    
    # Verificar que no existe ya un log para el mismo ejercicio programado y número de serie
    existing_log = await db.execute(
        select(StrengthLog)
        .where(
            StrengthLog.programmed_exercise_id == programmed_exercise_id,
            StrengthLog.set_number == log_data.set_number
        )
    )
    existing_log = existing_log.scalar_one_or_none()
    
    if existing_log:
        raise ValueError(f"A log for set number {log_data.set_number} of programmed exercise {programmed_exercise_id} already exists. Use PUT to update existing logs.")

    # Verificar que el número de serie sea válido (positivo)
    if log_data.set_number <= 0:
        raise ValueError(f"Set number must be positive, got {log_data.set_number}.")

    # Verificar que el número de serie no exceda los sets programados
    programmed_sets = getattr(programmed_exercise, 'sets', None)
    if programmed_sets is None:
        # Si no hay sets programados definidos, permitir un máximo razonable (ej: 10 sets)
        max_allowed_sets = 10
        if log_data.set_number > max_allowed_sets:
            raise ValueError(f"Set number {log_data.set_number} exceeds the maximum allowed sets ({max_allowed_sets}) when no specific sets are programmed.")
    elif log_data.set_number > programmed_sets:
        raise ValueError(f"Set number {log_data.set_number} exceeds the programmed sets ({programmed_sets}) for this exercise.")

    # Crear el log con los datos adicionales
    log_dict = log_data.model_dump()
    log_dict.update({
        "user_id": user_id,
        "programmed_exercise_id": programmed_exercise_id,
        "standard_exercise_id": programmed_exercise.standard_exercise_id
    })
    
    db_log = StrengthLog(**log_dict)
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
