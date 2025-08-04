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
from db.models.exercise_block import ExerciseBlock
from db.models.programmed_exercise import ProgrammedExercise
from db.schemas.training_program import (
    ExerciseBlockResponse, ProgrammedExerciseResponse,
    ExerciseBlockCreate, ProgrammedExerciseCreate,
    ExerciseBlockUpdate, ProgrammedExerciseUpdate
)
from api.services.auth import get_current_verified_user
from typing import cast

router = APIRouter()

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/blocks", response_model=List[ExerciseBlockResponse])
async def get_session_blocks(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Get all exercise blocks for a specific training session.
    
    Returns a list of exercise blocks without their nested exercises.
    """
    # Verify session exists and user has access
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
    
    # Get blocks for the session
    stmt = select(ExerciseBlock).where(
        ExerciseBlock.session_id == session_id
    ).order_by(ExerciseBlock.order)
    
    result = await db.execute(stmt)
    blocks = result.scalars().all()
    
    return blocks

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/blocks/{block_id}", response_model=ExerciseBlockResponse)
async def get_session_block(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    block_id: int = Path(..., ge=1),
    include_exercises: bool = Query(True, description="Include programmed exercises in response")
):
    """
    Get a specific exercise block from a training session.
    
    Returns details of the exercise block. By default includes exercises.
    """
    # Verify session exists and user has access
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
    
    # Get the specific block
    if include_exercises:
        stmt = select(ExerciseBlock).options(
            selectinload(ExerciseBlock.programmed_exercises)
        ).where(
            ExerciseBlock.id == block_id,
            ExerciseBlock.session_id == session_id
        )
    else:
        stmt = select(ExerciseBlock).where(
            ExerciseBlock.id == block_id,
            ExerciseBlock.session_id == session_id
        )
    
    result = await db.execute(stmt)
    block = result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise block not found"
        )
    
    return block

@router.get("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises", response_model=List[ProgrammedExerciseResponse])
async def get_session_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Get all programmed exercises for a specific training session across all blocks.
    
    Returns a flat list of all exercises in the session, including their block information.
    """
    # Verify session exists and user has access
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
    
    # Get all exercises for the session
    stmt = select(ProgrammedExercise).join(
        ExerciseBlock, ProgrammedExercise.block_id == ExerciseBlock.id
    ).where(
        ExerciseBlock.session_id == session_id
    ).order_by(ExerciseBlock.order, ProgrammedExercise.id)
    
    result = await db.execute(stmt)
    exercises = result.scalars().all()
    
    return exercises

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
    Get a specific programmed exercise from a training session.
    
    Returns details of the programmed exercise.
    """
    # Verify session exists and user has access
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
    
    # Get the specific exercise
    stmt = select(ProgrammedExercise).join(
        ExerciseBlock, ProgrammedExercise.block_id == ExerciseBlock.id
    ).where(
        ProgrammedExercise.id == exercise_id,
        ExerciseBlock.session_id == session_id
    )
    
    result = await db.execute(stmt)
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Programmed exercise not found"
        )
    
    return exercise

@router.post("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/blocks", response_model=ExerciseBlockResponse, status_code=status.HTTP_201_CREATED)
async def create_session_block(
    block_data: ExerciseBlockCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1)
):
    """
    Create a new exercise block for a training session.
    
    This endpoint allows users to add a new exercise block to an existing training session.
    """
    # Verify session exists and user has access
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
    
    # Create the new block
    new_block = ExerciseBlock(
        session_id=session_id,
        name=block_data.name,
        block_type=block_data.block_type,
        order=block_data.order,
        description=block_data.description
    )
    
    db.add(new_block)
    await db.commit()
    await db.refresh(new_block)
    
    # Add exercises if provided
    if hasattr(block_data, 'programmed_exercises') and block_data.programmed_exercises:
        for exercise_data in block_data.programmed_exercises:
            # Create exercise implementation
            pass
    
    return new_block

@router.post("/programs/{program_id}/weeks/{week_id}/sessions/{session_id}/blocks/{block_id}/exercises", response_model=ProgrammedExerciseResponse, status_code=status.HTTP_201_CREATED)
async def create_block_exercise(
    exercise_data: ProgrammedExerciseCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    session_id: int = Path(..., ge=1),
    block_id: int = Path(..., ge=1)
):
    """
    Add a new programmed exercise to an exercise block.
    
    This endpoint allows users to add a new exercise to an existing exercise block.
    """
    # Verify block exists and user has access to the program
    stmt = select(ExerciseBlock).join(
        TrainingSession, ExerciseBlock.session_id == TrainingSession.id
    ).join(
        TrainingWeek, TrainingSession.week_id == TrainingWeek.id
    ).join(
        TrainingProgram, TrainingWeek.program_id == TrainingProgram.id
    ).where(
        ExerciseBlock.id == block_id,
        TrainingSession.id == session_id,
        TrainingWeek.id == week_id,
        TrainingProgram.id == program_id,
        TrainingProgram.user_id == current_user.id
    )
    result = await db.execute(stmt)
    block = result.scalar_one_or_none()
    
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise block not found or access denied"
        )
    
    # Create the new exercise
    new_exercise = ProgrammedExercise(
        block_id=block_id,
        standard_exercise_id=exercise_data.standard_exercise_id,
        tempo=exercise_data.tempo,
        sets=exercise_data.sets,
        reps=exercise_data.reps,
        load_type=exercise_data.load_type,
        load_value=exercise_data.load_value,
        rpe_target=exercise_data.rpe_target,
        percentage_1rm=exercise_data.percentage_1rm,
        weight_range=exercise_data.weight_range,
        rest_seconds=exercise_data.rest_seconds,
        sets_type=exercise_data.sets_type,
        custom_parameters=exercise_data.custom_parameters
    )
    
    db.add(new_exercise)
    await db.commit()
    await db.refresh(new_exercise)
    
    return new_exercise
