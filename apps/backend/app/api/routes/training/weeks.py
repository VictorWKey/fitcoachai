"""
API endpoints for training weeks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Annotated

from db.session import get_db
from db.models.user import User
from db.models.training_program import TrainingProgram
from db.models.training_week import TrainingWeek
from db.schemas.training_program import (
    TrainingWeekResponse, TrainingWeekListResponse
)
from api.services.auth import get_current_verified_user

router = APIRouter()

@router.get("/programs/{program_id}/weeks", response_model=List[TrainingWeekListResponse])
async def get_program_weeks(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1)
):
    """
    Get all weeks for a specific training program.
    
    Returns only basic week information: id, week_number, and description.
    """
    # Verify program exists and user has access
    stmt = select(TrainingProgram).where(
        TrainingProgram.id == program_id,
        TrainingProgram.user_id == current_user.id
    )
    result = await db.execute(stmt)
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found or access denied"
        )
    
    # Get weeks for the program - no need for eager loading now
    stmt = select(TrainingWeek).where(
        TrainingWeek.program_id == program_id
    ).order_by(TrainingWeek.week_number)
    
    result = await db.execute(stmt)
    weeks = result.scalars().all()
    
    return weeks

@router.get("/programs/{program_id}/weeks/{week_id}", response_model=TrainingWeekResponse)
async def get_program_week(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1),
    include_sessions: bool = Query(False, description="Include training sessions in response")
):
    """
    Get a specific week from a training program.
    
    Returns details of the training week. Use include_sessions=True to include sessions.
    """
    # Verify program exists and user has access
    stmt = select(TrainingProgram).where(
        TrainingProgram.id == program_id,
        TrainingProgram.user_id == current_user.id
    )
    result = await db.execute(stmt)
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found or access denied"
        )
    
    # Get the specific week
    if include_sessions:
        stmt = select(TrainingWeek).options(
            selectinload(TrainingWeek.training_sessions)
        ).where(
            TrainingWeek.id == week_id,
            TrainingWeek.program_id == program_id
        )
    else:
        stmt = select(TrainingWeek).where(
            TrainingWeek.id == week_id,
            TrainingWeek.program_id == program_id
        )
    
    result = await db.execute(stmt)
    week = result.scalar_one_or_none()
    
    if not week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training week not found"
        )
    
    return week
