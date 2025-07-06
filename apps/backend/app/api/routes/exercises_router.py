"""
Routes for exercise-related operations that are not tied to specific workouts.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, select
from typing import List, Dict, Any, Annotated, Optional
from datetime import datetime, timedelta

from db.schemas.user import User
from db.schemas.strength_log import StrengthLog
from db.schemas.cardio_log import CardioLog
from db.schemas.exercise_log import ExerciseLog, convert_to_exercise_log
from db.models.strength_log import StrengthLog as StrengthLogModel
from db.models.cardio_log import CardioLog as CardioLogModel
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
        List[ExerciseLog]: List of recent exercise logs (both strength and cardio)
    """
    # Get recent strength exercises
    strength_result = await db.execute(
        select(StrengthLogModel)
        .where(StrengthLogModel.user_id == current_user.id)
        .order_by(desc(StrengthLogModel.exercise_date))
        .limit(limit)
    )
    strength_logs = list(strength_result.scalars().all())
    
    # Get recent cardio exercises  
    cardio_result = await db.execute(
        select(CardioLogModel)
        .where(CardioLogModel.user_id == current_user.id)
        .order_by(desc(CardioLogModel.exercise_date))
        .limit(limit)
    )
    cardio_logs = list(cardio_result.scalars().all())
    
    # Combine and convert to schema objects
    all_logs = strength_logs + cardio_logs
    exercise_logs = [convert_to_exercise_log(log) for log in all_logs]
    
    # Sort by exercise_date (most recent first) and limit
    exercise_logs.sort(key=lambda x: x.exercise_date, reverse=True)
    return exercise_logs[:limit]

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
    # Get strength exercise counts
    strength_result = await db.execute(
        select(
            StrengthLogModel.exercise_name,
            func.count(StrengthLogModel.id).label("count")
        )
        .where(
            StrengthLogModel.user_id == current_user.id,
            StrengthLogModel.exercise_name != None
        )
        .group_by(StrengthLogModel.exercise_name)
    )
    
    # Get cardio exercise counts
    cardio_result = await db.execute(
        select(
            CardioLogModel.exercise_name,
            func.count(CardioLogModel.id).label("count")
        )
        .where(
            CardioLogModel.user_id == current_user.id,
            CardioLogModel.exercise_name != None
        )
        .group_by(CardioLogModel.exercise_name)
    )
    
    # Combine results and aggregate by exercise name
    exercise_counts = {}
    
    for name, count in strength_result.all():
        if name:
            exercise_counts[name] = exercise_counts.get(name, 0) + count
    
    for name, count in cardio_result.all():
        if name:
            exercise_counts[name] = exercise_counts.get(name, 0) + count
    
    # Sort by count and limit
    sorted_exercises = sorted(exercise_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"name": name, "count": count} for name, count in sorted_exercises[:limit]]

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
    
    # Count total strength exercises
    strength_count_result = await db.execute(
        select(func.count(StrengthLogModel.id))
        .where(
            StrengthLogModel.user_id == current_user.id,
            StrengthLogModel.exercise_date >= start_date
        )
    )
    total_strength_exercises = strength_count_result.scalar_one()
    
    # Count total cardio exercises
    cardio_count_result = await db.execute(
        select(func.count(CardioLogModel.id))
        .where(
            CardioLogModel.user_id == current_user.id,
            CardioLogModel.exercise_date >= start_date
        )
    )
    total_cardio_exercises = cardio_count_result.scalar_one()
    
    total_exercises = total_strength_exercises + total_cardio_exercises
    
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
        "total_strength_exercises": total_strength_exercises,
        "total_cardio_exercises": total_cardio_exercises,
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
    # Search strength exercises
    strength_result = await db.execute(
        select(StrengthLogModel)
        .where(
            StrengthLogModel.user_id == current_user.id,
            StrengthLogModel.exercise_name.ilike(f"%{query}%")
        )
        .order_by(desc(StrengthLogModel.exercise_date))
        .limit(limit)
    )
    strength_logs = list(strength_result.scalars().all())
    
    # Search cardio exercises
    cardio_result = await db.execute(
        select(CardioLogModel)
        .where(
            CardioLogModel.user_id == current_user.id,
            CardioLogModel.exercise_name.ilike(f"%{query}%")
        )
        .order_by(desc(CardioLogModel.exercise_date))
        .limit(limit)
    )
    cardio_logs = list(cardio_result.scalars().all())
    
    # Combine and convert to schema objects
    all_logs = strength_logs + cardio_logs
    exercise_logs = [convert_to_exercise_log(log) for log in all_logs]
    
    # Sort by exercise_date (most recent first) and limit
    exercise_logs.sort(key=lambda x: x.exercise_date, reverse=True)
    return exercise_logs[:limit]

@exercises_router.get("/progress/{exercise_name}", response_model=List[Dict[str, Any]])
async def get_exercise_progress(
    exercise_name: str,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(90, ge=1, le=365)
):
    """
    Get progress data for a specific exercise over time (both strength and cardio).
    
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
    
    # Get strength logs
    strength_result = await db.execute(
        select(StrengthLogModel)
        .where(
            StrengthLogModel.user_id == current_user.id,
            StrengthLogModel.exercise_name.ilike(f"%{exercise_name}%"),
            StrengthLogModel.exercise_date >= start_date
        )
        .order_by(StrengthLogModel.exercise_date)
    )
    strength_logs = strength_result.scalars().all()
    
    # Get cardio logs
    cardio_result = await db.execute(
        select(CardioLogModel)
        .where(
            CardioLogModel.user_id == current_user.id,
            CardioLogModel.exercise_name.ilike(f"%{exercise_name}%"),
            CardioLogModel.exercise_date >= start_date
        )
        .order_by(CardioLogModel.exercise_date)
    )
    cardio_logs = cardio_result.scalars().all()
    
    # Format the response
    progress_data = []
    
    # Add strength exercise data
    for log in strength_logs:
        progress_data.append({
            "date": log.exercise_date.isoformat(),
            "type": "strength",
            "exercise_name": log.exercise_name,
            "reps": log.reps,
            "weight": log.weight,
            "weight_unit": log.weight_unit.value if log.weight_unit is not None else None,
            "rir": log.rir,
            "rpe": log.rpe,
            "set_number": log.set_number
        })
    
    # Add cardio exercise data
    for log in cardio_logs:
        progress_data.append({
            "date": log.exercise_date.isoformat(),
            "type": "cardio",
            "exercise_name": log.exercise_name,
            "cardio_type": log.cardio_type.value if log.cardio_type is not None else None,
            "duration_minutes": log.total_duration_seconds // 60 if log.total_duration_seconds is not None else None,
            "distance_km": log.distance_km,
            "average_speed_kmh": log.average_speed_kmh,
            "avg_heart_rate": log.avg_heart_rate,
            "calories_burned": log.calories_burned,
            "avg_rpe": log.avg_rpe
        })
    
    # Sort by date
    progress_data.sort(key=lambda x: x["date"])
    
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
    # Get all unique strength exercise names for this user
    strength_result = await db.execute(
        select(
            StrengthLogModel.exercise_name,
            WorkoutModel.muscle_group
        )
        .join(
            WorkoutModel,
            StrengthLogModel.workout_id == WorkoutModel.id
        )
        .where(
            StrengthLogModel.user_id == current_user.id,
            StrengthLogModel.exercise_name != None
        )
        .group_by(StrengthLogModel.exercise_name, WorkoutModel.muscle_group)
    )
    
    # Get all unique cardio exercise names for this user
    cardio_result = await db.execute(
        select(
            CardioLogModel.exercise_name,
            WorkoutModel.muscle_group
        )
        .join(
            WorkoutModel,
            CardioLogModel.workout_id == WorkoutModel.id
        )
        .where(
            CardioLogModel.user_id == current_user.id,
            CardioLogModel.exercise_name != None
        )
        .group_by(CardioLogModel.exercise_name, WorkoutModel.muscle_group)
    )
    
    # Organize by muscle group
    catalog = {}
    
    # Add strength exercises
    for exercise_name, muscle_group in strength_result.all():
        if not exercise_name:
            continue
            
        group_key = str(muscle_group.value) if muscle_group else "unknown"
        
        if group_key not in catalog:
            catalog[group_key] = []
            
        if exercise_name not in catalog[group_key]:
            catalog[group_key].append(exercise_name)
    
    # Add cardio exercises
    for exercise_name, muscle_group in cardio_result.all():
        if not exercise_name:
            continue
            
        group_key = str(muscle_group.value) if muscle_group else "unknown"
        
        if group_key not in catalog:
            catalog[group_key] = []
            
        if exercise_name not in catalog[group_key]:
            catalog[group_key].append(exercise_name)
    
    return catalog
