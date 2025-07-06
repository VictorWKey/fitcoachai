"""
Strength log schemas for the FitCoach AI application.

This module contains Pydantic schemas for strength training exercise logs including:
- Agent schema base (for LLM tools) without exercise_type field
- Complete schema base with all fields including exercise_type
- Create schema for creating new strength logs
- Update schema for modifying existing strength logs
- Response schema for returning strength log data

All schemas include comprehensive field descriptions for LLM processing and validation.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import Field
from db.models.strength_log import WeightUnit, ExerciseType
from utils.model_utils import coerce_null_string
from typing import Annotated
from pydantic import BeforeValidator

class StrengthLogAgentBase(BaseModel):
    """
    Base schema for strength training logs used by the LLM agent.
    
    This schema is specifically designed for agent tools and does NOT include
    the exercise_type field, which should be set programmatically by the application.
    
    Contains common fields for all strength training logs that the agent can infer.
    """
    exercise_name: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Nombre del ejercicio realizado. Ejemplo: 'press de banca', 'remo con barra'."
        )
    ]
    set_number: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Número de la serie dentro del ejercicio. Por ejemplo, 1 si es la primera serie, 2 si es la segunda, etc. Si el nombre del ejercicio cambia, el número de la serie se reinicia a 1."
        )
    ]
    reps: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Cantidad de repeticiones realizadas en esta serie."
        )
    ]
    weight: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Peso utilizado por el usuario en esta serie. No inclyas la unidad de medida. Solo el número."
        )
    ]
    weight_unit: Annotated[
        Optional[WeightUnit],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Unidad del peso registrado. Por ejemplo: kg o lbs"
        )
    ]
    one_rm_percentage: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Porcentaje del 1RM (una repetición máxima) utilizado. Rango típico: 30-120%."
        )
    ]
    rir: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Repeticiones en reserva (RIR) reportadas por el usuario. Puede ir de 0 a 10."
        )
    ]
    rpe: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Escala de esfuerzo percibido (RPE). Escala de 1 a 10."
        )
    ]
    tempo: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tempo del ejercicio en formato 'E-B-C-T' donde cada letra representa los segundos de cada fase: E=Excéntrica (bajada), B=Bottom (pausa abajo), C=Concéntrica (subida), T=Top (pausa arriba). Ejemplos: '3-1-1-0', '2-0-2-0', '4-2-1-1'. Si una fase no aplica, usar 'X'. Para movimientos explosivos usar 'X' en la fase concéntrica."
        )
    ]
    rest_time_seconds: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tiempo de descanso en segundos después de esta serie."
        )
    ]
    notes: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Información adicional *no* capturada por los otros campos: weight_unit, rir, serie_number, reps, series_number y exercise. Por ejemplo: técnica usada, sensaciones, ajustes en el equipo, o cualquier dato relevante. Si no hay nada extra, dejar vacío o null."
        )
    ]

class StrengthLogBase(StrengthLogAgentBase):
    """
    Complete base schema for strength training logs.
    
    Extends the agent base schema with the exercise_type field that is set programmatically.
    This schema is used for CRUD operations and database interactions.
    """
    exercise_type: Annotated[
        Optional[ExerciseType],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tipo de ejercicio: strength (fuerza), hypertrophy (hipertrofia), o technique (técnica). Este campo se establece programáticamente y no debe ser inferido por el agente."
        )
    ]

# Crear
class StrengthLogCreate(StrengthLogBase):
    """
    Schema for creating a new strength training log entry.
    
    Extends the complete base schema with required user and workout identification.
    """
    user_id: int
    workout_id: int

# Actualizar
class StrengthLogUpdate(BaseModel):
    """
    Schema for updating an existing strength training log entry.
    
    All fields are optional to allow partial updates.
    """
    exercise_name: Optional[str] = None
    exercise_type: Optional[ExerciseType] = None
    set_number: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    weight_unit: Optional[WeightUnit] = None
    one_rm_percentage: Optional[float] = None
    rir: Optional[int] = None
    rpe: Optional[float] = None
    tempo: Optional[str] = None
    rest_time_seconds: Optional[int] = None
    notes: Optional[str] = None

# Respuesta
class StrengthLog(StrengthLogBase):
    """
    Schema for strength training log response data.
    
    Includes database-generated fields like ID and timestamps.
    """
    id: int
    workout_id: int
    exercise_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
