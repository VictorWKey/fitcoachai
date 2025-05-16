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
from db.models.exercise_log import WeightUnit
from utils.utils import to_enum_or_none

@tool("log_exercise", args_schema=ExerciseLogBase)
async def log_exercise(
    config: RunnableConfig,
    exercise_name: str,
    set_number: int,
    reps: int,
    weight: float,
    weight_unit: WeightUnit,
    rir: int,
    notes: str
):
    """Registra una serie individual del entrenamiento del usuario, incluyendo ejercicio, repeticiones, peso, RIR y comentarios opcionales."""
    user_id: int = config["configurable"].get("user_id")
    print(type(exercise_name))
    print(type(set_number))
    print(type(reps))
    print(type(weight))
    print(type(weight_unit), weight_unit)
    print(type(rir))
    print(type(notes))
    
    workout_id = await get_or_create_workout_id(user_id)
    
    async with db_session() as db:
        await create_exercise_log(db, ExerciseLogCreate(
            workout_id=workout_id,
            exercise_name=exercise_name,
            set_number=set_number,
            reps=reps,
            weight=weight,
            weight_unit=weight_unit,
            rir=rir,
            notes=notes))
        
    return "Ejercicio registrado correctamente"



    
