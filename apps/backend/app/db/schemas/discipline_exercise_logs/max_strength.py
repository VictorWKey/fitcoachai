"""
Max Strength discipline schemas.
"""

from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from typing import Optional, Annotated
from utils.model_utils import coerce_null_string
from db.models.discipline_exercise_logs.common import WeightUnit, TempoPhase, RangeOfMotion

class MaxStrengthLogBase(BaseModel):
    exercise_name: Annotated[
        str,
        BeforeValidator(coerce_null_string),
        Field(
            description="Nombre del ejercicio de fuerza máxima realizado. Ejemplo: 'sentadilla', 'press de banca', 'peso muerto'."
        )
    ]
    set_number: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Número de la serie dentro del ejercicio. Por ejemplo, 1 si es la primera serie, 2 si es la segunda, etc."
        )
    ]
    reps: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Cantidad de repeticiones realizadas en esta serie, típicamente entre 1-10 para fuerza máxima."
        )
    ]
    weight: Annotated[
        float,
        BeforeValidator(coerce_null_string),
        Field(
            description="Peso utilizado en esta serie. Solo el número, sin unidad de medida."
        )
    ]
    weight_unit: Annotated[
        WeightUnit,
        BeforeValidator(coerce_null_string),
        Field(
            default=WeightUnit.KG,
            description="Unidad del peso registrado: kg o lb."
        )
    ]
    rpe: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Percepción del esfuerzo (RPE) en escala de 1-10. Indica qué tan difícil se sintió la serie."
        )
    ]
    rir: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Repeticiones en reserva (RIR). Cuántas repeticiones más podría haber hecho el usuario."
        )
    ]
    rest_time_seconds: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tiempo de descanso después de la serie en segundos. Típicamente 2-8 minutos para fuerza máxima."
        )
    ]
    one_rm_percentage: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Porcentaje del 1RM (una repetición máxima) utilizado en esta serie. Ejemplo: 85 para 85%."
        )
    ]
    exercise_type: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tipo específico de ejercicio de fuerza: sentadilla, press banca, peso muerto, clean, jerk, snatch, etc."
        )
    ]
    notes: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Información adicional sobre la serie: técnica utilizada, sensaciones, ajustes en el equipo, fallos técnicos, etc."
        )
    ]
    tempo_eccentric: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tiempo en segundos de la fase excéntrica (bajada) del movimiento."
        )
    ]
    tempo_pause_bottom: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tiempo en segundos de pausa en la posición inferior del movimiento."
        )
    ]
    tempo_concentric: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tiempo en segundos de la fase concéntrica (subida) del movimiento."
        )
    ]

class MaxStrengthLogCreate(MaxStrengthLogBase):
    workout_id: int

class MaxStrengthLogUpdate(BaseModel):
    exercise_name: Optional[str] = None
    set_number: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    weight_unit: Optional[WeightUnit] = None
    rpe: Optional[float] = None
    rir: Optional[int] = None
    rest_time_seconds: Optional[int] = None
    one_rm_percentage: Optional[float] = None
    exercise_type: Optional[str] = None
    tempo_eccentric: Optional[int] = None
    tempo_pause_bottom: Optional[int] = None
    tempo_concentric: Optional[int] = None
    notes: Optional[str] = None

class MaxStrengthLog(MaxStrengthLogBase):
    id: int
    user_id: int
    workout_id: int
    exercise_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 