from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.workout import Workout
from ..schemas.workout import WorkoutCreate, WorkoutUpdate
from datetime import datetime

def get_workout(db: Session, workout_id: int) -> Optional[Workout]:
    """Obtener un entrenamiento por ID"""
    return db.query(Workout).filter(Workout.id == workout_id).first()

def get_user_workouts(db: Session, user_id: int) -> List[Workout]:
    """Obtener entrenamientos de un usuario"""
    return db.query(Workout).filter(Workout.user_id == user_id).order_by(Workout.created_at.desc()).all()

def create_workout(db: Session, workout_data: WorkoutCreate) -> Workout:
    """Crear un nuevo entrenamiento"""
    db_workout = Workout(
        user_id=workout_data.user_id,
        category=workout_data.category,
        start_time=workout_data.start_time
    )
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

def update_workout(db: Session, workout_id: int, update_data: WorkoutUpdate) -> Optional[Workout]:
    """Actualizar un entrenamiento"""
    db_workout = get_workout(db, workout_id)
    if not db_workout:
        return None

    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_workout, key, value)

    db.commit()
    db.refresh(db_workout)
    return db_workout

def delete_workout(db: Session, workout_id: int) -> bool:
    """Eliminar un entrenamiento"""
    db_workout = get_workout(db, workout_id)
    if not db_workout:
        return False

    db.delete(db_workout)
    db.commit()
    return True
