from db.session import db_session
from db.models.exercise_log import ExerciseLog
from sqlalchemy import select

import json

def to_dict(log):
    """
    Converts an ExerciseLog instance into a dictionary with selected fields.

    Args:
        log: An instance of ExerciseLog.

    Returns:
        A dictionary representation of the exercise log.
    """
    return {
        "exercise_name": log.exercise_name,
        "weight": log.weight,
        "reps": log.reps,
        "set_number": log.set_number,
    }

async def get_history_context(user_id: int, n_logs: int = 10) -> str:
    """
    Retrieves the most recent exercise logs for a user and formats them as a JSON string.

    Args:
        user_id: ID of the user whose logs are being fetched.
        n_logs: The number of most recent logs to retrieve. Defaults to 10.

    Returns:
        A pretty-formatted JSON string containing the selected exercise logs.
    """
    async with db_session() as db:
        result = await db.execute(
            select(ExerciseLog)
            .where(ExerciseLog.user_id == user_id)
            .order_by(ExerciseLog.exercise_date.desc())
            .limit(n_logs)
        )
        
        history = result.scalars().all()
        history_dicts = [to_dict(log) for log in history]

        return json.dumps(history_dicts, indent=2)
