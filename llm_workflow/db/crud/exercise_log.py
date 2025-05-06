from sqlalchemy.orm import Session
from typing import Optional, List
from db.models.exercise_log import ExerciseLog
from db.schemas.exercise_log import ExerciseLogCreate, ExerciseLogUpdate

def get_exercise_log(db: Session, log_id: int) -> Optional[ExerciseLog]:
    """Obtener un log de ejercicio por ID"""
    return db.query(ExerciseLog).filter(ExerciseLog.id == log_id).first()

def get_workout_logs(db: Session, workout_id: int) -> List[ExerciseLog]:
    """Obtener todos los logs de un entrenamiento"""
    return db.query(ExerciseLog).filter(ExerciseLog.workout_id == workout_id).order_by(ExerciseLog.set_number).all()

def create_exercise_log(db: Session, log_data: ExerciseLogCreate) -> ExerciseLog:
    """Crear un nuevo log de ejercicio"""
    db_log = ExerciseLog(
        workout_id=log_data.workout_id,
        exercise_name=log_data.exercise_name,
        set_number=log_data.set_number,
        reps=log_data.reps,
        weight=log_data.weight,
        weight_unit=log_data.weight_unit,
        rir=log_data.rir,
        notes=log_data.notes,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def update_exercise_log(db: Session, log_id: int, update_data: ExerciseLogUpdate) -> Optional[ExerciseLog]:
    """Actualizar un log de ejercicio"""
    db_log = get_exercise_log(db, log_id)
    if not db_log:
        return None

    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_log, key, value)

    db.commit()
    db.refresh(db_log)
    return db_log

def delete_exercise_log(db: Session, log_id: int) -> bool:
    """Eliminar un log de ejercicio"""
    db_log = get_exercise_log(db, log_id)
    if not db_log:
        return False

    db.delete(db_log)
    db.commit()
    return True
