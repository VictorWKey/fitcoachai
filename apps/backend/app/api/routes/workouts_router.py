"""
Routes for managing workouts and exercise logs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Annotated
from datetime import datetime

from db.schemas.user import User
from db.schemas.workout import Workout, WorkoutCreate, WorkoutUpdate
from db.schemas.exercise_log import ExerciseLog, ExerciseLogCreate, ExerciseLogUpdate
from db.session import get_db
from api.services import get_current_verified_user
from db.crud.workout import (
    get_workout, get_user_workouts, get_active_workout, 
    create_workout, update_workout, delete_workout, finalize_workout
)
from db.crud.exercise_log import (
    get_exercise_log, get_workout_logs, create_exercise_log,
    update_exercise_log, delete_exercise_log
)

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
    if workout.user_id != current_user.id:
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
    
    if workout.user_id != current_user.id:
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
    
    if workout.user_id != current_user.id:
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
    
    if workout.user_id != current_user.id:
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
@workouts_router.get("/{workout_id}/exercises", response_model=List[ExerciseLog])
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
        List[ExerciseLog]: List of exercise logs
    """
    # Verify that the workout exists and belongs to the user
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this workout's exercises"
        )
    
    return await get_workout_logs(db, workout_id)

@workouts_router.post("/{workout_id}/exercises", response_model=ExerciseLog, status_code=status.HTTP_201_CREATED)
async def create_exercise_for_workout(
    workout_id: int,
    exercise_data: ExerciseLogCreate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Add a new exercise log to a workout.
    
    Args:
        workout_id: ID of the workout
        exercise_data: Exercise log data to create
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        ExerciseLog: The created exercise log
    """
    # Verify that the workout exists and belongs to the user
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to add exercises to this workout"
        )
    
    # Ensure the exercise log is assigned to the current user and workout
    exercise_data.user_id = current_user.id
    exercise_data.workout_id = workout_id
    
    return await create_exercise_log(db, exercise_data)

@workouts_router.get("/{workout_id}/exercises/{exercise_id}", response_model=ExerciseLog)
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
        ExerciseLog: The requested exercise log
    """
    # Verify that the workout exists and belongs to the user
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this workout's exercises"
        )
    
    # Get the exercise log
    exercise_log = await get_exercise_log(db, exercise_id)
    if not exercise_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise log not found"
        )
    
    # Verify that the exercise log belongs to the specified workout
    if exercise_log.workout_id != workout_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exercise log does not belong to the specified workout"
        )
    
    return exercise_log

@workouts_router.put("/{workout_id}/exercises/{exercise_id}", response_model=ExerciseLog)
async def update_exercise_by_id(
    workout_id: int,
    exercise_id: int,
    exercise_data: ExerciseLogUpdate,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update a specific exercise log.
    
    Args:
        workout_id: ID of the workout
        exercise_id: ID of the exercise log to update
        exercise_data: Updated exercise log data
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        ExerciseLog: The updated exercise log
    """
    # Verify that the workout exists and belongs to the user
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update exercises in this workout"
        )
    
    # Get the exercise log
    exercise_log = await get_exercise_log(db, exercise_id)
    if not exercise_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise log not found"
        )
    
    # Verify that the exercise log belongs to the specified workout
    if exercise_log.workout_id != workout_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exercise log does not belong to the specified workout"
        )
    
    # Update the exercise log
    updated_log = await update_exercise_log(db, exercise_id, exercise_data)
    return updated_log

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
    # Verify that the workout exists and belongs to the user
    workout = await get_workout(db, workout_id)
    if not workout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workout not found"
        )
    
    if workout.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete exercises from this workout"
        )
    
    # Get the exercise log
    exercise_log = await get_exercise_log(db, exercise_id)
    if not exercise_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise log not found"
        )
    
    # Verify that the exercise log belongs to the specified workout
    if exercise_log.workout_id != workout_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exercise log does not belong to the specified workout"
        )
    
    # Delete the exercise log
    success = await delete_exercise_log(db, exercise_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete exercise log"
        )
