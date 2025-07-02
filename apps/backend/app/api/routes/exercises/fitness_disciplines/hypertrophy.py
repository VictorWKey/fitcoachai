"""
Hypertrophy exercise routes for bodybuilding and fitness training.
Handles CRUD operations and specific analytics for hypertrophy training.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Dict, Any, Annotated, Optional
from datetime import datetime, timedelta

from db.schemas.user import User
from db.schemas.discipline_exercise_logs.hypertrophy import (
    HypertrophyLogCreate, 
    HypertrophyLogUpdate, 
    HypertrophyLogBase
)
from db.models.discipline_exercise_logs.hypertrophy import HypertrophyLog
from db.crud.discipline_exercise_logs.hypertrophy import (
    create_hypertrophy_log,
    get_hypertrophy_log,
    get_user_hypertrophy_logs,
    get_workout_hypertrophy_logs,
    update_hypertrophy_log,
    delete_hypertrophy_log
)
from db.session import get_db
from api.services import get_current_verified_user

hypertrophy_router = APIRouter(prefix="/hypertrophy", tags=["hypertrophy"])

@hypertrophy_router.post("/", response_model=HypertrophyLogBase)
async def create_hypertrophy_exercise(
    log_data: HypertrophyLogCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Create a new hypertrophy exercise log."""
    return await create_hypertrophy_log(db, log_data, current_user.id)

@hypertrophy_router.get("/{log_id}", response_model=HypertrophyLogBase)
async def get_hypertrophy_exercise(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get a specific hypertrophy exercise log by ID."""
    log = await get_hypertrophy_log(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hypertrophy log not found"
        )
    if getattr(log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hypertrophy log not found"
        )
    return log

@hypertrophy_router.get("/", response_model=List[HypertrophyLogBase])
async def get_user_hypertrophy_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all hypertrophy exercise logs for the current user."""
    return await get_user_hypertrophy_logs(db, current_user.id, skip, limit)

@hypertrophy_router.get("/workout/{workout_id}", response_model=List[HypertrophyLogBase])
async def get_workout_hypertrophy_exercises(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get all hypertrophy exercises for a specific workout."""
    return await get_workout_hypertrophy_logs(db, workout_id)

@hypertrophy_router.put("/{log_id}", response_model=HypertrophyLogBase)
async def update_hypertrophy_exercise(
    log_id: int,
    log_update: HypertrophyLogUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update a hypertrophy exercise log."""
    existing_log = await get_hypertrophy_log(db, log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hypertrophy log not found"
        )
    if getattr(existing_log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hypertrophy log not found"
        )
    
    updated_log = await update_hypertrophy_log(db, log_id, log_update)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update hypertrophy log"
        )
    
    return updated_log

@hypertrophy_router.delete("/{log_id}")
async def delete_hypertrophy_exercise(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Delete a hypertrophy exercise log."""
    existing_log = await get_hypertrophy_log(db, log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hypertrophy log not found"
        )
    if getattr(existing_log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hypertrophy log not found"
        )
    
    success = await delete_hypertrophy_log(db, log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete hypertrophy log"
        )
    
    return {"message": "Hypertrophy log deleted successfully"}

