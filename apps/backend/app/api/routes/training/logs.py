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
        selectinload(TrainingSession.strength_logs),
        selectinload(TrainingSession.cardio_logs),
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

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/logs", response_model=Dict[str, List[Any]])
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
        logs = await get_all_session_logs(db, session_id)
        
        return logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session logs: {str(e)}")

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/logs/strength", response_model=List[StrengthLogResponse])
async def get_session_strength_logs_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Get all strength exercise logs for a specific training session.
    """
    try:
        # Verificar acceso a la sesión
        session = await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Update last activity if session is active
        stmt = select(TrainingSession.session_status).where(TrainingSession.id == session_id)
        result = await db.execute(stmt)
        session_status = result.scalar_one()
        

        
        # Get strength logs for the session
        logs = await get_session_strength_logs(db, session_id)
        
        return logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving strength logs: {str(e)}")

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/logs/cardio", response_model=List[CardioLogResponse])
async def get_session_cardio_logs_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Get all cardio exercise logs for a specific training session.
    """
    try:
        # Verificar acceso a la sesión
        session = await verify_session_access(db, session_id, program_id, week_id, cast(int, current_user.id))
        
        # Update last activity if session is active
        stmt = select(TrainingSession.session_status).where(TrainingSession.id == session_id)
        result = await db.execute(stmt)
        session_status = result.scalar_one()
        

        
        # Get cardio logs for the session
        logs = await get_session_cardio_logs(db, session_id)
        
        return logs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cardio logs: {str(e)}")

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
        log_data_dict = log_data.dict()
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
    exercise_id: int = Path(..., ge=1)
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
        log_data_dict = log_data.dict()
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

@router.post("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/logs/cardio", response_model=CardioLogResponse, status_code=status.HTTP_201_CREATED)
async def create_free_cardio_log_endpoint(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    log_data: CardioLogCreate,
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Create a new free cardio exercise log entry for a training session (not linked to a programmed exercise).
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

        # Asegurarnos de que log_data tenga el user_id correcto para cardio libre
        log_data_dict = log_data.dict()
        log_data_dict["user_id"] = cast(int, current_user.id)
        log_data_dict["programmed_exercise_id"] = None
        log_data_dict["training_session_id"] = session_id
        
        # Crear el log de cardio libre
        new_log = await create_cardio_log(
            db=db,
            log_data=CardioLogCreate(**log_data_dict)
        )
        
        return new_log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating free cardio log: {str(e)}")

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
