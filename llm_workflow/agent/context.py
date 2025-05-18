from db.session import db_session
from db.models.exercise_log import ExerciseLog
from sqlalchemy import select

import json

def to_dict(log):
    return {
        "exercise_name": log.exercise_name,
        "weight": log.weight,
        "reps": log.reps,
        "set_number": log.set_number,
    }

async def get_history_context(user_id: int, n_logs: int = 10) -> str:
    async with db_session() as db:
        result = await db.execute(
            select(ExerciseLog)
            .where(ExerciseLog.user_id == user_id)
            .order_by(ExerciseLog.exercise_date.desc())
            .limit(n_logs)
        )
        
        history = result.scalars().all()
        history_dicts = [to_dict(log) for log in history]

        return json.dumps(history_dicts, indent=2)  # 🔥 string bonito y útil para el prompt




