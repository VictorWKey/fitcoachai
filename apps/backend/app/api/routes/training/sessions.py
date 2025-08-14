"""
API endpoints for training sessions.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Annotated, Optional
from pydantic import BaseModel

from db.session import get_db
from db.models.user import User
from db.models.training_program import TrainingProgram
from db.models.training_week import TrainingWeek
from db.models.training_session import TrainingSession, SessionStatus
from db.models.programmed_exercise import ProgrammedExercise
from db.schemas.training_program import (
    TrainingSessionResponse, TrainingSessionListResponse
)
from db.crud.training_session import (
    get_session_with_exercises,
    start_training_session,
    finish_training_session,
    get_active_session_for_user,
    TrainingSessionNotFoundError,
    SessionAlreadyActiveError,
    NoActiveSessionError
)
from api.services.auth import get_current_verified_user

router = APIRouter()

class FinishSessionRequest(BaseModel):
    """Request model for finishing a session with optional duration."""
    duration_seconds: Optional[int] = None

@router.get("/programs/{program_id}/weeks/{week_id}/sessions", response_model=List[TrainingSessionListResponse])
async def get_week_sessions(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1)
):
    """
    Get all sessions for a specific training week.
    
    Returns a simplified list of training sessions with only essential fields.
    """
    # Verify week exists and user has access to the program
    stmt = select(TrainingWeek).join(TrainingProgram).where(
        TrainingWeek.id == week_id,
        TrainingWeek.program_id == program_id,
        TrainingProgram.user_id == current_user.id
    )
    result = await db.execute(stmt)
    week = result.scalar_one_or_none()

    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training week not found or access denied"
        )

    # Get sessions for the week
    stmt = select(TrainingSession).where(
        TrainingSession.week_id == week_id
    ).order_by(TrainingSession.session_order)

    result = await db.execute(stmt)
    sessions = result.scalars().all()

    # Return sessions directly - Pydantic will handle the transformation using the schema
    return sessions

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}", response_model=TrainingSessionResponse)
async def get_week_session(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    include_exercises: bool = Query(False, description="Include exercise blocks in response")
):
    """
    Get a specific session from a training week.
    
    Returns details of the training session. Use include_exercises=True to include exercise blocks.
    """
    # Verify week exists and user has access to the program
    stmt = select(TrainingWeek).join(TrainingProgram).where(
        TrainingWeek.id == week_id,
        TrainingWeek.program_id == program_id,
        TrainingProgram.user_id == current_user.id
    )
    result = await db.execute(stmt)
    week = result.scalar_one_or_none()
    
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training week not found or access denied"
        )
    
    # Get the specific session
    if include_exercises:
        session = await get_session_with_exercises(db, session_id)
    else:
        stmt = select(TrainingSession).where(
            TrainingSession.id == session_id,
            TrainingSession.week_id == week_id
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    
    return session

# ============================================================================
# SESSION STATUS MANAGEMENT
# ============================================================================

@router.post("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/start")
async def start_session(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Start a training session for exercise logging.
    """
    try:
        session = await start_training_session(db, current_user.id, session_id)
        return {
            "message": "Training session started successfully",
            "session": {
                "id": session.id,
                "name": session.name,
                "week_id": session.week_id,
                "day_of_week": session.day_of_week,
                "session_status": session.session_status.value,
                "start_time": session.session_start_time
            }
        }
    except SessionAlreadyActiveError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TrainingSessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")

@router.post("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/finish")
async def finish_session(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    finish_data: Optional[FinishSessionRequest] = Body(None)
):
    """
    Finish the training session by ID.
    
    Can optionally receive duration_seconds from frontend for timer-based sessions.
    If no duration provided, calculates duration based on session timestamps.
    """
    try:
        # Verify session belongs to the specified week and program
        stmt = select(TrainingSession).join(
            TrainingWeek, TrainingSession.week_id == TrainingWeek.id
        ).join(
            TrainingProgram, TrainingWeek.program_id == TrainingProgram.id
        ).where(
            TrainingSession.id == session_id,
            TrainingWeek.id == week_id,
            TrainingProgram.id == program_id,
            TrainingProgram.user_id == current_user.id
        )
        result = await db.execute(stmt)
        session_check = result.scalar_one_or_none()
        
        if not session_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training session not found or does not belong to the specified week/program"
            )
        
        # Extract duration from request if provided
        frontend_duration = finish_data.duration_seconds if finish_data else None
        
        session = await finish_training_session(
            db, 
            current_user.id, 
            session_id, 
            frontend_duration_seconds=frontend_duration
        )
        return {
            "message": "Training session finished successfully",
            "session": {
                "id": session.id,
                "name": session.name,
                "duration_seconds": session.session_duration_seconds,
                "completion_percentage": session.session_completion_percentage,
                "end_time": session.session_end_time
            }
        }
    except NoActiveSessionError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TrainingSessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finishing session: {str(e)}")

@router.get("/active-session")
async def get_active_session(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get the currently active training session for the user, if any.
    """
    try:
        session = await get_active_session_for_user(db, current_user.id)
        if not session:
            return {"message": "No active session found", "active": False}
        
        return {
            "message": "Active session found",
            "active": True,
            "session": {
                "id": session.id,
                "name": session.name,
                "week_id": session.week_id,
                "status": session.session_status.value,
                "start_time": session.session_start_time
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving active session: {str(e)}")
