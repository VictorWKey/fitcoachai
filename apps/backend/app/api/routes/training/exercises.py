"""
API endpoints for programmed exercises.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
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
    ProgrammedExerciseUpdate,
    ExerciseReorderRequest
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
    
    # Calculate exercise_order if not provided
    exercise_order = exercise_data.exercise_order
    if exercise_order is None:
        # Get the highest order in the session and add 1
        order_stmt = select(func.coalesce(func.max(ProgrammedExercise.exercise_order), -1)).where(
            ProgrammedExercise.session_id == session_id
        )
        result = await db.execute(order_stmt)
        max_order = result.scalar()
        exercise_order = max_order + 1
    else:
        # If order is specified, shift existing exercises
        await _shift_exercises_order(db, session_id, exercise_order, shift_up=True)

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
        exercise_order=exercise_order,
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
    stmt = select(ProgrammedExercise).options(
        selectinload(ProgrammedExercise.standard_exercise)
    ).join(
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
    update_data = exercise_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exercise, field, value)
    
    await db.commit()
    await db.refresh(exercise)
    
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
    
    # Reorder remaining exercises to fill the gap
    await _compact_exercises_order(db, exercise.session_id)
    
    return None


@router.patch("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/reorder", response_model=List[ProgrammedExerciseResponse])
async def reorder_session_exercises(
    reorder_data: ExerciseReorderRequest,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Reorder exercises within a training session.
    
    Send the complete list of exercises with their new order positions.
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

    # Validate that all exercises belong to this session
    exercise_ids = [item.id for item in reorder_data.exercises]
    stmt = select(ProgrammedExercise).where(
        ProgrammedExercise.id.in_(exercise_ids),
        ProgrammedExercise.session_id == session_id
    )
    result = await db.execute(stmt)
    exercises = result.scalars().all()
    
    if len(exercises) != len(exercise_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some exercises do not belong to this session"
        )
    
    # Update exercise orders
    exercise_map = {ex.id: ex for ex in exercises}
    for item in reorder_data.exercises:
        if item.id in exercise_map:
            exercise_map[item.id].exercise_order = item.exercise_order
    
    await db.commit()
    
    # Return updated exercises in order
    stmt = select(ProgrammedExercise).options(
        selectinload(ProgrammedExercise.standard_exercise)
    ).where(
        ProgrammedExercise.session_id == session_id
    ).order_by(ProgrammedExercise.exercise_order)
    
    result = await db.execute(stmt)
    updated_exercises = result.scalars().all()
    
    # Set exercise names
    for exercise in updated_exercises:
        if exercise.standard_exercise:
            exercise.exercise_name = exercise.standard_exercise.standard_name
        else:
            exercise.exercise_name = None
    
    return updated_exercises


# Helper functions for exercise ordering
async def _shift_exercises_order(db: AsyncSession, session_id: int, from_order: int, shift_up: bool = True):
    """
    Shift exercises order to make space for insertion or fill gaps after deletion.
    
    Args:
        db: Database session
        session_id: Session ID
        from_order: Starting order position
        shift_up: True to shift up (+1), False to shift down (-1)
    """
    if shift_up:
        stmt = (
            update(ProgrammedExercise)
            .where(
                ProgrammedExercise.session_id == session_id,
                ProgrammedExercise.exercise_order >= from_order
            )
            .values(exercise_order=ProgrammedExercise.exercise_order + 1)
        )
    else:
        stmt = (
            update(ProgrammedExercise)
            .where(
                ProgrammedExercise.session_id == session_id,
                ProgrammedExercise.exercise_order > from_order
            )
            .values(exercise_order=ProgrammedExercise.exercise_order - 1)
        )
    
    await db.execute(stmt)


async def _compact_exercises_order(db: AsyncSession, session_id: int):
    """
    Compact exercise order to remove gaps (0, 1, 2, 3...).
    
    Args:
        db: Database session
        session_id: Session ID
    """
    # Get all exercises ordered by current order
    stmt = select(ProgrammedExercise).where(
        ProgrammedExercise.session_id == session_id
    ).order_by(ProgrammedExercise.exercise_order)
    
    result = await db.execute(stmt)
    exercises = result.scalars().all()
    
    # Reassign sequential order
    for i, exercise in enumerate(exercises):
        exercise.exercise_order = i
    
    await db.commit()
