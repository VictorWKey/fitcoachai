"""
Routes for standard exercise catalog and utilities that support training programs.
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
from db.schemas.standard_exercises import StandardExercise as StandardExerciseSchema
from db.models.strength_log import StrengthLog as StrengthLogModel
from db.models.cardio_log import CardioLog as CardioLogModel
from db.models.standard_exercises import StandardExercise, MuscleGroupEnum, EquipmentEnum, StandardExerciseType
from db.crud.standard_exercises import get_standard_exercises, get_standard_exercises_by_equipment_and_muscle_group
from db.session import get_db
from api.services.auth import get_current_verified_user

standard_exercises_router = APIRouter(prefix="/standard-exercises", tags=["standard-exercises"])

@standard_exercises_router.get("/catalog", response_model=List[StandardExerciseSchema])
async def get_standard_exercises_with_ids(
    # current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    equipment: Optional[str] = Query(None, description="Filter by equipment type"),
    muscle_group: Optional[str] = Query(None, description="Filter by muscle group"),
    exercise_type: Optional[str] = Query(None, description="Filter by exercise type"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of exercises to return")
):
    """
    Get standard exercises with their real IDs.
    
    This endpoint returns standardized exercises from the database with their IDs,
    allowing the frontend to work with real exercise entities instead of free text.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        equipment: Filter by equipment (barra, mancuernas, maquina, poleas, peso_corporal, discos)
        muscle_group: Filter by muscle group (pectoral, espalda, biceps, etc.)
        exercise_type: Filter by exercise type (compuesto, aislado)
        limit: Maximum number of exercises to return
        
    Returns:
        List[StandardExerciseSchema]: List of standard exercises with IDs
    """
    # Validate enum values if provided
    if equipment and equipment not in [e.value for e in EquipmentEnum]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid equipment type: {equipment}"
        )
    
    if muscle_group and muscle_group not in [m.value for m in MuscleGroupEnum]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid muscle group: {muscle_group}"
        )
    
    if exercise_type and exercise_type not in [t.value for t in StandardExerciseType]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid exercise type: {exercise_type}"
        )
    
    # Get filtered exercises
    if equipment or muscle_group:
        exercises = await get_standard_exercises_by_equipment_and_muscle_group(
            db, equipment, muscle_group
        )
        
        # Apply exercise type filter if provided
        if exercise_type:
            exercises = [e for e in exercises if e.type.value == exercise_type]
        
        # Apply limit
        exercises = exercises[:limit]
    else:
        exercises = await get_standard_exercises(db, limit=limit)
        
        # Apply exercise type filter if provided
        if exercise_type:
            exercises = [e for e in exercises if e.type.value == exercise_type]
    
    return exercises

@standard_exercises_router.get("/autocomplete", response_model=List[str])
async def autocomplete_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    query: str = Query(..., min_length=2, max_length=50, description="Search query for exercise names"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions to return")
):
    """
    Autocomplete exercise names for search functionality.
    
    This endpoint provides autocomplete suggestions for exercise names,
    useful for implementing search bars and exercise selection interfaces.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        query: Search query string (minimum 2 characters)
        limit: Maximum number of suggestions to return
        
    Returns:
        List[str]: List of exercise names that match the query
    """
    # Search in standard exercises
    exercises = await db.execute(
        select(StandardExercise.standard_name)
        .where(StandardExercise.standard_name.ilike(f"%{query}%"))
        .order_by(StandardExercise.standard_name)
        .limit(limit)
    )
    
    exercise_names = [name for name in exercises.scalars().all()]
    return exercise_names

@standard_exercises_router.get("/search", response_model=List[Dict[str, Any]])
async def search_exercises(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results to return")
):
    """
    Search for exercises by name.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        query: Search query string
        limit: Maximum number of results to return
        
    Returns:
        List[Dict[str, Any]]: List of matching exercises with usage stats
    """
    # Search all standard exercises first (regardless of usage)
    standard_exercises = await db.execute(
        select(
            StandardExercise.id,
            StandardExercise.standard_name,
            StandardExercise.main_muscle_group,
            StandardExercise.equipment,
            StandardExercise.type
        )
        .where(StandardExercise.standard_name.ilike(f"%{query}%"))
        .order_by(StandardExercise.standard_name)
        .limit(limit)
    )
    
    # Get usage counts for exercises that have been used by this user
    usage_counts = await db.execute(
        select(
            StandardExercise.id,
            func.count(StrengthLogModel.id).label("usage_count")
        )
        .join(StrengthLogModel, StrengthLogModel.standard_exercise_id == StandardExercise.id, isouter=True)
        .where(
            StandardExercise.standard_name.ilike(f"%{query}%"),
            StrengthLogModel.user_id == current_user.id
        )
        .group_by(StandardExercise.id)
    )
    
    # Create a dict for quick lookup of usage counts
    usage_dict = {exercise_id: count for exercise_id, count in usage_counts.all()}
    
    # Build results with all matching exercises
    search_results = []
    
    for exercise_id, exercise_name, muscle_group, equipment, exercise_type in standard_exercises.all():
        usage_count = usage_dict.get(exercise_id, 0)
        search_results.append({
            "exercise_id": exercise_id,
            "exercise_name": exercise_name,
            "type": "strength",
            "muscle_group": muscle_group.value if muscle_group else None,
            "equipment": equipment.value if equipment else None,
            "exercise_type": exercise_type.value if exercise_type else None,
            "usage_count": usage_count
        })
    
    # Search cardio exercises from logs (these are free-form names)
    cardio_exercises = await db.execute(
        select(
            CardioLogModel.exercise_name,
            func.count(CardioLogModel.id).label("usage_count")
        )
        .where(
            CardioLogModel.user_id == current_user.id,
            CardioLogModel.exercise_name.ilike(f"%{query}%")
        )
        .group_by(CardioLogModel.exercise_name)
        .order_by(desc("usage_count"))
        .limit(limit // 2)  # Limit cardio results to half of total limit
    )
    
    # Add cardio results
    for exercise_name, usage_count in cardio_exercises.all():
        search_results.append({
            "exercise_id": None,
            "exercise_name": exercise_name,
            "type": "cardio",
            "muscle_group": None,
            "equipment": None,
            "exercise_type": None,
            "usage_count": usage_count
        })
    
    # Sort by usage count (desc) then by name (asc)
    search_results.sort(key=lambda x: (-x["usage_count"], x["exercise_name"]))
    return search_results

@standard_exercises_router.get("/equipment-types", response_model=List[Dict[str, str]])
async def get_equipment_types(
    current_user: Annotated[User, Depends(get_current_verified_user)]
):
    """
    Get all valid equipment types for exercises.
    
    Returns:
        List[Dict[str, str]]: List of equipment types with value and label
    """
    equipment_types = []
    for equipment in EquipmentEnum:
        equipment_types.append({
            "value": equipment.value,
            "label": equipment.value.replace("_", " ").title()
        })
    return equipment_types

@standard_exercises_router.get("/muscle-groups", response_model=List[Dict[str, str]])
async def get_muscle_groups(
    current_user: Annotated[User, Depends(get_current_verified_user)]
):
    """
    Get all valid muscle groups for exercises.
    
    Returns:
        List[Dict[str, str]]: List of muscle groups with value and label
    """
    muscle_groups = []
    for muscle_group in MuscleGroupEnum:
        muscle_groups.append({
            "value": muscle_group.value,
            "label": muscle_group.value.replace("_", " ").title()
        })
    return muscle_groups

@standard_exercises_router.get("/exercise-types", response_model=List[Dict[str, str]])
async def get_exercise_types(
    current_user: Annotated[User, Depends(get_current_verified_user)]
):
    """
    Get all valid exercise types.
    
    Returns:
        List[Dict[str, str]]: List of exercise types with value and label
    """
    exercise_types = []
    for ex_type in StandardExerciseType:
        exercise_types.append({
            "value": ex_type.value,
            "label": ex_type.value.title()
        })
    return exercise_types

@standard_exercises_router.get("/progress/{exercise_name}", response_model=List[Dict[str, Any]])
async def get_exercise_progress(
    exercise_name: str,
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(90, ge=1, le=365)
):
    """
    Get progress history for a specific exercise.
    
    Args:
        exercise_name: Name of the exercise to track
        current_user: Authenticated and verified user
        db: Database session
        days: Number of days to look back
        
    Returns:
        List[Dict[str, Any]]: Progress history
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Get strength exercise progress
    strength_logs = await db.execute(
        select(
            StrengthLogModel.exercise_date,
            StrengthLogModel.repetitions_done,
            StrengthLogModel.used_weight,
            StrengthLogModel.used_weight_unit,
            StrengthLogModel.perceived_rir,
            StrengthLogModel.perceived_rpe,
            StrengthLogModel.set_number,
            StandardExercise.standard_name
        )
        .join(StandardExercise, StrengthLogModel.standard_exercise_id == StandardExercise.id)
        .where(
            StrengthLogModel.user_id == current_user.id,
            StandardExercise.standard_name.ilike(f"%{exercise_name}%"),
            StrengthLogModel.exercise_date >= start_date,
            StrengthLogModel.exercise_date <= end_date
        )
        .order_by(StrengthLogModel.exercise_date)
    )
    
    # Get cardio exercise progress
    cardio_logs = await db.execute(
        select(
            CardioLogModel.exercise_date,
            CardioLogModel.exercise_name,
            CardioLogModel.total_duration_seconds,
            CardioLogModel.distance,
            CardioLogModel.distance_unit,
            CardioLogModel.avg_heart_rate,
            CardioLogModel.calories_burned
        )
        .where(
            CardioLogModel.user_id == current_user.id,
            CardioLogModel.exercise_name.ilike(f"%{exercise_name}%"),
            CardioLogModel.exercise_date >= start_date,
            CardioLogModel.exercise_date <= end_date
        )
        .order_by(CardioLogModel.exercise_date)
    )
    
    progress_data = []
    
    # Add strength exercise data
    for exercise_date, reps, weight, weight_unit, rir, rpe, set_number, exercise_name in strength_logs.all():
        progress_data.append({
            "date": exercise_date.isoformat(),
            "type": "strength",
            "exercise_name": exercise_name,
            "reps": reps,
            "weight": weight,
            "weight_unit": weight_unit.value if weight_unit is not None else None,
            "rir": rir,
            "rpe": rpe,
            "set_number": set_number
        })
    
    # Add cardio exercise data
    for exercise_date, exercise_name, duration, distance, distance_unit, avg_hr, calories in cardio_logs.all():
        progress_data.append({
            "date": exercise_date.isoformat(),
            "type": "cardio",
            "exercise_name": exercise_name,
            "duration": duration,
            "distance": distance,
            "distance_unit": distance_unit.value if distance_unit is not None else None,
            "avg_heart_rate": avg_hr,
            "max_heart_rate": None,  # No disponible en este modelo
            "calories_burned": calories
        })
    
    # Sort by date
    progress_data.sort(key=lambda x: x["date"])
    return progress_data


@standard_exercises_router.get("/personal-records", response_model=List[Dict[str, Any]])
async def get_personal_records(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get personal records for strength exercises (max weight for each exercise).
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        List[Dict[str, Any]]: List of personal records
    """
    # Get max weight for each exercise
    records = await db.execute(
        select(
            StandardExercise.standard_name,
            func.max(StrengthLogModel.used_weight).label("max_weight"),
            StrengthLogModel.used_weight_unit,
            func.max(StrengthLogModel.exercise_date).label("record_date")
        )
        .join(StrengthLogModel, StrengthLogModel.standard_exercise_id == StandardExercise.id)
        .where(
            StrengthLogModel.user_id == current_user.id,
            StandardExercise.standard_name.isnot(None),
            StrengthLogModel.used_weight.isnot(None)
        )
        .group_by(StandardExercise.standard_name, StrengthLogModel.used_weight_unit)
        .order_by(desc("max_weight"))
    )
    
    personal_records = []
    for exercise_name, max_weight, weight_unit, record_date in records.all():
        personal_records.append({
            "exercise_name": exercise_name,
            "max_weight": float(max_weight) if max_weight else 0,
            "weight_unit": weight_unit.value if weight_unit else None,
            "record_date": record_date.isoformat() if record_date else None
        })
    
    return personal_records
