from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.discipline_exercise_logs.max_strength import MaxStrengthLogCreate, MaxStrengthLogBase
from db.models.discipline_exercise_logs.common import WeightUnit
from langchain_core.tools import tool
from db.crud.discipline_exercise_logs.max_strength import create_max_strength_log
from db.session import db_session
from db.crud.utils import get_or_create_workout_id
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig

@tool("exercise_log_max_strength", args_schema=MaxStrengthLogBase)
async def exercise_log_max_strength(
    config: RunnableConfig,
    exercise_name: str,
    set_number: int,
    reps: int,
    weight: float,
    weight_unit: WeightUnit = WeightUnit.KG,
    rpe: Optional[float] = None,
    rir: Optional[int] = None,
    rest_time_seconds: Optional[int] = None,
    one_rm_percentage: Optional[float] = None,
    exercise_type: Optional[str] = None,
    tempo_eccentric: Optional[int] = None,
    tempo_pause_bottom: Optional[int] = None,
    tempo_concentric: Optional[int] = None,
    notes: Optional[str] = None
):
    """
    Registra una serie individual de entrenamiento de fuerza máxima en la base de datos.
    
    Incluye información específica sobre ejercicios de fuerza máxima con repeticiones bajas
    (1-10) y cargas altas. Esta tool está optimizada para registrar datos como porcentaje
    de 1RM, velocidad de ejecución, RPE y otros parámetros específicos del entrenamiento
    de fuerza máxima.
    """
    user_id = config.get("configurable", {}).get("user_id")
    llm = config.get("configurable", {}).get("llm")
    
    if not user_id:
        raise ValueError("user_id is required in config")
    
    workout_id = await get_or_create_workout_id(user_id, llm)
    
    async with db_session() as db:
        await create_max_strength_log(
            db, 
            MaxStrengthLogCreate(
                workout_id=workout_id,
                exercise_name=exercise_name,
                set_number=set_number,
                reps=reps,
                weight=weight,
                weight_unit=weight_unit,
                rpe=rpe,
                rir=rir,
                rest_time_seconds=rest_time_seconds,
                one_rm_percentage=one_rm_percentage,
                exercise_type=exercise_type,
                tempo_eccentric=tempo_eccentric,
                tempo_pause_bottom=tempo_pause_bottom,
                tempo_concentric=tempo_concentric,
                notes=notes
            ),
            user_id
        )
        
    return "Ejercicio de fuerza máxima registrado correctamente en la base de datos." 