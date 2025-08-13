"""
Service for integrating training programs with workout logging.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, cast, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, update, func
from db.models.training_program import TrainingProgram
from db.models.training_session import TrainingSession
from db.models.programmed_exercise import ProgrammedExercise
from db.models.strength_log import StrengthLog
from db.models.standard_exercises import StandardExercise
from utils.load_utils import calculate_weight_from_load

async def get_active_program_for_user(db: AsyncSession, user_id: int) -> Optional[TrainingProgram]:
    """
    Get the active training program for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        Active training program or None if no active program exists
    """
    result = await db.execute(select(TrainingProgram).filter(
        TrainingProgram.user_id == user_id,
        TrainingProgram.is_active == True
    ))
    return result.scalar_one_or_none()


async def get_or_create_program_workout(
    db: AsyncSession,
    user_id: int,
    exercise_name: str,
    exercise_data: Dict[str, Any]
) -> Tuple[int, Optional[int]]:
    """
    Get or create a workout. Simplified version without program tracking.
    
    Args:
        db: Database session
        user_id: User ID
        exercise_name: Name of the exercise being logged
        exercise_data: Exercise data for analysis
        
    Returns:
        Tuple of (workout_id, None)
    """
    # For now, just create a regular workout without program integration
    return await _create_regular_workout(db, user_id), None


async def detect_session_mismatch(
    db: AsyncSession,
    user_id: int,
    exercise_name: str
) -> Optional[Dict[str, Any]]:
    """
    Detect if an exercise doesn't match the current session. Simplified version.
    
    Args:
        db: Database session
        user_id: User ID
        exercise_name: Name of the exercise being logged
        
    Returns:
        None (mismatch detection disabled for now)
    """
    # For now, disable mismatch detection
    return None


async def find_matching_programmed_exercise(
    db: AsyncSession,
    session_id: int,
    exercise_name: str
) -> Optional[ProgrammedExercise]:
    """
    Find a programmed exercise that matches the exercise being logged.
    
    Args:
        db: Database session
        session_id: Training session ID
        exercise_name: Name of the exercise being logged
        
    Returns:
        Matching programmed exercise or None if no match found
    """
    from sqlalchemy.orm import selectinload
    
    # Get all programmed exercises for this session with their standard exercises
    result = await db.execute(
        select(ProgrammedExercise)
        .options(selectinload(ProgrammedExercise.standard_exercise))
        .where(ProgrammedExercise.session_id == session_id)
        .order_by(ProgrammedExercise.block, ProgrammedExercise.id)
    )
    programmed_exercises = list(result.scalars().all())
    
    # Try exact match by standard exercise name
    exercise_name_lower = exercise_name.lower()
    for exercise in programmed_exercises:
        if exercise.standard_exercise and exercise.standard_exercise.standard_name:
            standard_name_lower = exercise.standard_exercise.standard_name.lower()
            if standard_name_lower == exercise_name_lower:
                return exercise
    
    # Try partial match
    for exercise in programmed_exercises:
        if exercise.standard_exercise and exercise.standard_exercise.standard_name:
            standard_name_lower = exercise.standard_exercise.standard_name.lower()
            if (exercise_name_lower in standard_name_lower or 
                standard_name_lower in exercise_name_lower):
                return exercise
    
    # Try matching by standard_exercise_id directly
    try:
        # Get standard exercise by name
        standard_result = await db.execute(
            select(StandardExercise)
            .where(StandardExercise.standard_name.ilike(f"%{exercise_name}%"))
            .limit(1)
        )
        standard_exercise = standard_result.scalar_one_or_none()
        
        if standard_exercise:
            for exercise in programmed_exercises:
                if cast(int, exercise.standard_exercise_id) == cast(int, standard_exercise.id):
                    return exercise
    except:
        pass  # Standard exercise matching failed, continue
    
    return None


async def _create_regular_workout(db: AsyncSession, user_id: int) -> int:
    """Create a regular workout not linked to any program."""
    workout = Workout(
        user_id=user_id,
        start_time=datetime.now(),
        is_finished=False
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return cast(int, workout.id)


async def _get_active_program_workout(
    db: AsyncSession,
    user_id: int,
    program_id: int,
    session_id: int
) -> Optional[Workout]:
    """Get active workout for a specific program session."""
    result = await db.execute(
        select(Workout)
        .where(and_(
            Workout.user_id == user_id,
            Workout.program_id == program_id,
            Workout.program_session_id == session_id,
            Workout.is_finished == False
        ))
        .order_by(Workout.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def link_log_to_program_by_id(
    db: AsyncSession,
    log_id: int
) -> bool:
    """
    Try to link a strength log entry to a programmed exercise by log ID.
    
    Args:
        db: Database session
        log_id: ID of the strength log entry to link
        
    Returns:
        True if linked successfully, False otherwise
    """
    # Get the strength log
    result = await db.execute(select(StrengthLog).where(StrengthLog.id == log_id))
    strength_log = result.scalar_one_or_none()
    if not strength_log:
        return False
    
    # Get active program for the user
    # We get the user_id directly from the query to avoid type issues
    result_user = await db.execute(select(StrengthLog.user_id).where(StrengthLog.id == log_id))
    user_id = result_user.scalar_one()
    active_program = await get_active_program_for_user(db, user_id)
    if not active_program:
        return False
    
    # This is a placeholder - you would need to implement the full query logic
    # In a real implementation, you would:
    # 1. Determine which week of the program the user is in
    # 2. Look for programmed exercises in that week that match this exercise
    
    # Placeholder logic - look for any programmed exercise with the same name
    # This is greatly simplified and should be replaced with proper logic
    programmed_exercise = None
    
    if not programmed_exercise:
        return False
    
    # Link strength log to programmed exercise
    strength_log.programmed_exercise_id = programmed_exercise.id
    db.add(strength_log)
    await db.commit()
    
    return True

async def get_program_recommendations(
    db: AsyncSession,
    user_id: int,
    date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Get recommendations from the active program for today's workout.
    
    Args:
        db: Database session
        user_id: User ID
        date: Date for recommendations (defaults to today)
        
    Returns:
        Dictionary with recommended exercises, sets, reps, etc.
    """
    if date is None:
        date = datetime.now()
    
    # Get active program
    active_program = await get_active_program_for_user(db, user_id)
    if not active_program:
        return {"has_active_program": False}
    
    # In a real implementation, you would:
    # 1. Calculate which week of the program the user is in (based on start date)
    # 2. Find the session for today in that week
    # 3. Return the exercises, sets, reps, etc. for that session
    
    # Placeholder return
    return {
        "has_active_program": True,
        "program_name": active_program.name,
        "today_session": None,  # Placeholder
        "recommended_exercises": []  # Placeholder
    }

async def calculate_performance_metrics(
    db: AsyncSession,
    user_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Calculate performance metrics comparing programmed vs. actual performance.
    
    Args:
        db: Database session
        user_id: User ID
        start_date: Start date for analysis
        end_date: End date for analysis
        
    Returns:
        Dictionary with performance metrics
    """
    # In a real implementation, you would:
    # 1. Find all strength logs with programmed_exercise_id for the date range
    # 2. Compare actual performance (weight, reps) with programmed performance
    # 3. Calculate metrics like adherence, achievement, progression, etc.
    
    # Placeholder return
    return {
        "adherence_percentage": 0,  # Placeholder
        "weight_achievement_percentage": 0,  # Placeholder
        "volume_achievement_percentage": 0,  # Placeholder
        "progression_rate": 0  # Placeholder
    }
