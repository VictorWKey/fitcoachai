"""
Routes for managing workouts and exercise logs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from datetime import datetime

from db.schemas.user import User
from db.schemas.workout import Workout, WorkoutCreate, WorkoutUpdate
from db.session import get_db
from api.services import get_current_verified_user
from db.crud.workout import (
    get_workout, get_user_workouts, get_active_workout, 
    create_workout, update_workout, delete_workout, finalize_workout
)
from core.services.exercise_log import CoreExerciseLogService

workouts_router = APIRouter(prefix="/workouts", tags=["workouts"])

# Workout endpoints
@workouts_router.get("/", response_model=List[Workout])
async def list_workouts(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get all workouts for the current user.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List[Workout]: List of workouts
    """
    workouts = await get_user_workouts(db, current_user.id)
    return workouts[skip:skip+limit]

@workouts_router.get("/active", response_model=Optional[Workout])
async def get_current_workout(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get the user's active (most recent unfinished) workout.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Workout: Active workout or null if not found
    """
    return await get_active_workout(db, current_user.id)

@workouts_router.get("/{workout_id}", response_model=Workout)
async def get_workout_by_id(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get a specific workout by ID.
    
    Args:
        workout_id: ID of the workout to retrieve
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Workout: The requested workout
    """
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    # Verify that the workout belongs to the current user
    if getattr(workout, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this workout"
        )
    
    return workout

@workouts_router.post("/", response_model=Workout, status_code=status.HTTP_201_CREATED)
async def create_new_workout(
    workout_data: WorkoutCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new workout.
    
    Args:
        workout_data: Workout data to create
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Workout: The created workout
    """
    # Ensure the workout is assigned to the current user
    workout_data.user_id = current_user.id
    
    # Set start_time to now if not provided
    if not workout_data.start_time:
        workout_data.start_time = datetime.now()
    
    return await create_workout(db, workout_data)

@workouts_router.put("/{workout_id}", response_model=Workout)
async def update_workout_by_id(
    workout_id: int,
    workout_data: WorkoutUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update a workout.
    
    Args:
        workout_id: ID of the workout to update
        workout_data: Updated workout data
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Workout: The updated workout
    """
    # Verify that the workout exists and belongs to the user
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if getattr(workout, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this workout"
        )
    
    updated_workout = await update_workout(db, workout_id, workout_data)
    return updated_workout

@workouts_router.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout_by_id(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete a workout.
    
    Args:
        workout_id: ID of the workout to delete
        current_user: Authenticated and verified user
        db: Database session
    """
    # Verify that the workout exists and belongs to the user
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if getattr(workout, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this workout"
        )
    
    success = await delete_workout(db, workout_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete workout"
        )

@workouts_router.post("/{workout_id}/finish", response_model=Workout)
async def finish_workout_by_id(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    request: Request
):
    """
    Finish a workout and infer its type.
    
    Args:
        workout_id: ID of the workout to finish
        current_user: Authenticated and verified user
        db: Database session
        request: FastAPI request with app state
        
    Returns:
        Workout: The updated workout
    """
    # Verify that the workout exists and belongs to the user
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if getattr(workout, 'user_id') != getattr(current_user, 'id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to finish this workout"
        )
    
    # Get LLM from app state if available
    llm = getattr(request.app.state, "llm", None)
    
    # Finalize the workout
    finished_workout = await finalize_workout(db, workout_id, llm)
    if not finished_workout:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to finish workout"
        )
    
    return finished_workout

# Exercise log endpoints
@workouts_router.get("/{workout_id}/exercises")
async def list_workout_exercises(
    workout_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get all exercise logs for a specific workout.
    
    Args:
        workout_id: ID of the workout
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        List[Dict]: List of exercise logs with all discipline-specific fields
    """
    try:
        logs_dicts = await CoreExerciseLogService.get_exercise_logs_as_dicts(
            db, workout_id, current_user.id
        )
        return logs_dicts  # Return raw dictionaries with all fields
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "not authorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercise logs"
        )

# Note: This endpoint is disabled until we implement discipline-specific creation
# @workouts_router.post("/{workout_id}/exercises", response_model=BaseExerciseLogResponse, status_code=status.HTTP_201_CREATED)
# async def create_exercise_for_workout(
#     workout_id: int,
#     exercise_data: Any,  # Will need to be discipline-specific
#     current_user: Annotated[User, Depends(get_current_verified_user)],
#     db: Annotated[AsyncSession, Depends(get_db)]
# ):
#     """
#     Add a new exercise log to a workout.
#     Note: This endpoint needs to be discipline-specific.
#     Use the individual discipline endpoints in /api/routes/exercises/ instead.
#     """
#     pass

@workouts_router.get("/{workout_id}/exercises/{exercise_id}")
async def get_exercise_by_id(
    workout_id: int,
    exercise_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get a specific exercise log by ID.
    
    Args:
        workout_id: ID of the workout
        exercise_id: ID of the exercise log
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Exercise log of the appropriate discipline
    """
    try:
        exercise_log = await CoreExerciseLogService.get_exercise_log_by_workout(
            db, exercise_id, workout_id, current_user.id
        )
        if not exercise_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exercise log not found"
            )
        return exercise_log
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "not authorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve exercise log"
        )

# Note: Update and Delete endpoints are temporarily disabled until we implement discipline-specific updates
# These endpoints need to handle different schemas for each discipline

# @workouts_router.put("/{workout_id}/exercises/{exercise_id}")
# async def update_exercise_by_id(
#     workout_id: int,
#     exercise_id: int,
#     exercise_data: Any,  # Will need to be discipline-specific
#     current_user: Annotated[User, Depends(get_current_verified_user)],
#     db: Annotated[AsyncSession, Depends(get_db)]
# ):
#     """
#     Update a specific exercise log.
#     Note: This endpoint needs to be discipline-specific.
#     Use the individual discipline endpoints in /api/routes/exercises/ instead.
#     """
#     try:
#         updated_log = await CoreExerciseLogService.update_exercise_log_by_workout(
#             db, exercise_id, workout_id, exercise_data, current_user.id
#         )
#         return updated_log
#     except Exception as e:
#         # Handle exceptions appropriately
#         pass

@workouts_router.delete("/{workout_id}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise_by_id(
    workout_id: int,
    exercise_id: int,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete a specific exercise log.
    
    Args:
        workout_id: ID of the workout
        exercise_id: ID of the exercise log to delete
        current_user: Authenticated and verified user
        db: Database session
    """
    try:
        success = await CoreExerciseLogService.delete_exercise_log_by_workout(
            db, exercise_id, workout_id, current_user.id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete exercise log"
            )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "not authorized" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete exercise log"
        )
