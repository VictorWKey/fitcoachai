"""
Cardio log schemas for the FitCoach AI application.

This module contains Pydantic schemas for cardiovascular exercise logs including:
- Agent schema base (for LLM tools) with simplified cardio training fields
- Complete schema base with all fields (currently same as agent base)
- Create schema for creating new cardio logs
- Update schema for modifying existing cardio logs
- Response schema for returning cardio log data

All schemas include comprehensive field descriptions for LLM processing and validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import Field
from utils.model_utils import coerce_null_string
from typing import Annotated
from pydantic import BeforeValidator
from enum import Enum
from db.models.cardio_log import CardioType, DistanceUnit

class CardioLogAgentBase(BaseModel):
    """
    Base schema for cardio training logs used by the LLM agent.
    
    This schema is specifically designed for agent tools and contains
    all fields that the agent can infer for cardio exercises.
    
    Contains common fields for all cardio training logs.
    """
    exercise_name: Annotated[
        str,
        BeforeValidator(coerce_null_string),
        Field(
            description="Nombre del ejercicio cardiovascular. Ejemplo: 'Caminata en cinta', 'Bicicleta estática', 'Elíptica'."
        )
    ]
    cardio_type: Annotated[
        CardioType,
        Field(
            description="Tipo de entrenamiento cardiovascular. Opciones: 'hiit' (HIIT, Tabata), 'steady_state' (cardio constante, LISS, MISS)."
        )
    ]
    total_duration_seconds: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Duración total del entrenamiento en segundos."
        )
    ]
    distance: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Distancia recorrida durante el entrenamiento."
        )
    ]
    distance_unit: Annotated[
        Optional[DistanceUnit],
        Field(
            default=DistanceUnit.KM,
            description="Unidad de distancia: 'km' para kilómetros, 'mi' para millas."
        )
    ]
    calories_burned: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Calorías quemadas durante el entrenamiento."
        )
    ]
    avg_heart_rate: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Frecuencia cardíaca promedio durante el entrenamiento."
        )
    ]
    avg_rpe: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Escala de esfuerzo percibido (RPE) promedio. Escala de 1 a 10."
        )
    ]
    intensity_level: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Nivel de intensidad del ejercicio (1-20). Representa la velocidad en cintas de correr o el nivel de resistencia en bicicletas/elípticas."
        )
    ]
    incline_level: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Nivel de inclinación en máquinas como cintas de correr (0-15)."
        )
    ]
    notes: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Información adicional sobre el entrenamiento cardiovascular: sensaciones, ajustes en el equipo, o cualquier dato relevante."
        )
    ]

class CardioLogAgent(CardioLogAgentBase):
    """
    Schema for cardio training logs used by the LLM agent.
    
    This schema is specifically designed for agent tools and does NOT include
    the exercise_type field, which should be set programmatically by the application.
    """

class CardioLogBase(CardioLogAgentBase):
    """
    Complete base schema for cardio training logs.
    
    Currently extends the agent base schema. If in the future you need to add
    fields that should be set programmatically (not by the agent), you can
    add them here.
    
    This schema is used for CRUD operations and database interactions.
    """
    # Currently no additional fields beyond what the agent can infer
    # If you need to add programmatically controlled fields in the future,
    # add them here following the same pattern as StrengthLogBase

# Crear
class CardioLogCreate(CardioLogBase):
    """
    Schema for creating a new cardiovascular exercise log entry.
    
    Can be either:
    - Programmed cardio: provide programmed_exercise_id (session derived automatically)
    - Free cardio: provide training_session_id directly
    """
    # One of these two should be provided, but not both
    programmed_exercise_id: Optional[int] = None
    training_session_id: Optional[int] = None
    user_id: int

# Actualizar
class CardioLogUpdate(BaseModel):
    """
    Schema for updating an existing cardiovascular exercise log entry.
    
    All fields are optional to allow partial updates.
    """
    exercise_name: Optional[str] = None
    cardio_type: Optional[CardioType] = None
    total_duration_seconds: Optional[int] = None
    distance: Optional[float] = None
    distance_unit: Optional[DistanceUnit] = None
    calories_burned: Optional[int] = None
    avg_heart_rate: Optional[int] = None
    avg_rpe: Optional[float] = None
    intensity_level: Optional[int] = None
    incline_level: Optional[int] = None
    notes: Optional[str] = None
    programmed_exercise_id: Optional[int] = None
    training_session_id: Optional[int] = None

# Respuesta
class CardioLog(CardioLogBase):
    """
    Schema for cardiovascular exercise log response data.
    
    Includes database-generated fields like ID and timestamps.
    """
    id: int
    user_id: int
    programmed_exercise_id: Optional[int] = None
    training_session_id: Optional[int] = None
    exercise_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 