"""
Flexibility exercise routes for mobility and stretching training.
Handles CRUD operations and specific analytics for flexibility training.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Dict, Any, Annotated, Optional
from datetime import datetime, timedelta

from db.schemas.user import User
from db.schemas.discipline_exercise_logs.flexibility import (
    FlexibilityLogCreate, 
    FlexibilityLogUpdate, 
    FlexibilityLogBase
)
from db.models.discipline_exercise_logs.flexibility import FlexibilityLog
from db.crud.discipline_exercise_logs.flexibility import (
    create_flexibility_log,
    get_flexibility_log,
    get_user_flexibility_logs,
    get_workout_flexibility_logs,
    update_flexibility_log,
    delete_flexibility_log
)
from db.session import get_db
from api.services import get_current_verified_user

flexibility_router = APIRouter(prefix="/flexibility", tags=["flexibility"])

@flexibility_router.post("/", response_model=FlexibilityLogBase)
async def create_flexibility_exercise(
    log_data: FlexibilityLogCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Create a new flexibility exercise log."""
    return await create_flexibility_log(db, log_data, current_user.id)

@flexibility_router.get("/{log_id}", response_model=FlexibilityLogBase)
async def get_flexibility_exercise(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get a specific flexibility exercise log by ID."""
    log = await get_flexibility_log(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flexibility log not found"
        )

    if getattr(log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flexibility log not found"
        )
    return log

@flexibility_router.get("/", response_model=List[FlexibilityLogBase])
async def get_user_flexibility_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all flexibility exercise logs for the current user."""
    return await get_user_flexibility_logs(db, current_user.id, skip, limit)

@flexibility_router.get("/workout/{workout_id}", response_model=List[FlexibilityLogBase])
async def get_workout_flexibility_exercises(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get all flexibility exercises for a specific workout."""
    return await get_workout_flexibility_logs(db, workout_id)

@flexibility_router.put("/{log_id}", response_model=FlexibilityLogBase)
async def update_flexibility_exercise(
    log_id: int,
    log_update: FlexibilityLogUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update a flexibility exercise log."""
    existing_log = await get_flexibility_log(db, log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flexibility log not found"
        )

    if getattr(existing_log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flexibility log not found"
        )
    
    updated_log = await update_flexibility_log(db, log_id, log_update)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update flexibility log"
        )
    
    return updated_log

@flexibility_router.delete("/{log_id}")
async def delete_flexibility_exercise(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Delete a flexibility exercise log."""
    existing_log = await get_flexibility_log(db, log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flexibility log not found"
        )

    if getattr(existing_log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flexibility log not found"
        )
    
    success = await delete_flexibility_log(db, log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete flexibility log"
        )
    
    return {"message": "Flexibility log deleted successfully"}