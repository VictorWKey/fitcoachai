"""
Cardio discipline schemas.
"""

from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from typing import Optional, Annotated
from utils.model_utils import coerce_null_string

class CardioLogBase(BaseModel):
    cardio_type: Annotated[
        str,
        BeforeValidator(coerce_null_string),
        Field(
            description="Tipo de cardio realizado: HIIT, LISS, spinning, elíptica, etc."
        )
    ]
    total_duration_seconds: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Duración total de la sesión de cardio en segundos."
        )
    ]
    intervals_completed: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Número de intervalos completados (para HIIT)."
        )
    ]
    work_rest_ratio: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Ratio de trabajo:descanso. Ejemplo: '1:1', '1:2', '3:1'."
        )
    ]
    avg_heart_rate: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Frecuencia cardíaca promedio en latidos por minuto."
        )
    ]
    max_heart_rate: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Frecuencia cardíaca máxima en latidos por minuto."
        )
    ]
    heart_rate_zones: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Distribución del tiempo en zonas de FC en formato JSON."
        )
    ]
    estimated_calories: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Calorías estimadas quemadas durante la sesión."
        )
    ]
    avg_power_watts: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Potencia promedio desarrollada en watts."
        )
    ]
    max_power_watts: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Potencia máxima desarrollada en watts."
        )
    ]
    avg_rpe: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="RPE promedio de toda la sesión en escala de 1-10."
        )
    ]
    avg_cadence: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Cadencia promedio en RPM o pasos por minuto."
        )
    ]
    resistance_level: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Nivel de resistencia utilizado (0-100)."
        )
    ]
    avg_speed_kmh: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Velocidad promedio en km/h."
        )
    ]
    interval_rpe_data: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Datos de RPE por intervalo en formato JSON."
        )
    ]
    notes: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Información adicional: sensaciones durante el ejercicio, equipamiento utilizado, incidencias, etc."
        )
    ]

class CardioLogCreate(CardioLogBase):
    workout_id: int

class CardioLogUpdate(BaseModel):
    cardio_type: Optional[str] = None
    total_duration_seconds: Optional[int] = None
    intervals_completed: Optional[int] = None
    work_rest_ratio: Optional[str] = None
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    heart_rate_zones: Optional[str] = None
    estimated_calories: Optional[int] = None
    avg_power_watts: Optional[float] = None
    max_power_watts: Optional[float] = None
    avg_rpe: Optional[float] = None
    avg_cadence: Optional[int] = None
    resistance_level: Optional[int] = None
    avg_speed_kmh: Optional[float] = None
    interval_rpe_data: Optional[str] = None
    notes: Optional[str] = None

class CardioLog(CardioLogBase):
    id: int
    user_id: int
    workout_id: int
    exercise_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 