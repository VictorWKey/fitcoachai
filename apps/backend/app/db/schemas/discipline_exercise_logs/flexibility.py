"""
Flexibility discipline schemas.
"""

from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from typing import Optional, Annotated
from utils.model_utils import coerce_null_string
from db.models.discipline_exercise_logs.common import StretchType

class FlexibilityLogBase(BaseModel):
    exercise_name: Annotated[
        str,
        BeforeValidator(coerce_null_string),
        Field(
            description="Nombre del ejercicio de flexibilidad realizado. Ejemplo: 'estiramiento de isquiotibiales', 'apertura de cadera', 'flexión de columna'."
        )
    ]
    joint_name: Annotated[
        str,
        BeforeValidator(coerce_null_string),
        Field(
            description="Articulación trabajada: cuello, hombro, codo, muñeca, columna, cadera, rodilla, tobillo."
        )
    ]
    rom_degrees: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Rango de movimiento alcanzado en grados (0-360°)."
        )
    ]
    stretch_time_seconds: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Tiempo de duración del estiramiento en segundos."
        )
    ]
    intensity_scale: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Intensidad del estiramiento en escala de 1-10."
        )
    ]
    stretch_type: Annotated[
        Optional[StretchType],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tipo de estiramiento: estático, dinámico, PNF, balístico."
        )
    ]
    pain_level: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Nivel de dolor durante el estiramiento en escala de 0-10."
        )
    ]
    pre_session_feeling: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Sensación antes de la sesión de estiramiento: relajado, tenso, muy tenso, etc."
        )
    ]
    post_session_feeling: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Sensación después de la sesión de estiramiento."
        )
    ]
    improvement_percentage: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Mejora porcentual respecto a la sesión anterior (-90% a +500%+)."
        )
    ]
    ambient_temperature: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Temperatura ambiente en grados Celsius."
        )
    ]
    body_temperature_feeling: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Sensación de temperatura corporal: frío, tibio, caliente."
        )
    ]
    notes: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Información adicional: técnicas utilizadas, limitaciones encontradas, progreso observado, etc."
        )
    ]

class FlexibilityLogCreate(FlexibilityLogBase):
    workout_id: int

class FlexibilityLogUpdate(BaseModel):
    exercise_name: Optional[str] = None
    joint_name: Optional[str] = None
    rom_degrees: Optional[float] = None
    stretch_time_seconds: Optional[int] = None
    intensity_scale: Optional[float] = None
    stretch_type: Optional[StretchType] = None
    pain_level: Optional[float] = None
    pre_session_feeling: Optional[str] = None
    post_session_feeling: Optional[str] = None
    improvement_percentage: Optional[float] = None
    ambient_temperature: Optional[float] = None
    body_temperature_feeling: Optional[str] = None
    notes: Optional[str] = None

class FlexibilityLog(FlexibilityLogBase):
    id: int
    user_id: int
    workout_id: int
    exercise_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 