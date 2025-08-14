"""
API endpoints for programmed exercises.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Annotated

from db.session import get_db
from db.models.user import User
from db.models.training_program import TrainingProgram
from db.models.training_week import TrainingWeek
from db.models.training_session import TrainingSession
from db.models.programmed_exercise import ProgrammedExercise, BlockType
from db.schemas.training_program import (
    SessionExercisesResponse
)
from api.services.auth import get_current_verified_user

router = APIRouter()

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises", response_model=SessionExercisesResponse)
async def get_session_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Get all exercises for a training session, grouped by block type (main/accessory).
    """
    # Verify user has access to the program
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
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found or access denied"
        )
    
    # Get all exercises for the session with their standard exercises
    stmt = select(ProgrammedExercise).options(
        selectinload(ProgrammedExercise.standard_exercise)
    ).where(
        ProgrammedExercise.session_id == session_id
    ).order_by(ProgrammedExercise.exercise_order)
    
    result = await db.execute(stmt)
    exercises = result.scalars().all()

    main_exercises = []
    accessory_exercises = []

    for exercise in exercises:
        # Set the exercise_name from the standard_exercise relationship
        if exercise.standard_exercise:
            exercise.exercise_name = exercise.standard_exercise.standard_name
        else:
            exercise.exercise_name = None
        
        # Group by block type while preserving exercise_order
        if exercise.block == BlockType.MAIN:
            main_exercises.append(exercise)
        elif exercise.block == BlockType.ACCESSORY:
            accessory_exercises.append(exercise)

    return {
        "main": main_exercises,
        "accessory": accessory_exercises
    }
