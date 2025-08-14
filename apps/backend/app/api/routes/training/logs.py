"""
API endpoints for exercise logs.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Annotated, Optional, Dict, Any, cast, Union

from db.session import get_db
from db.models.user import User
from db.models.training_session import TrainingSession, SessionStatus
from db.models.training_week import TrainingWeek
from db.models.training_program import TrainingProgram
from db.models.programmed_exercise import ProgrammedExercise
from db.models.strength_log import StrengthLog
from db.models.cardio_log import CardioLog
from db.models.standard_exercises import StandardExercise
from db.schemas.strength_log import StrengthLogCreate, StrengthLogUpdate, StrengthLog as StrengthLogResponse
from db.schemas.cardio_log import CardioLogCreate, CardioLogUpdate, CardioLog as CardioLogResponse

from db.crud.strength_log import (
    get_strength_log, create_strength_log, update_strength_log, delete_strength_log,
    get_session_strength_logs, get_all_session_logs, get_exercise_logs_in_session
)
from db.crud.cardio_log import (
    get_cardio_log, create_cardio_log, update_cardio_log, delete_cardio_log,
    get_session_cardio_logs
)
from api.services.auth import get_current_verified_user

router = APIRouter()

async def verify_session_access(
    db: AsyncSession, 
    session_id: int, 
    program_id: int, 
    week_id: int, 
    user_id: int
) -> TrainingSession:
    """
    Verifica que la sesión exista, pertenezca al programa y semana especificados, 
    y el usuario tenga acceso a ella.
    
    Retorna el objeto de sesión si todo está bien, o lanza excepciones HTTP apropiadas.
    """
    # Verificamos que la sesión exista y pertenezca al usuario correcto, programa y semana
    stmt = select(TrainingSession).join(
        TrainingWeek, TrainingSession.week_id == TrainingWeek.id
    ).join(
        TrainingProgram, TrainingWeek.program_id == TrainingProgram.id
    ).where(
        TrainingSession.id == session_id,
        TrainingWeek.id == week_id,
        TrainingProgram.id == program_id,
        TrainingProgram.user_id == user_id
    ).options(
        selectinload(TrainingSession.programmed_exercises),
        selectinload(TrainingSession.training_week)
    )
    
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        # Verificamos si la sesión existe en general
        check_stmt = select(TrainingSession).where(TrainingSession.id == session_id)
        check_result = await db.execute(check_stmt)
        check_session = check_result.scalar_one_or_none()
        
        if not check_session:
            raise HTTPException(status_code=404, detail="Training session not found")
            
        # Verificamos si pertenece al programa y semana correctos
        check_program_stmt = select(TrainingSession).join(
            TrainingWeek, TrainingSession.week_id == TrainingWeek.id
        ).join(
            TrainingProgram, TrainingWeek.program_id == TrainingProgram.id
        ).where(
            TrainingSession.id == session_id,
            TrainingWeek.id == week_id,
            TrainingProgram.id == program_id
        )
        check_program_result = await db.execute(check_program_stmt)
        if check_program_result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=404, 
                detail="Training session doesn't belong to the specified week and program"
            )
            
        # Si llegamos aquí, es un problema de acceso
        raise HTTPException(status_code=403, detail="Access denied to this session's logs")
        
    return session

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/logs", response_model=List[Dict[str, Any]])
async def get_all_session_logs_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Get all exercise logs (strength + cardio) for a specific training session.
    """
    try:
        # Verificar acceso a la sesión
        session = await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Update last activity if session is active
        # Verificamos si la sesión está activa usando session_status
        stmt = select(TrainingSession.session_status).where(TrainingSession.id == session_id)
        result = await db.execute(stmt)
        session_status = result.scalar_one()
        
        # Get all logs for the session
        # First, get all programmed exercises for this session in order
        
        programmed_exercises_stmt = select(ProgrammedExercise).options(
            selectinload(ProgrammedExercise.standard_exercise)
        ).where(
            ProgrammedExercise.session_id == session_id
        ).order_by(ProgrammedExercise.id)
        
        programmed_exercises_result = await db.execute(programmed_exercises_stmt)
        programmed_exercises = list(programmed_exercises_result.scalars().all())
        
        # Build the response with exercises in programmed order
        exercises_with_logs = []
        
        for programmed_exercise in programmed_exercises:
            # Get strength logs for this specific programmed exercise, ordered by set number
            strength_logs_stmt = select(StrengthLog).where(
                StrengthLog.programmed_exercise_id == programmed_exercise.id
            ).order_by(StrengthLog.set_number)
            
            strength_logs_result = await db.execute(strength_logs_stmt)
            strength_logs = list(strength_logs_result.scalars().all())
            
            # Get cardio logs for this specific programmed exercise, ordered by date
            cardio_logs_stmt = select(CardioLog).where(
                CardioLog.programmed_exercise_id == programmed_exercise.id
            ).order_by(CardioLog.exercise_date)
            
            cardio_logs_result = await db.execute(cardio_logs_stmt)
            cardio_logs = list(cardio_logs_result.scalars().all())
            
            # Convert ORM objects to dictionaries that match the schema
            strength_log_responses = []
            for log in strength_logs:
                log_dict = {
                    "id": log.id,
                    "user_id": log.user_id,
                    "programmed_exercise_id": log.programmed_exercise_id,
                    "set_number": log.set_number,
                    "set_type": log.set_type,
                    "repetitions_done": log.repetitions_done,
                    "used_weight": log.used_weight,
                    "used_weight_unit": log.used_weight_unit,
                    "perceived_rir": log.perceived_rir,
                    "perceived_rpe": log.perceived_rpe,
                    "tempo": log.tempo,
                    "rest_time_seconds": log.rest_time_seconds,
                    "notes": log.notes,
                    "exercise_date": log.exercise_date,
                    "updated_at": log.updated_at
                }
                strength_log_responses.append(log_dict)
            
            cardio_log_responses = []
            for log in cardio_logs:
                log_dict = {
                    "id": log.id,
                    "user_id": log.user_id,
                    "programmed_exercise_id": log.programmed_exercise_id,
                    "training_session_id": log.training_session_id,
                    "exercise_name": log.exercise_name,
                    "cardio_type": log.cardio_type,
                    "total_duration_seconds": log.total_duration_seconds,
                    "distance": log.distance,
                    "distance_unit": log.distance_unit,
                    "calories_burned": log.calories_burned,
                    "avg_heart_rate": log.avg_heart_rate,
                    "avg_rpe": log.avg_rpe,
                    "intensity_level": log.intensity_level,
                    "incline_level": log.incline_level,
                    "notes": log.notes,
                    "exercise_date": log.exercise_date,
                    "updated_at": log.updated_at
                }
                cardio_log_responses.append(log_dict)
            
            # Combine logs - strength logs first, then cardio logs
            all_exercise_logs = strength_log_responses + cardio_log_responses
            
            exercises_with_logs.append({
                "exercise_name": programmed_exercise.standard_exercise.standard_name if programmed_exercise.standard_exercise else "Unknown Exercise",
                "exercise_type": programmed_exercise.standard_exercise.type.value if programmed_exercise.standard_exercise else None,
                "programmed_exercise_id": programmed_exercise.id,
                "logs": all_exercise_logs
            })
        
        return exercises_with_logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session logs: {str(e)}")


@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs", response_model=List[Union[StrengthLogResponse, CardioLogResponse]])
async def get_exercise_logs_in_session_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1)
):
    """
    Get all logs for a specific exercise in a training session.
    """
    try:
        # Verificar acceso a la sesión
        session = await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Update last activity if session is active
        stmt = select(TrainingSession.session_status).where(TrainingSession.id == session_id)
        result = await db.execute(stmt)
        session_status = result.scalar_one()
        

        
        # Get exercise logs for the session
        logs = await get_exercise_logs_in_session(db, session_id, exercise_id, cast(int, current_user.id))
        
        return logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving exercise logs: {str(e)}")

@router.post("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/strength", response_model=StrengthLogResponse, status_code=status.HTTP_201_CREATED)
async def create_strength_log_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    log_data: StrengthLogCreate,
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1)
):
    """
    Create a new strength exercise log entry for a training session.
    """
    try:
        # Verificar acceso a la sesión
        session = await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Verificar que la sesión esté activa
        stmt = select(TrainingSession.session_status).where(TrainingSession.id == session_id)
        result = await db.execute(stmt)
        session_status = result.scalar_one()
        
        if session_status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Cannot add logs to an inactive session."
            )
        
        # Asegurarnos de que log_data tenga el session_id y user_id correctos
        log_data_dict = log_data.model_dump()
        log_data_dict["session_id"] = session_id
        log_data_dict["user_id"] = cast(int, current_user.id)
        
        # Crear el log de fuerza
        new_log = await create_strength_log(
            db=db,
            log_data=StrengthLogCreate(**log_data_dict),
            user_id=cast(int, current_user.id),
            programmed_exercise_id=exercise_id
        )
        
        return new_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating strength log: {str(e)}")

@router.post("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/cardio", response_model=CardioLogResponse, status_code=status.HTTP_201_CREATED)
async def create_cardio_log_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    log_data: CardioLogCreate,
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=0)  # Cambiado para permitir 0 para cardio libre
):
    """
    Create a new cardio exercise log entry for a training session.
    """
    try:
        # Verificar acceso a la sesión
        session = await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Verificar que la sesión esté activa
        stmt = select(TrainingSession.session_status).where(TrainingSession.id == session_id)
        result = await db.execute(stmt)
        session_status = result.scalar_one()
        
        if session_status != SessionStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Cannot add logs to an inactive session."
            )

        
        # Asegurarnos de que log_data tenga el user_id correcto
        log_data_dict = log_data.model_dump()
        log_data_dict["user_id"] = cast(int, current_user.id)
        
        # Decidir si es cardio programado o libre
        # Si exercise_id se proporciona en la URL (distinto de 0), es cardio programado
        if exercise_id and exercise_id > 0:
            log_data_dict["programmed_exercise_id"] = exercise_id
            log_data_dict["training_session_id"] = None
        else:
            # Es cardio libre, usar la sesión directamente
            log_data_dict["programmed_exercise_id"] = None
            log_data_dict["training_session_id"] = session_id
        
        # Crear el log de cardio
        new_log = await create_cardio_log(
            db=db,
            log_data=CardioLogCreate(**log_data_dict)
        )
        
        return new_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating cardio log: {str(e)}")

@router.put("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/strength/{log_id}", response_model=StrengthLogResponse)
async def update_strength_log_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    log_data: StrengthLogUpdate,
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1),
    log_id: int = Path(..., ge=1)
):
    """
    Update an existing strength exercise log entry.
    """
    try:
        # Verificar que el log existe
        existing_log = await get_strength_log(db, log_id)
        if not existing_log:
            raise HTTPException(status_code=404, detail="Strength log not found")
        
        # Verificar que el usuario es dueño del log
        if existing_log.user_id != cast(int, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this log")
        
        # Verificar que la sesión pertenece al programa y semana correctos
        await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Verificar que el log pertenece al ejercicio programado correcto en esta sesión
        # Necesitamos verificar via el programmed_exercise
        stmt = select(ProgrammedExercise.session_id).where(
            ProgrammedExercise.id == existing_log.programmed_exercise_id
        )
        result = await db.execute(stmt)
        log_session_id = result.scalar_one_or_none()
        
        if log_session_id != session_id:
            raise HTTPException(status_code=400, detail="This log does not belong to the specified session")
        
        # Actualizar el log
        updated_log = await update_strength_log(db, log_id, log_data)
        
        return updated_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating strength log: {str(e)}")

@router.put("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/cardio/{log_id}", response_model=CardioLogResponse)
async def update_cardio_log_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    log_data: CardioLogUpdate,
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1),
    log_id: int = Path(..., ge=1)
):
    """
    Update an existing cardio exercise log entry.
    """
    try:
        # Verificar que el log existe
        existing_log = await get_cardio_log(db, log_id)
        if not existing_log:
            raise HTTPException(status_code=404, detail="Cardio log not found")
        
        # Verificar que el usuario es dueño del log
        if existing_log.user_id != cast(int, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this log")
        
        # Verificar que la sesión pertenece al programa y semana correctos
        await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Verificar que el log pertenece a la sesión correcta
        # Para cardio puede ser programado (via programmed_exercise) o libre (via training_session)
        if existing_log.programmed_exercise_id:
            # Es cardio programado, verificar via programmed_exercise
            stmt = select(ProgrammedExercise.session_id).where(
                ProgrammedExercise.id == existing_log.programmed_exercise_id
            )
            result = await db.execute(stmt)
            log_session_id = result.scalar_one_or_none()
        else:
            # Es cardio libre, verificar directamente
            log_session_id = existing_log.training_session_id
        
        if log_session_id != session_id:
            raise HTTPException(status_code=400, detail="This log does not belong to the specified session")
        
        # Actualizar el log
        updated_log = await update_cardio_log(db, log_id, log_data)
        
        return updated_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating cardio log: {str(e)}")

@router.delete("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/strength/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strength_log_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1),
    log_id: int = Path(..., ge=1)
):
    """
    Delete a strength exercise log entry.
    """
    try:
        # Verificar que el log existe
        existing_log = await get_strength_log(db, log_id)
        if not existing_log:
            raise HTTPException(status_code=404, detail="Strength log not found")
        
        # Verificar que el usuario es dueño del log
        user_id_column = existing_log.user_id
        stmt = select(user_id_column)
        result = await db.execute(stmt)
        log_user_id = result.scalar_one()
        
        if log_user_id != cast(int, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this log")
        
        # Verificar que la sesión pertenece al programa y semana correctos
        await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Verificar que el log pertenece a la sesión
        session_id_column = existing_log.session_id
        stmt = select(session_id_column)
        result = await db.execute(stmt)
        log_session_id = result.scalar_one()
        
        if log_session_id != session_id:
            raise HTTPException(status_code=400, detail="This log does not belong to the specified session")
        
        # Eliminar el log
        await delete_strength_log(db, log_id)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting strength log: {str(e)}")

@router.delete("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/cardio/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cardio_log_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1),
    log_id: int = Path(..., ge=1)
):
    """
    Delete a cardio exercise log entry.
    """
    try:
        # Verificar que el log existe
        existing_log = await get_cardio_log(db, log_id)
        if not existing_log:
            raise HTTPException(status_code=404, detail="Cardio log not found")
        
        # Verificar que el usuario es dueño del log
        user_id_column = existing_log.user_id
        stmt = select(user_id_column)
        result = await db.execute(stmt)
        log_user_id = result.scalar_one()
        
        if log_user_id != cast(int, current_user.id):
            raise HTTPException(status_code=403, detail="Access denied to this log")
        
        # Verificar que la sesión pertenece al programa y semana correctos
        await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Verificar que el log pertenece a la sesión
        session_id_column = existing_log.session_id
        stmt = select(session_id_column)
        result = await db.execute(stmt)
        log_session_id = result.scalar_one()
        
        if log_session_id != session_id:
            raise HTTPException(status_code=400, detail="This log does not belong to the specified session")
        
        # Eliminar el log
        await delete_cardio_log(db, log_id)
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting cardio log: {str(e)}")
