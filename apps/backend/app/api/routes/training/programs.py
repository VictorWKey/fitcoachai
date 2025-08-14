"""
API endpoints for training programs.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc
from sqlalchemy.orm import selectinload
from typing import List, Annotated, Optional

from db.session import get_db
from db.models.user import User
from db.models.training_program import TrainingProgram
from db.models.training_week import TrainingWeek
from db.models.training_session import TrainingSession
from db.models.programmed_exercise import ProgrammedExercise
from db.models.strength_log import StrengthLog
from db.schemas.training_program import (
    TrainingProgramCreate, TrainingProgramUpdate, 
    TrainingProgramResponse, TrainingProgramSimpleResponse, 
    TrainingProgramSummary
)
from db.crud.training_program import (
    get_training_program, get_training_program_simple,
    get_user_training_programs, create_training_program,
    update_training_program, delete_training_program
)
from api.services.auth import get_current_verified_user
from typing import cast
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/programs", response_model=TrainingProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    program_data: TrainingProgramCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new training program.
    
    This endpoint allows users to create a complete training program with all its components:
    weeks, sessions, exercise blocks, and programmed exercises.
    """
    try:
        logger.info(f"Creating training program for user {current_user.id}: {program_data.name}")
        logger.debug(f"Program data: {program_data}")
        
        result = await create_training_program(db, program_data, cast(int, current_user.id))
        
        logger.info(f"Successfully created training program with ID: {result.id}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating training program for user {current_user.id}: {str(e)}")
        logger.exception("Full exception traceback:")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating training program: {str(e)}"
        )

@router.get("/programs", response_model=List[TrainingProgramSimpleResponse])
async def get_programs(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """
    Get all training programs for the current user.
    
    Returns a list of training programs without their nested components.
    """
    programs = await get_user_training_programs(db, cast(int, current_user.id))
    return programs[skip : skip + limit]

@router.get("/programs/{program_id}", response_model=TrainingProgramResponse)
async def get_program(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    include_details: bool = Query(False, description="Include all program details including weeks, sessions, exercises")
):
    """
    Get a specific training program.
    
    Returns the complete training program structure. Use include_details=False to get only summary.
    """
    if include_details:
        program = await get_training_program(db, program_id)
    else:
        program = await get_training_program_simple(db, program_id)
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found"
        )
    
    if cast(bool, program.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this training program"
        )
    
    return program

@router.get("/programs/{program_id}/summary", response_model=TrainingProgramSummary)
async def get_program_summary(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1)
):
    """
    Get a summary of a specific training program.
    
    Returns just the basic information about the program without nested components.
    """
    from db.crud.training_program import get_program_summary
    
    summary = await get_program_summary(db, program_id)
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found"
        )
    
    if cast(bool, summary["user_id"] != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this training program"
        )
    
    return summary

@router.patch("/programs/{program_id}", response_model=TrainingProgramResponse)
async def update_program(
    program_data: TrainingProgramUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1)
):
    """
    Update a training program.
    
    This endpoint allows users to update the properties of a training program.
    """
    program = await get_training_program(db, program_id)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found"
        )
    
    if cast(bool, program.user_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this training program"
        )
    
    updated_program = await update_training_program(db, program_id, program_data)
    return updated_program

@router.put("/programs/{program_id}", response_model=TrainingProgramResponse)
async def replace_program_complete(
    program_data: TrainingProgramCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1)
):
    """
    Replace entire training program structure (holistic approach).
    
    This endpoint allows users to completely replace a training program and all its components:
    weeks, sessions, exercise blocks, and programmed exercises. Maintains existing IDs where possible.
    """
    try:
        logger.info(f"Replacing training program {program_id} for user {current_user.id}")
        
        # Verify program exists and user has access
        existing_program = await get_training_program_simple(db, program_id)
        if not existing_program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training program not found"
            )
        
        if cast(bool, existing_program.user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this training program"
            )
        
        # Update program basic fields
        existing_program.name = program_data.name
        existing_program.description = program_data.description
        existing_program.program_type = program_data.program_type
        existing_program.duration_weeks = program_data.duration_weeks
        existing_program.is_ai_generated = program_data.is_ai_generated
        
        # Get current weeks to compare with new data
        current_weeks_stmt = select(TrainingWeek).where(
            TrainingWeek.program_id == program_id
        ).order_by(TrainingWeek.week_number)
        current_weeks_result = await db.execute(current_weeks_stmt)
        current_weeks = {week.week_number: week for week in current_weeks_result.scalars().all()}
        
        # Process weeks from new data
        new_week_numbers = set()
        if program_data.training_weeks:
            for week_data in program_data.training_weeks:
                new_week_numbers.add(week_data.week_number)
                
                if week_data.week_number in current_weeks:
                    # Update existing week
                    existing_week = current_weeks[week_data.week_number]
                    existing_week.description = week_data.description
                    await _update_week_sessions(db, existing_week.id, week_data.training_sessions or [])
                else:
                    # Create new week
                    new_week = TrainingWeek(
                        program_id=program_id,
                        week_number=week_data.week_number,
                        description=week_data.description
                    )
                    db.add(new_week)
                    await db.flush()  # Get the ID
                    await _update_week_sessions(db, new_week.id, week_data.training_sessions or [])
        
        # Delete weeks that are no longer in the new data
        weeks_to_delete = set(current_weeks.keys()) - new_week_numbers
        for week_number in weeks_to_delete:
            await db.delete(current_weeks[week_number])
        
        await db.commit()
        
        # Return updated program with full details
        updated_program = await get_training_program(db, program_id)
        logger.info(f"Successfully updated training program {program_id}")
        return updated_program
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error replacing training program {program_id} for user {current_user.id}: {str(e)}")
        logger.exception("Full exception traceback:")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error replacing training program: {str(e)}"
        )

async def _update_week_sessions(db: AsyncSession, week_id: int, sessions_data: List):
    """
    Update sessions for a week, maintaining existing IDs where possible.
    """
    from db.models.training_session import TrainingSession
    from db.models.programmed_exercise import ProgrammedExercise
    
    # Get current sessions
    current_sessions_stmt = select(TrainingSession).where(
        TrainingSession.week_id == week_id
    ).order_by(TrainingSession.session_order)
    current_sessions_result = await db.execute(current_sessions_stmt)
    current_sessions = {session.session_order: session for session in current_sessions_result.scalars().all()}
    
    # Process sessions from new data
    new_session_orders = set()
    for session_data in sessions_data:
        new_session_orders.add(session_data.session_order)
        
        if session_data.session_order in current_sessions:
            # Update existing session
            existing_session = current_sessions[session_data.session_order]
            existing_session.name = session_data.name
            existing_session.day_of_week = session_data.day_of_week
            existing_session.description = session_data.description
            await _update_session_exercises(db, existing_session.id, session_data.programmed_exercises or [])
        else:
            # Create new session
            new_session = TrainingSession(
                week_id=week_id,
                name=session_data.name,
                day_of_week=session_data.day_of_week,
                session_order=session_data.session_order,
                description=session_data.description
            )
            db.add(new_session)
            await db.flush()  # Get the ID
            await _update_session_exercises(db, new_session.id, session_data.programmed_exercises or [])
    
    # Delete sessions that are no longer in the new data
    sessions_to_delete = set(current_sessions.keys()) - new_session_orders
    for session_order in sessions_to_delete:
        await db.delete(current_sessions[session_order])

async def _update_session_exercises(db: AsyncSession, session_id: int, exercises_data: List):
    """
    Update exercises for a session, maintaining existing IDs where possible.
    """
    # Get current exercises
    current_exercises_stmt = select(ProgrammedExercise).where(
        ProgrammedExercise.session_id == session_id
    ).order_by(ProgrammedExercise.exercise_order)
    current_exercises_result = await db.execute(current_exercises_stmt)
    current_exercises = {exercise.exercise_order: exercise for exercise in current_exercises_result.scalars().all()}
    
    # Process exercises from new data
    new_exercise_orders = set()
    for exercise_data in exercises_data:
        new_exercise_orders.add(exercise_data.exercise_order)
        
        if exercise_data.exercise_order in current_exercises:
            # Update existing exercise
            existing_exercise = current_exercises[exercise_data.exercise_order]
            existing_exercise.standard_exercise_id = exercise_data.standard_exercise_id
            existing_exercise.block = exercise_data.block
            existing_exercise.tempo = exercise_data.tempo
            existing_exercise.sets = exercise_data.sets
            existing_exercise.reps = exercise_data.reps
            existing_exercise.load_type = exercise_data.load_type
            existing_exercise.rpe_target = exercise_data.rpe_target
            existing_exercise.percentage_1rm = exercise_data.percentage_1rm
            existing_exercise.weight_range = exercise_data.weight_range
            existing_exercise.rest_seconds = exercise_data.rest_seconds
            existing_exercise.sets_type = exercise_data.sets_type
            existing_exercise.notes = exercise_data.notes
        else:
            # Create new exercise
            new_exercise = ProgrammedExercise(
                session_id=session_id,
                standard_exercise_id=exercise_data.standard_exercise_id,
                block=exercise_data.block,
                exercise_order=exercise_data.exercise_order,
                tempo=exercise_data.tempo,
                sets=exercise_data.sets,
                reps=exercise_data.reps,
                load_type=exercise_data.load_type,
                rpe_target=exercise_data.rpe_target,
                percentage_1rm=exercise_data.percentage_1rm,
                weight_range=exercise_data.weight_range,
                rest_seconds=exercise_data.rest_seconds,
                sets_type=exercise_data.sets_type,
                notes=exercise_data.notes
            )
            db.add(new_exercise)
    
    # Delete exercises that are no longer in the new data
    exercises_to_delete = set(current_exercises.keys()) - new_exercise_orders
    for exercise_order in exercises_to_delete:
        await db.delete(current_exercises[exercise_order])

@router.delete("/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1)
):
    """
    Delete a training program.
    
    This endpoint allows users to delete a training program.
    """
    try:
        program = await get_training_program_simple(db, program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Training program not found"
            )
        
        if cast(bool, program.user_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this training program"
            )
        
        success = await delete_training_program(db, program_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete training program"
            )
        
        return None
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        logger.error(f"Error deleting training program {program_id}: {str(e)}")
        logger.exception("Full exception traceback:")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting training program: {str(e)}"
        )
