from datetime import datetime, timedelta
from db.models.workout import Workout
from db.session import db_session

WORKOUT_TIMEOUT_MINUTES = 90

def get_or_create_workout_id(user_id: int) -> int:
    now = datetime.now(datetime.UTC)

    with db_session() as db:
        # Buscar el último workout del usuario
        last_workout = (
            db.query(Workout)
            .filter(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
            .first()
        )

        # Si no hay workout reciente, crear uno nuevo
        if last_workout is None or (now - last_workout.created_at) > timedelta(minutes=WORKOUT_TIMEOUT_MINUTES):
            new_workout = Workout(user_id=user_id, category="strength", start_time=now)
            db.add(new_workout)
            db.flush()  # Para obtener el ID sin hacer commit explícito
            db.refresh(new_workout)
            return new_workout.id

        # Si sí hay uno reciente, reusar ese workout_id
        return last_workout.id