"""
Strength exercise logging tool for the FitCoach AI agent.

This module contains the tool for logging individual strength training sets,
including exercises, sets, reps, weight, and other performance metrics.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.strength_log import StrengthLogCreate
from langchain_core.tools import tool
from db.crud.strength_log import create_strength_log
from db.session import db_session
from db.schemas.strength_log import StrengthLogAgentBase
from db.crud.utils import get_or_create_workout_id
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig
from db.models.strength_log import WeightUnit
from core.services import infer_series_type
from utils.tempo_utils import fix_tempo_format

@tool("log_strength_exercise", args_schema=StrengthLogAgentBase)
async def log_strength_exercise(
    config: RunnableConfig,
    exercise_name: Optional[str] = None,
    set_number: Optional[int] = None,
    reps: Optional[int] = None,
    weight: Optional[float] = None,
    weight_unit: Optional[WeightUnit] = None,
    rir: Optional[int] = None,
    one_rm_percentage: Optional[float] = None,
    rpe: Optional[float] = None,
    tempo: Optional[str] = None,
    rest_time_seconds: Optional[int] = None,
    notes: Optional[str] = None
):
    """Registra una serie individual del entrenamiento de fuerza o hipertrofia del usuario en la base de datos. El usuario no necesariamente tiene que especificar que se registre una serie en la base de datos, puede simplemente escribir lo que hizo en el entrenamiento.
    """
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id")
    llm = configurable.get("llm")

    if not exercise_name:
        raise ValueError("Nombre del ejercicio requerido")

    if not set_number:
        raise ValueError("Número de serie requerido")

    if not reps:
        raise ValueError("Número de repeticiones requerido")

    if not weight:
        raise ValueError("Peso requerido")
    
    if not weight_unit:
        raise ValueError("Unidad de peso requerida")
    
    if not user_id:
        raise ValueError("user_id is required")
    
    # Validate and normalize tempo format
    if tempo is not None:
        tempo = fix_tempo_format(tempo)
    
    # Prepare exercise data for workout type inference
    exercise_data = {
        'exercise_name': exercise_name,
        'set_number': set_number,
        'reps': reps,
        'weight': weight,
        'weight_unit': weight_unit,
        'rir': rir,
        'notes': notes
    }
    
    # Get or create workout with exercise data for inference
    workout_id = await get_or_create_workout_id(user_id, exercise_data, llm)
    
    # Determine exercise type using sophisticated analysis
    exercise_type = infer_series_type(
        rir=rir,
        one_rm_percentage=one_rm_percentage,
        rpe=rpe,
        tempo=tempo,
        rest_time_seconds=rest_time_seconds,
    )
    
    async with db_session() as db:
        await create_strength_log(db, StrengthLogCreate(
            user_id=user_id,
            workout_id=workout_id,
            exercise_name=exercise_name,
            exercise_type=exercise_type,
            set_number=set_number,
            reps=reps,
            weight=weight,
            weight_unit=weight_unit,
            rir=rir,
            one_rm_percentage=one_rm_percentage,
            rpe=rpe,
            tempo=tempo,
            rest_time_seconds=rest_time_seconds,
            notes=notes))
        
    return "Ejercicio registrado correctamente en la base de datos."
