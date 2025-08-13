"""
API endpoints for programmed exercises.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Annotated, Optional

from db.session import get_db
from db.models.user import User
from db.models.training_program import TrainingProgram
from db.models.training_week import TrainingWeek
from db.models.training_session import TrainingSession
from db.models.programmed_exercise import ProgrammedExercise, BlockType
from db.schemas.training_program import (
    ProgrammedExerciseResponse, SessionExercisesResponse,
    ProgrammedExerciseCreate,
    ProgrammedExerciseUpdate
)
from api.services.auth import get_current_verified_user
from core.services.exercise_analysis import infer_series_type
from typing import cast

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
    ).order_by(ProgrammedExercise.block, ProgrammedExercise.id)
    
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
        
        # Group by block type
        if exercise.block == BlockType.MAIN:
            main_exercises.append(exercise)
        elif exercise.block == BlockType.ACCESSORY:
            accessory_exercises.append(exercise)

    return {
        "main": main_exercises,
        "accessory": accessory_exercises
    }

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}", response_model=ProgrammedExerciseResponse)
async def get_session_exercise(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1)
):
    """
    Get a specific exercise from a training session.
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
    
    # Get the specific exercise with standard exercise
    stmt = select(ProgrammedExercise).options(
        selectinload(ProgrammedExercise.standard_exercise)
    ).where(
        ProgrammedExercise.id == exercise_id,
        ProgrammedExercise.session_id == session_id
    )
    
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programmed exercise not found"
        )
    
    # Set the exercise_name from the standard_exercise relationship
    if exercise.standard_exercise:
        exercise.exercise_name = exercise.standard_exercise.standard_name
    else:
        exercise.exercise_name = None
    
    return exercise

@router.post("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises", response_model=ProgrammedExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_session_exercise(
    exercise_data: ProgrammedExerciseCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Add a new programmed exercise to a training session.
    """
    # Verify session exists and user has access to the program
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
    
    # Calculate sets_type automatically if not provided
    calculated_sets_type = exercise_data.sets_type
    if calculated_sets_type is None:
        calculated_sets_type = infer_series_type(
            reps=exercise_data.reps,
            one_rm_percentage=exercise_data.percentage_1rm,
            rpe=exercise_data.rpe_target,
            tempo=exercise_data.tempo,
            rest_time_seconds=exercise_data.rest_seconds
        )
    
    # Create the new exercise
    new_exercise = ProgrammedExercise(
        session_id=session_id,
        standard_exercise_id=exercise_data.standard_exercise_id,
        block=exercise_data.block,
        tempo=exercise_data.tempo,
        sets=exercise_data.sets,
        reps=exercise_data.reps,
        load_type=exercise_data.load_type,
        rpe_target=exercise_data.rpe_target,
        percentage_1rm=exercise_data.percentage_1rm,
        weight_range=exercise_data.weight_range,
        rest_seconds=exercise_data.rest_seconds,
        sets_type=calculated_sets_type,
        notes=exercise_data.notes
    )
    
    db.add(new_exercise)
    await db.commit()
    await db.refresh(new_exercise, ['standard_exercise'])
    
    # Set the exercise_name from the standard_exercise relationship
    if new_exercise.standard_exercise:
        new_exercise.exercise_name = new_exercise.standard_exercise.standard_name
    else:
        new_exercise.exercise_name = None
    
    return new_exercise

@router.put("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}", response_model=ProgrammedExerciseResponse)
async def update_session_exercise(
    exercise_data: ProgrammedExerciseUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1)
):
    """
    Update a programmed exercise in a training session.
    """
    # Verify user has access to the program and exercise
    stmt = select(ProgrammedExercise).join(
        TrainingSession, ProgrammedExercise.session_id == TrainingSession.id
    ).join(
        TrainingWeek, TrainingSession.week_id == TrainingWeek.id
    ).join(
        TrainingProgram, TrainingWeek.program_id == TrainingProgram.id
    ).where(
        ProgrammedExercise.id == exercise_id,
        TrainingSession.id == session_id,
        TrainingWeek.id == week_id,
        TrainingProgram.id == program_id,
        TrainingProgram.user_id == current_user.id
    )
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programmed exercise not found or access denied"
        )
    
    # Update the exercise
    update_data = exercise_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    
    await db.commit()
    await db.refresh(exercise, ['standard_exercise'])
    
    # Set the exercise_name from the standard_exercise relationship
    if exercise.standard_exercise:
        exercise.exercise_name = exercise.standard_exercise.standard_name
    else:
        exercise.exercise_name = None
    
    return exercise

@router.delete("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session_exercise(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    exercise_id: int = Path(..., ge=1)
):
    """
    Delete a programmed exercise from a training session.
    """
    # Verify user has access to the program and exercise
    stmt = select(ProgrammedExercise).join(
        TrainingSession, ProgrammedExercise.session_id == TrainingSession.id
    ).join(
        TrainingWeek, TrainingSession.week_id == TrainingWeek.id
    ).join(
        TrainingProgram, TrainingWeek.program_id == TrainingProgram.id
    ).where(
        ProgrammedExercise.id == exercise_id,
        TrainingSession.id == session_id,
        TrainingWeek.id == week_id,
        TrainingProgram.id == program_id,
        TrainingProgram.user_id == current_user.id
    )
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programmed exercise not found or access denied"
        )
    
    await db.delete(exercise)
    await db.commit()
    
    return None
