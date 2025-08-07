"""
API endpoints for training weeks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Annotated, Optional, Union

from db.session import get_db
from db.models.user import User
from db.models.training_program import TrainingProgram
from db.models.training_week import TrainingWeek
from db.schemas.training_program import (
    TrainingWeekResponse, TrainingWeekCreate, TrainingWeekUpdate, TrainingWeekListResponse
)
from api.services.auth import get_current_verified_user
from typing import cast

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

@router.post("/programs/{program_id}/weeks", response_model=TrainingWeekResponse, status_code=status.HTTP_201_CREATED)
async def create_program_week(
    week_data: TrainingWeekCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1)
):
    """
    Create a new week for a training program.
    
    This endpoint allows users to add a new week to an existing training program.
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
    
    # Create the new week
    new_week = TrainingWeek(
        program_id=program_id,
        week_number=week_data.week_number,
        description=week_data.description
    )
    
    db.add(new_week)
    await db.commit()
    await db.refresh(new_week)
    
    # Add sessions if provided
    if hasattr(week_data, 'training_sessions') and week_data.training_sessions:
        for session_data in week_data.training_sessions:
            # Create session implementation
            pass
    
    return new_week

@router.patch("/programs/{program_id}/weeks/{week_id}", response_model=TrainingWeekResponse)
async def update_program_week(
    week_data: TrainingWeekUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1)
):
    """
    Update a week in a training program.
    
    This endpoint allows users to update the properties of a training week.
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
    
    # Get the week to update
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
    
    # Update week fields
    if week_data.week_number is not None:
        week.week_number = week_data.week_number
    if week_data.description is not None:
        week.description = week_data.description
    
    await db.commit()
    await db.refresh(week)
    
    return week

@router.delete("/programs/{program_id}/weeks/{week_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program_week(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    program_id: int = Path(..., ge=1),
    week_id: int = Path(..., ge=1)
):
    """
    Delete a week from a training program.
    
    This endpoint allows users to remove a week from a training program.
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
    
    # Get the week to delete
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
    
    # Delete the week
    await db.delete(week)
    await db.commit()
    
    return None
