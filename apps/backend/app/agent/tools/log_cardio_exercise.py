"""
Cardio exercise logging tool for the FitCoach AI agent.

This module contains the tool for logging cardiovascular training sessions,
including HIIT and steady-state cardio activities with simplified performance metrics
focused on the needs of strength/hypertrophy athletes.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.cardio_log import CardioLogCreate
from db.models.cardio_log import CardioType, DistanceUnit
from langchain_core.tools import tool
from db.crud.cardio_log import create_cardio_log
from db.session import db_session
from db.schemas.cardio_log import CardioLogAgentBase
from db.crud.utils import get_or_create_workout_id
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig

@tool("log_cardio_exercise", args_schema=CardioLogAgentBase)
async def log_cardio_exercise(
    config: RunnableConfig,
    exercise_name: str,
    cardio_type: CardioType,
    total_duration_seconds: int,
    distance: Optional[float] = None,
    distance_unit: Optional[DistanceUnit] = DistanceUnit.KM,
    calories_burned: Optional[int] = None,
    avg_heart_rate: Optional[int] = None,
    avg_rpe: Optional[float] = None,
    intensity_level: Optional[int] = None,
    incline_level: Optional[int] = None,
    notes: Optional[str] = None
):
    """Registra una sesión de entrenamiento cardiovascular del usuario en la base de datos (HIIT o steady-state). El usuario no necesariamente tiene que especificar que se registre una sesión en la base de datos, puede simplemente escribir lo que hizo en el entrenamiento.
    """
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id")
    llm = configurable.get("llm")
    
    if not user_id:
        raise ValueError("user_id is required")
    
    # Prepare exercise data for workout type inference
    exercise_data = {
        'cardio_type': cardio_type,
        'total_duration_seconds': total_duration_seconds,
        'avg_heart_rate': avg_heart_rate,
        'avg_rpe': avg_rpe,
        'notes': notes
    }
    
    # Get or create workout with exercise data for inference
    workout_id = await get_or_create_workout_id(user_id, exercise_data, llm)
    
    async with db_session() as db:
        await create_cardio_log(db, CardioLogCreate(
            user_id=user_id,
            workout_id=workout_id,
            exercise_name=exercise_name,
            cardio_type=cardio_type,
            total_duration_seconds=total_duration_seconds,
            distance=distance,
            distance_unit=distance_unit,
            calories_burned=calories_burned,
            avg_heart_rate=avg_heart_rate,
            avg_rpe=avg_rpe,
            intensity_level=intensity_level,
            incline_level=incline_level,
            notes=notes))
        
    return "Ejercicio de cardio registrado correctamente en la base de datos." 