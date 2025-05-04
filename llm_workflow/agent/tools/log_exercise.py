from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.exercise_log import ExerciseLogCreate
from langchain_core.tools import tool
from db.crud.exercise_log import create_exercise_log
from db.session import db_session

@tool("log_exercise", args_schema=ExerciseLogCreate, return_direct=True)
def log_exercise(
    workout_id: int,
    exercise_name: Optional[str] = None,
    set_number: Optional[int] = None,
    reps: Optional[int] = None,
    weight: Optional[float] = None,
    weight_unit: Optional[str] = None,
    rir: Optional[int] = None,
    notes: Optional[str] = None
):
    """Registra una serie individual del entrenamiento del usuario, incluyendo ejercicio, repeticiones, peso, RIR y comentarios opcionales."""
    
    with db_session() as db:
        exercise_log = create_exercise_log(db, ExerciseLogCreate(
            workout_id=workout_id,
            exercise_name=exercise_name,
            set_number=set_number,
            reps=reps,
            weight=weight,
            weight_unit=weight_unit,
            rir=rir,
            notes=notes))
        
    return exercise_log



    
