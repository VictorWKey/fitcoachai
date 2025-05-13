from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.exercise_log import ExerciseLogCreate
from langchain_core.tools import tool
from db.crud.exercise_log import create_exercise_log
from db.session import db_session
from db.schemas.exercise_log import ExerciseLogBase
from db.crud.utils import get_or_create_workout_id
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig

@tool("log_exercise", args_schema=ExerciseLogBase, return_direct=True)
def log_exercise(
    config: RunnableConfig,
    exercise_name: Optional[str],
    set_number: Optional[int],
    reps: Optional[int],
    weight: Optional[float],
    weight_unit: Optional[str],
    rir: Optional[int],
    notes: Optional[str]
):
    """Registra una serie individual del entrenamiento del usuario, incluyendo ejercicio, repeticiones, peso, RIR y comentarios opcionales."""
    user_id = config["configurable"].get("thread_id")
    print("Llegamos a log_exercise", user_id)
    
    return "Ejercicio registrado correctamente"
    
    
    # workout_id = get_or_create_workout_id(user_id)
    
    # with db_session() as db:
    #     exercise_log = create_exercise_log(db, ExerciseLogCreate(
    #         workout_id=workout_id,
    #         exercise_name=exercise_name,
    #         set_number=set_number,
    #         reps=reps,
    #         weight=weight,
    #         weight_unit=weight_unit,
    #         rir=rir,
    #         notes=notes))
        
    # return exercise_log



    
