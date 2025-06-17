"""
Routes for exercise-related operations that are not tied to specific workouts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, select
from typing import List, Dict, Any, Annotated, Optional
from datetime import datetime, timedelta

from db.schemas.user import User
from db.schemas.exercise_log import ExerciseLog
from db.models.exercise_log import ExerciseLog as ExerciseLogModel
from db.models.workout import Workout as WorkoutModel
from db.session import get_db
from api.services import get_current_verified_user

exercises_router = APIRouter(prefix="/exercises", tags=["exercises"])

@exercises_router.get("/recent", response_model=List[ExerciseLog])
async def get_recent_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get the user's most recent exercises across all workouts.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        limit: Maximum number of exercises to return
        
    Returns:
        List[ExerciseLog]: List of recent exercise logs
    """
    result = await db.execute(
        select(ExerciseLogModel)
        .where(ExerciseLogModel.user_id == current_user.id)
        .order_by(desc(ExerciseLogModel.exercise_date))
        .limit(limit)
    )
    
    return result.scalars().all()

@exercises_router.get("/popular", response_model=List[Dict[str, Any]])
async def get_popular_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get the user's most frequently performed exercises.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        limit: Maximum number of exercises to return
        
    Returns:
        List[Dict]: List of exercise names and their counts
    """
    result = await db.execute(
        select(
            ExerciseLogModel.exercise_name,
            func.count(ExerciseLogModel.id).label("count")
        )
        .where(
            ExerciseLogModel.user_id == current_user.id,
            ExerciseLogModel.exercise_name != None
        )
        .group_by(ExerciseLogModel.exercise_name)
        .order_by(desc("count"))
        .limit(limit)
    )
    
    return [{"name": name, "count": count} for name, count in result.all()]

@exercises_router.get("/stats", response_model=Dict[str, Any])
async def get_exercise_stats(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(30, ge=1, le=365)
):
    """
    Get exercise statistics for the current user.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        days: Number of days to look back
        
    Returns:
        Dict: Exercise statistics
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Count total exercises
    exercise_count_result = await db.execute(
        select(func.count(ExerciseLogModel.id))
        .where(
            ExerciseLogModel.user_id == current_user.id,
            ExerciseLogModel.exercise_date >= start_date
        )
    )
    total_exercises = exercise_count_result.scalar_one()
    
    # Count total workouts
    workout_count_result = await db.execute(
        select(func.count(WorkoutModel.id))
        .where(
            WorkoutModel.user_id == current_user.id,
            WorkoutModel.start_time >= start_date
        )
    )
    total_workouts = workout_count_result.scalar_one()
    
    # Get most trained muscle groups
    muscle_groups_result = await db.execute(
        select(
            WorkoutModel.muscle_group,
            func.count(WorkoutModel.id).label("count")
        )
        .where(
            WorkoutModel.user_id == current_user.id,
            WorkoutModel.start_time >= start_date,
            WorkoutModel.is_finished == True
        )
        .group_by(WorkoutModel.muscle_group)
        .order_by(desc("count"))
        .limit(5)
    )
    
    muscle_groups = [
        {"muscle_group": str(muscle_group.value), "count": count}
        for muscle_group, count in muscle_groups_result.all()
    ]
    
    # Calculate average exercises per workout
    avg_exercises = total_exercises / total_workouts if total_workouts > 0 else 0
    
    return {
        "total_exercises": total_exercises,
        "total_workouts": total_workouts,
        "avg_exercises_per_workout": round(avg_exercises, 2),
        "top_muscle_groups": muscle_groups,
        "period_days": days
    }

@exercises_router.get("/search", response_model=List[ExerciseLog])
async def search_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search for exercises by name.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List[ExerciseLog]: List of matching exercise logs
    """
    result = await db.execute(
        select(ExerciseLogModel)
        .where(
            ExerciseLogModel.user_id == current_user.id,
            ExerciseLogModel.exercise_name.ilike(f"%{query}%")
        )
        .order_by(desc(ExerciseLogModel.exercise_date))
        .limit(limit)
    )
    
    return result.scalars().all()

@exercises_router.get("/progress/{exercise_name}", response_model=List[Dict[str, Any]])
async def get_exercise_progress(
    exercise_name: str,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(90, ge=1, le=365)
):
    """
    Get progress data for a specific exercise over time.
    
    Args:
        exercise_name: Name of the exercise to track
        current_user: Authenticated and verified user
        db: Database session
        days: Number of days to look back
        
    Returns:
        List[Dict]: List of exercise logs with date and performance metrics
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    result = await db.execute(
        select(ExerciseLogModel)
        .where(
            ExerciseLogModel.user_id == current_user.id,
            ExerciseLogModel.exercise_name.ilike(f"%{exercise_name}%"),
            ExerciseLogModel.exercise_date >= start_date
        )
        .order_by(ExerciseLogModel.exercise_date)
    )
    
    logs = result.scalars().all()
    
    # Format the response
    progress_data = []
    for log in logs:
        progress_data.append({
            "date": log.exercise_date.isoformat(),
            "reps": log.reps,
            "weight": log.weight,
            "weight_unit": log.weight_unit.value if log.weight_unit else None,
            "rir": log.rir,
            "set_number": log.set_number
        })
    
    return progress_data

@exercises_router.get("/catalog", response_model=Dict[str, List[str]])
async def get_exercise_catalog(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get a catalog of all unique exercises performed by the user, 
    categorized by muscle group when possible.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Dict[str, List[str]]: Dictionary of muscle groups and their exercises
    """
    # Get all unique exercise names for this user
    result = await db.execute(
        select(
            ExerciseLogModel.exercise_name,
            WorkoutModel.muscle_group
        )
        .join(
            WorkoutModel,
            ExerciseLogModel.workout_id == WorkoutModel.id
        )
        .where(
            ExerciseLogModel.user_id == current_user.id,
            ExerciseLogModel.exercise_name != None
        )
        .group_by(ExerciseLogModel.exercise_name, WorkoutModel.muscle_group)
    )
    
    # Organize by muscle group
    catalog = {}
    for exercise_name, muscle_group in result.all():
        if not exercise_name:
            continue
            
        group_key = str(muscle_group.value) if muscle_group else "unknown"
        
        if group_key not in catalog:
            catalog[group_key] = []
            
        if exercise_name not in catalog[group_key]:
            catalog[group_key].append(exercise_name)
    
    return catalog
