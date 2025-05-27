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

@tool("log_exercise", args_schema=ExerciseLogBase)
async def log_exercise(
    config: RunnableConfig,
    exercise_name: Optional[str] = None,
    set_number: Optional[int] = None,
    reps: Optional[int] = None,
    weight: Optional[float] = None,
    weight_unit: Optional[WeightUnit] = None,
    rir: Optional[int] = None,
    notes: Optional[str] = None
):
    """Registra una serie individual del entrenamiento del usuario en la base de datos, incluyendo ejercicio, repeticiones, peso, RIR y comentarios opcionales cuando el usuario pone información sobre lo que podria ser una serie de entrenamiento. El usuario no necesariamente tiene que especificar que se registre una serie en la base de datos, puede simplemente escribir lo que hizo en el entrenamiento.
    """
    user_id: int = config["configurable"].get("user_id")
    workout_id = await get_or_create_workout_id(user_id)
    
    async with db_session() as db:
        await create_exercise_log(db, ExerciseLogCreate(
            user_id=user_id,
            workout_id=workout_id,
            exercise_name=exercise_name,
            set_number=set_number,
            reps=reps,
            weight=weight,
            weight_unit=weight_unit,
            rir=rir,
            notes=notes))
        
    return "Ejercicio registrado correctamente en la base de datos."



    
