from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from db.models.workout import Workout
from db.session import db_session
from db.models.workout import Category, MuscleGroup


WORKOUT_TIMEOUT_MINUTES = 90

async def get_or_create_workout_id(user_id: int) -> int:
    now = datetime.now(timezone.utc)

    async with db_session() as db:
        # Buscar el último workout del usuario
        result = await db.execute(
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
            .limit(1)
        )
        last_workout = result.scalar_one_or_none()

        if last_workout is None or (now - last_workout.created_at) > timedelta(minutes=WORKOUT_TIMEOUT_MINUTES):
            new_workout = Workout(user_id=user_id, category=Category.STRENGTH, muscle_group=MuscleGroup.FULL_BODY, start_time=now)
            db.add(new_workout)
            await db.flush()
            await db.refresh(new_workout)
            return new_workout.id

        # Si sí hay uno reciente, reusar ese workout_id
        return last_workout.id
