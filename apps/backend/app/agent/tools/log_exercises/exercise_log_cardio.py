from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.discipline_exercise_logs.cardio import CardioLogCreate, CardioLogBase
from langchain_core.tools import tool
from db.crud.discipline_exercise_logs.cardio import create_cardio_log
from db.session import db_session
from db.crud.utils import get_or_create_workout_id
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig

@tool("exercise_log_cardio", args_schema=CardioLogBase)
async def exercise_log_cardio(
    config: RunnableConfig,
    cardio_type: str,
    total_duration_seconds: int,
    intervals_completed: Optional[int] = None,
    work_rest_ratio: Optional[str] = None,
    avg_heart_rate: Optional[int] = None,
    max_heart_rate: Optional[int] = None,
    heart_rate_zones: Optional[str] = None,
    estimated_calories: Optional[int] = None,
    avg_power_watts: Optional[float] = None,
    max_power_watts: Optional[float] = None,
    avg_rpe: Optional[float] = None,
    avg_cadence: Optional[int] = None,
    resistance_level: Optional[int] = None,
    avg_speed_kmh: Optional[float] = None,
    interval_rpe_data: Optional[str] = None,
    notes: Optional[str] = None
):
    """
    Registra una sesión de entrenamiento cardiovascular en la base de datos.
    
    Incluye información específica sobre ejercicios cardiovasculares como HIIT, LISS,
    spinning, elíptica. Esta tool está optimizada para registrar datos como intervalos,
    frecuencia cardíaca, potencia, calorías quemadas y otros parámetros específicos
    del entrenamiento cardiovascular.
    """
    user_id = config.get("configurable", {}).get("user_id")
    llm = config.get("configurable", {}).get("llm")
    
    if not user_id:
        raise ValueError("user_id is required in config")
    
    workout_id = await get_or_create_workout_id(user_id, llm)
    
    async with db_session() as db:
        await create_cardio_log(
            db, 
            CardioLogCreate(
                workout_id=workout_id,
                cardio_type=cardio_type,
                total_duration_seconds=total_duration_seconds,
                intervals_completed=intervals_completed,
                work_rest_ratio=work_rest_ratio,
                avg_heart_rate=avg_heart_rate,
                max_heart_rate=max_heart_rate,
                heart_rate_zones=heart_rate_zones,
                estimated_calories=estimated_calories,
                avg_power_watts=avg_power_watts,
                max_power_watts=max_power_watts,
                avg_rpe=avg_rpe,
                avg_cadence=avg_cadence,
                resistance_level=resistance_level,
                avg_speed_kmh=avg_speed_kmh,
                interval_rpe_data=interval_rpe_data,
                notes=notes
            ),
            user_id
        )
        
    return "Ejercicio cardiovascular registrado correctamente en la base de datos." 