"""
General exercise routes that are not tied to specific fitness disciplines.
These routes provide general exercise functionality like search, stats, and recent exercises.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, select, union_all
from typing import List, Dict, Any, Annotated, Optional, Union
from datetime import datetime, timedelta

from db.schemas.user import User
from db.schemas.discipline_exercise_logs import (
    HypertrophyLog, MaxStrengthLog,
    FlexibilityLog, CardioLog
)
from db.models.discipline_exercise_logs import (
    HypertrophyLog as HypertrophyLogModel,
    MaxStrengthLog as MaxStrengthLogModel,
    FlexibilityLog as FlexibilityLogModel,
    CardioLog as CardioLogModel,
    WeightUnit
)
from db.models.workout import Workout as WorkoutModel
from db.session import get_db
from api.services import get_current_verified_user

# Union type for all exercise log schemas
ExerciseLogUnion = Union[
    HypertrophyLog, MaxStrengthLog,         
    FlexibilityLog, CardioLog
]

# All discipline models for querying
ALL_DISCIPLINE_MODELS = [
    HypertrophyLogModel, MaxStrengthLogModel, FlexibilityLogModel, CardioLogModel
]

general_exercises_router = APIRouter(tags=["general-exercises"])

@general_exercises_router.get("/recent", response_model=List[Dict[str, Any]])
async def get_recent_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get the user's most recent exercises across all workouts and disciplines.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        limit: Maximum number of exercises to return
        
    Returns:
        List[Dict[str, Any]]: List of recent exercise logs with discipline info
    """
    # Create union query for all discipline tables
    queries = []
    for model in ALL_DISCIPLINE_MODELS:
        # Get common fields that exist in all models
        query = select(
            model.exercise_name,
            model.exercise_date,
            model.workout_id,
            func.literal(model.__tablename__).label('discipline')
        ).where(model.user_id == current_user.id)
        queries.append(query)
    
    # Union all queries and order by date
    union_query = union_all(*queries).order_by(desc('exercise_date')).limit(limit)
    result = await db.execute(union_query)
    
    exercises = []
    for row in result.fetchall():
        exercises.append({
            "exercise_name": row.exercise_name,
            "exercise_date": row.exercise_date.isoformat(),
            "workout_id": row.workout_id,
            "discipline": row.discipline
        })
    
    return exercises

@general_exercises_router.get("/popular", response_model=List[Dict[str, Any]])
async def get_popular_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50)
):
    """
    Get the user's most frequently performed exercises across all disciplines.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        limit: Maximum number of exercises to return
        
    Returns:
        List[Dict]: List of exercise names and their counts
    """
    # Create union query for all discipline tables to count exercises
    queries = []
    for model in ALL_DISCIPLINE_MODELS:
        query = select(
            model.exercise_name
        ).where(
            model.user_id == current_user.id,
            model.exercise_name != None
        )
        queries.append(query)
    
    # Union all queries and count by exercise name
    union_query = union_all(*queries).alias('all_exercises')
    count_query = select(
        union_query.c.exercise_name,
        func.count().label("count")
    ).group_by(
        union_query.c.exercise_name
    ).order_by(desc("count")).limit(limit)
    
    result = await db.execute(count_query)
    
    return [{"name": name, "count": count} for name, count in result.all()]

@general_exercises_router.get("/stats", response_model=Dict[str, Any])
async def get_exercise_stats(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(30, ge=1, le=365)
):
    """
    Get exercise statistics for the current user across all disciplines.
    
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
    
    # Count total exercises across all disciplines
    total_exercises = 0
    for model in ALL_DISCIPLINE_MODELS:
        exercise_count_result = await db.execute(
            select(func.count(model.id))
            .where(
                model.user_id == current_user.id,
                model.exercise_date >= start_date
            )
        )
        total_exercises += exercise_count_result.scalar_one()
    
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

@general_exercises_router.get("/search", response_model=List[Dict[str, Any]])
async def search_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Search for exercises by name across all disciplines.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of matching exercise logs with discipline info
    """
    # Create union query for all discipline tables
    queries = []
    for model in ALL_DISCIPLINE_MODELS:
        model_query = select(
            model.exercise_name,
            model.exercise_date,
            model.workout_id,
            func.literal(model.__tablename__).label('discipline')
        ).where(
            model.user_id == current_user.id,
            model.exercise_name.ilike(f"%{query}%")
        )
        queries.append(model_query)
    
    # Union all queries and order by date
    union_query = union_all(*queries).order_by(desc('exercise_date')).limit(limit)
    result = await db.execute(union_query)
    
    exercises = []
    for row in result.fetchall():
        exercises.append({
            "exercise_name": row.exercise_name,
            "exercise_date": row.exercise_date.isoformat(),
            "workout_id": row.workout_id,
            "discipline": row.discipline
        })
    
    return exercises

@general_exercises_router.get("/progress/{exercise_name}", response_model=List[Dict[str, Any]])
async def get_exercise_progress(
    exercise_name: str,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(90, ge=1, le=365)
):
    """
    Get progress data for a specific exercise over time across all disciplines.
    
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
    
    progress_data = []
    
    # Search across all discipline models
    for model in ALL_DISCIPLINE_MODELS:
        result = await db.execute(
            select(model)
            .where(
                model.user_id == current_user.id,
                model.exercise_name.ilike(f"%{exercise_name}%"),
                model.exercise_date >= start_date
            )
            .order_by(model.exercise_date)
        )
        
        logs = result.scalars().all()
        
        # Format the response based on available fields
        for log in logs:
            log_data = {
                "date": log.exercise_date.isoformat(),
                "discipline": model.__tablename__
            }
            
            # Add common fields if they exist
            if hasattr(log, 'completed_reps'):
                log_data["reps"] = log.completed_reps
            elif hasattr(log, 'reps'):
                log_data["reps"] = log.reps
                
            if hasattr(log, 'weight'):
                log_data["weight"] = log.weight
                log_data["weight_unit"] = log.weight_unit.value if log.weight_unit else None
                
            if hasattr(log, 'rir'):
                log_data["rir"] = log.rir
                
            if hasattr(log, 'set_number'):
                log_data["set_number"] = log.set_number
                
            if hasattr(log, 'distance'):
                log_data["distance"] = log.distance
                log_data["distance_unit"] = log.distance_unit.value if hasattr(log, 'distance_unit') and log.distance_unit else None
                
            if hasattr(log, 'duration_seconds'):
                log_data["duration_seconds"] = log.duration_seconds
            
            progress_data.append(log_data)
    
    # Sort by date
    progress_data.sort(key=lambda x: x["date"])
    
    return progress_data

@general_exercises_router.get("/catalog", response_model=Dict[str, List[str]])
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
    catalog = {}
    
    # Get exercises from all discipline models
    for model in ALL_DISCIPLINE_MODELS:
        result = await db.execute(
            select(
                model.exercise_name,
                WorkoutModel.muscle_group
            )
            .join(
                WorkoutModel,
                model.workout_id == WorkoutModel.id
            )
            .where(
                model.user_id == current_user.id,
                model.exercise_name != None
            )
            .group_by(model.exercise_name, WorkoutModel.muscle_group)
        )
        
        # Organize by muscle group
        for exercise_name, muscle_group in result.all():
            if not exercise_name:
                continue
                
            group_key = str(muscle_group.value) if muscle_group else "unknown"
            
            if group_key not in catalog:
                catalog[group_key] = []
                
            if exercise_name not in catalog[group_key]:
                catalog[group_key].append(exercise_name)
    
    return catalog 