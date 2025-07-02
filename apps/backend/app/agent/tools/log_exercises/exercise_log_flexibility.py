from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.discipline_exercise_logs.flexibility import FlexibilityLogCreate, FlexibilityLogBase
from db.models.discipline_exercise_logs.common import StretchType
from langchain_core.tools import tool
from db.crud.discipline_exercise_logs.flexibility import create_flexibility_log
from db.session import db_session
from db.crud.utils import get_or_create_workout_id
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig

@tool("exercise_log_flexibility", args_schema=FlexibilityLogBase)
async def exercise_log_flexibility(
    config: RunnableConfig,
    exercise_name: str,
    joint_name: str,
    stretch_time_seconds: int,
    rom_degrees: Optional[float] = None,
    intensity_scale: Optional[float] = None,
    stretch_type: Optional[StretchType] = None,
    pain_level: Optional[float] = None,
    pre_session_feeling: Optional[str] = None,
    post_session_feeling: Optional[str] = None,
    improvement_percentage: Optional[float] = None,
    ambient_temperature: Optional[float] = None,
    body_temperature_feeling: Optional[str] = None,
    notes: Optional[str] = None
):
    """
    Registra una sesión de entrenamiento de flexibilidad en la base de datos.
    
    Incluye información específica sobre ejercicios de flexibilidad y estiramiento como
    rango de movimiento, intensidad, tipo de estiramiento, sensaciones antes y después,
    mejoras en flexibilidad y otros parámetros específicos del entrenamiento de flexibilidad.
    """
    user_id = config.get("configurable", {}).get("user_id")
    llm = config.get("configurable", {}).get("llm")
    
    if not user_id:
        raise ValueError("user_id is required in config")
    
    workout_id = await get_or_create_workout_id(user_id, llm)
    
    async with db_session() as db:
        await create_flexibility_log(
            db, 
            FlexibilityLogCreate(
                workout_id=workout_id,
                exercise_name=exercise_name,
                joint_name=joint_name,
                rom_degrees=rom_degrees,
                stretch_time_seconds=stretch_time_seconds,
                intensity_scale=intensity_scale,
                stretch_type=stretch_type,
                pain_level=pain_level,
                pre_session_feeling=pre_session_feeling,
                post_session_feeling=post_session_feeling,
                improvement_percentage=improvement_percentage,
                ambient_temperature=ambient_temperature,
                body_temperature_feeling=body_temperature_feeling,
                notes=notes
            ),
            user_id
        )
        
    return "Ejercicio de flexibilidad registrado correctamente en la base de datos." 