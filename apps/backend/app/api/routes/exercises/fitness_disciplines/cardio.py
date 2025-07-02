"""
Cardio exercise routes for interval training and cardiovascular fitness.
Handles CRUD operations and specific analytics for cardio training.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Dict, Any, Annotated, Optional
from datetime import datetime, timedelta

from db.schemas.user import User
from db.schemas.discipline_exercise_logs.cardio import (
    CardioLogCreate, 
    CardioLogUpdate, 
    CardioLogBase
)
from db.models.discipline_exercise_logs.cardio import CardioLog
from db.crud.discipline_exercise_logs.cardio import (
    create_cardio_log,
    get_cardio_log,
    get_user_cardio_logs,
    get_workout_cardio_logs,
    update_cardio_log,
    delete_cardio_log
)
from db.session import get_db
from api.services import get_current_verified_user

cardio_router = APIRouter(prefix="/cardio", tags=["cardio"])

@cardio_router.post("/", response_model=CardioLogBase)
async def create_cardio_exercise(
    log_data: CardioLogCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Create a new cardio exercise log."""
    return await create_cardio_log(db, log_data, current_user.id)

@cardio_router.get("/{log_id}", response_model=CardioLogBase)
async def get_cardio_exercise(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get a specific cardio exercise log by ID."""
    log = await get_cardio_log(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio log not found"
        )
    if getattr(log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio log not found"
        )
    return log

@cardio_router.get("/", response_model=List[CardioLogBase])
async def get_user_cardio_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """Get all cardio exercise logs for the current user."""
    return await get_user_cardio_logs(db, current_user.id, skip, limit)

@cardio_router.get("/workout/{workout_id}", response_model=List[CardioLogBase])
async def get_workout_cardio_exercises(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get all cardio exercises for a specific workout."""
    return await get_workout_cardio_logs(db, workout_id)

@cardio_router.put("/{log_id}", response_model=CardioLogBase)
async def update_cardio_exercise(
    log_id: int,
    log_update: CardioLogUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update a cardio exercise log."""
    existing_log = await get_cardio_log(db, log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio log not found"
        )
    if getattr(existing_log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio log not found"
        )
    
    updated_log = await update_cardio_log(db, log_id, log_update)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update cardio log"
        )
    
    return updated_log

@cardio_router.delete("/{log_id}")
async def delete_cardio_exercise(
    log_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Delete a cardio exercise log."""
    existing_log = await get_cardio_log(db, log_id)
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio log not found"
        )
    if getattr(existing_log, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cardio log not found"
        )
    
    success = await delete_cardio_log(db, log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete cardio log"
        )
    
    return {"message": "Cardio log deleted successfully"}