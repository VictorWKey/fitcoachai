from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.discipline_exercise_logs.hypertrophy import HypertrophyLogCreate, HypertrophyLogBase
from db.models.discipline_exercise_logs.common import WeightUnit, RangeOfMotion
from langchain_core.tools import tool
from db.crud.discipline_exercise_logs.hypertrophy import create_hypertrophy_log
from db.session import db_session
from db.crud.utils import get_or_create_workout_id
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig

@tool("exercise_log_hypertrophy", args_schema=HypertrophyLogBase)
async def exercise_log_hypertrophy(
    config: RunnableConfig,
    exercise_name: str,
    set_number: int,
    completed_reps: int,
    weight: float,
    weight_unit: WeightUnit = WeightUnit.KG,
    target_reps: Optional[int] = None,
    rpe: Optional[float] = None,
    rir: Optional[int] = None,
    tempo_eccentric: Optional[int] = None,
    tempo_pause_bottom: Optional[int] = None,
    tempo_concentric: Optional[int] = None,
    rest_time_seconds: Optional[int] = None,
    range_of_motion: RangeOfMotion = RangeOfMotion.FULL,
    target_muscle: Optional[str] = None,
    notes: Optional[str] = None
):
    """
    Registra una serie individual de entrenamiento de hipertrofia/culturismo en la base de datos.
    
    Incluye información detallada sobre ejercicio, repeticiones, peso, tempo, RIR, RPE y otros
    parámetros específicos para entrenamiento de hipertrofia. Esta tool está optimizada para
    registrar ejercicios de hipertrofia donde se manejan series, repeticiones, peso, tempo
    y técnicas avanzadas como RIR (Reps in Reserve) y RPE (Rate of Perceived Exertion).
    """
    user_id = config.get("configurable", {}).get("user_id")
    llm = config.get("configurable", {}).get("llm")
    
    if not user_id:
        raise ValueError("user_id is required in config")
    
    workout_id = await get_or_create_workout_id(user_id, llm)
    
    async with db_session() as db:
        await create_hypertrophy_log(
            db, 
            HypertrophyLogCreate(
                workout_id=workout_id,
                exercise_name=exercise_name,
                set_number=set_number,
                target_reps=target_reps,
                completed_reps=completed_reps,
                weight=weight,
                weight_unit=weight_unit,
                rpe=rpe,
                rir=rir,
                tempo_eccentric=tempo_eccentric,
                tempo_pause_bottom=tempo_pause_bottom,
                tempo_concentric=tempo_concentric,
                rest_time_seconds=rest_time_seconds,
                range_of_motion=range_of_motion,
                target_muscle=target_muscle,
                notes=notes
            ),
            user_id
        )
        
    return "Ejercicio de hipertrofia registrado correctamente en la base de datos."



    
