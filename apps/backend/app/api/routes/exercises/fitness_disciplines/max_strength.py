"""
Max strength exercise routes for powerlifting and olympic lifting.
Handles CRUD operations and specific analytics for max strength training.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Dict, Any, Annotated, Optional
from datetime import datetime, timedelta

from db.schemas.user import User
from db.schemas.discipline_exercise_logs.max_strength import (
    MaxStrengthLogCreate, 
    MaxStrengthLogUpdate, 
    MaxStrengthLogBase
)
from db.models.discipline_exercise_logs.max_strength import MaxStrengthLog
from db.crud.discipline_exercise_logs.max_strength import (
    create_max_strength_log,
    get_max_strength_log,
    get_user_max_strength_logs,
    get_workout_max_strength_logs,
    update_max_strength_log,
    delete_max_strength_log
)
from db.session import get_db
from api.services import get_current_verified_user

max_strength_router = APIRouter(prefix="/max-strength", tags=["max-strength"])

@max_strength_router.post("/", response_model=MaxStrengthLogBase)
async def create_max_strength_exercise(
    log_data: MaxStrengthLogCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new max strength exercise log.
    
    Args:
        log_data: Max strength exercise data
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        MaxStrengthLogBase: Created max strength log
    """
    return await create_max_strength_log(db, log_data, current_user.id)

@max_strength_router.get("/{log_id}", response_model=MaxStrengthLogBase)
async def get_max_strength_exercise(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get a specific max strength exercise log by ID.
    
    Args:
        log_id: ID of the exercise log
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        MaxStrengthLogBase: Max strength exercise log
        
    Raises:
        HTTPException: If log not found or user doesn't have access
    """
    log = await get_max_strength_log(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Max strength log not found"
        )
    if getattr(log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Max strength log not found"
        )
    return log

@max_strength_router.get("/", response_model=List[MaxStrengthLogBase])
async def get_user_max_strength_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get all max strength exercise logs for the current user.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[MaxStrengthLogBase]: List of max strength exercise logs
    """
    return await get_user_max_strength_logs(db, current_user.id, skip, limit)

@max_strength_router.get("/workout/{workout_id}", response_model=List[MaxStrengthLogBase])
async def get_workout_max_strength_exercises(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get all max strength exercises for a specific workout.
    
    Args:
        workout_id: ID of the workout
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        List[MaxStrengthLogBase]: List of max strength exercises in the workout
    """
    return await get_workout_max_strength_logs(db, workout_id)

@max_strength_router.put("/{log_id}", response_model=MaxStrengthLogBase)
async def update_max_strength_exercise(
    log_id: int,
    log_update: MaxStrengthLogUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update a max strength exercise log.
    
    Args:
        log_id: ID of the exercise log to update
        log_update: Updated exercise data
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        MaxStrengthLogBase: Updated max strength log
        
    Raises:
        HTTPException: If log not found or user doesn't have access
    """
    # Verify ownership
    existing_log = await get_max_strength_log(db, log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Max strength log not found"
        )
    if getattr(existing_log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Max strength log not found"
        )
    
    updated_log = await update_max_strength_log(db, log_id, log_update)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update max strength log"
        )
    
    return updated_log

@max_strength_router.delete("/{log_id}")
async def delete_max_strength_exercise(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete a max strength exercise log.
    
    Args:
        log_id: ID of the exercise log to delete
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Dict: Success message
        
    Raises:
        HTTPException: If log not found or user doesn't have access
    """
    # Verify ownership
    existing_log = await get_max_strength_log(db, log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Max strength log not found"
        )
    if getattr(existing_log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Max strength log not found"
        )
    
    success = await delete_max_strength_log(db, log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete max strength log"
        )
    
    return {"message": "Max strength log deleted successfully"}
