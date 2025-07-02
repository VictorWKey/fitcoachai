"""
Context management utilities for retrieving and formatting user exercise history.
Provides functionality to fetch exercise logs across all disciplines and format them for agent context.
"""

from db.session import db_session
from db.models.discipline_exercise_logs import (
    HypertrophyLog, MaxStrengthLog, FlexibilityLog, CardioLog
)
from sqlalchemy import select, union_all, func

import json

# All discipline models for querying
ALL_DISCIPLINE_MODELS = [
    HypertrophyLog, MaxStrengthLog, FlexibilityLog, CardioLog
]


def to_dict(log, discipline_name: str):
    """
    Converts an exercise log instance into a dictionary with selected fields.

    Args:
        log: An instance of any discipline exercise log.
        discipline_name: Name of the discipline/table.

    Returns:
        A dictionary representation of the exercise log.
    """
    log_dict = {
        "exercise_name": log.exercise_name,
        "discipline": discipline_name,
        "exercise_date": log.exercise_date.isoformat() if log.exercise_date else None,
        "set_number": getattr(log, 'set_number', None),
    }
    
    # Add common fields that might exist across different disciplines
    if hasattr(log, 'weight'):
        log_dict["weight"] = log.weight
        log_dict["weight_unit"] = log.weight_unit.value if hasattr(log, 'weight_unit') and log.weight_unit else None
    
    if hasattr(log, 'completed_reps'):
        log_dict["reps"] = log.completed_reps
    elif hasattr(log, 'reps'):
        log_dict["reps"] = log.reps
    
    if hasattr(log, 'rir'):
        log_dict["rir"] = log.rir
    
    if hasattr(log, 'distance'):
        log_dict["distance"] = log.distance
        log_dict["distance_unit"] = log.distance_unit.value if hasattr(log, 'distance_unit') and log.distance_unit else None
    
    if hasattr(log, 'duration_seconds'):
        log_dict["duration_seconds"] = log.duration_seconds
    
    if hasattr(log, 'target_muscle'):
        log_dict["target_muscle"] = log.target_muscle
    
    return log_dict


async def get_history_context(user_id: int, n_logs: int = 10) -> str:
    """
    Retrieves the most recent exercise logs for a user across all disciplines 
    and formats them as a JSON string.

    Args:
        user_id: ID of the user whose logs are being fetched.
        n_logs: The number of most recent logs to retrieve. Defaults to 10.

    Returns:
        A pretty-formatted JSON string containing the selected exercise logs.
    """
    async with db_session() as db:
        # Collect all logs from all discipline tables
        all_logs = []
        
        for model in ALL_DISCIPLINE_MODELS:
            result = await db.execute(
                select(model)
                .where(model.user_id == user_id)
                .order_by(model.exercise_date.desc())
                .limit(n_logs)  # Get more than needed from each table, we'll sort later
            )
            
            logs = result.scalars().all()
            discipline_name = model.__tablename__
            
            for log in logs:
                all_logs.append((log, discipline_name))
        
        # Sort all logs by date (most recent first) and take only n_logs
        all_logs.sort(key=lambda x: x[0].exercise_date, reverse=True)
        recent_logs = all_logs[:n_logs]
        
        # Convert to dictionaries
        history_dicts = [to_dict(log, discipline) for log, discipline in recent_logs]

        return json.dumps(history_dicts, indent=2)
