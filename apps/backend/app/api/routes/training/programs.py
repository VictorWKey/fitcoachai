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
