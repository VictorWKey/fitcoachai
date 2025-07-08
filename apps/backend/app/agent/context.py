"""
Context management for FitCoach AI agent.

This module handles the retrieval and formatting of user exercise history
to provide context for the AI agent during conversations.
"""

from db.session import db_session
from db.models.strength_log import StrengthLog
from db.models.cardio_log import CardioLog
from db.models.workout import Workout
from db.crud.workout import get_active_workout
from sqlalchemy import select, or_

import json

def to_dict(log):
    """
    Converts a StrengthLog instance into a dictionary with selected fields.

    Args:
        log: An instance of StrengthLog.

    Returns:
        A dictionary representation of the exercise log.
    """
    return {
        "type": "strength",
        "exercise_name": log.exercise_name,
        "weight": log.weight,
        "reps": log.reps,
        "set_number": log.set_number,
        "rir": log.rir,
        "rpe": log.rpe,
        "weight_unit": log.weight_unit.value if log.weight_unit else None,
        "one_rm_percentage": log.one_rm_percentage,
        "tempo": log.tempo,
        "rest_time_seconds": log.rest_time_seconds,
        "notes": log.notes
    }

def cardio_to_dict(log):
    """
    Converts a CardioLog instance into a dictionary with selected fields.

    Args:
        log: An instance of CardioLog.

    Returns:
        A dictionary representation of the cardio log.
    """
    return {
        "type": "cardio",
        "exercise_name": log.exercise_name,
        "cardio_type": log.cardio_type.value if log.cardio_type else None,
        "total_duration_seconds": log.total_duration_seconds,
        "distance": log.distance,
        "distance_unit": log.distance_unit.value if log.distance_unit else None,
        "calories_burned": log.calories_burned,
        "avg_heart_rate": log.avg_heart_rate,
        "avg_rpe": log.avg_rpe,
        "intensity_level": log.intensity_level,
        "incline_level": log.incline_level,
        "notes": log.notes
    }

async def get_history_context(user_id: int, n_logs: int = 10) -> str:
    """
    Retrieves exercise logs from the user's current active workout and formats them as a JSON string.
    Returns empty string if no active workout exists or if the active workout has no exercises.

    Args:
        user_id: ID of the user whose logs are being fetched.
        n_logs: Maximum number of logs to retrieve. Defaults to 10.

    Returns:
        A pretty-formatted JSON string containing the exercise logs from the active workout,
        or empty string if no active workout or no exercises.
    """
    async with db_session() as db:
        # Get the user's active workout
        active_workout = await get_active_workout(db, user_id)
        
        if not active_workout:
            return ""
        
        # Get strength logs from the active workout
        strength_result = await db.execute(
            select(StrengthLog)
            .where(StrengthLog.workout_id == active_workout.id)
            .order_by(StrengthLog.exercise_date.desc())
            .limit(n_logs)
        )
        strength_logs = strength_result.scalars().all()
        
        # Get cardio logs from the active workout
        cardio_result = await db.execute(
            select(CardioLog)
            .where(CardioLog.workout_id == active_workout.id)
            .order_by(CardioLog.exercise_date.desc())
            .limit(n_logs)
        )
        cardio_logs = cardio_result.scalars().all()
        
        # Convert to dictionaries
        strength_dicts = [to_dict(log) for log in strength_logs]
        cardio_dicts = [cardio_to_dict(log) for log in cardio_logs]
        
        # Combine and sort by date (most recent first)
        all_logs = strength_dicts + cardio_dicts
        
        # If no exercises in the active workout, return empty string
        if not all_logs:
            return ""
        
        # Return only the requested number of logs
        limited_logs = all_logs[:n_logs]
        
        return json.dumps(limited_logs, indent=2)
