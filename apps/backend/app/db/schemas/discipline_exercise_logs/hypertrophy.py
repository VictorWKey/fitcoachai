"""
Hypertrophy discipline schemas.
"""

from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from typing import Optional, Annotated
from utils.model_utils import coerce_null_string
from db.models.discipline_exercise_logs.common import WeightUnit, RangeOfMotion

class HypertrophyLogBase(BaseModel):
    exercise_name: Annotated[
        str,
        BeforeValidator(coerce_null_string),
        Field(
            description="Nombre del ejercicio de hipertrofia realizado. Ejemplo: 'curl de bíceps', 'press inclinado', 'extensiones de cuádriceps'."
        )
    ]
    set_number: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Número de la serie dentro del ejercicio. Se reinicia a 1 cuando cambia el ejercicio."
        )
    ]
    target_reps: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Número de repeticiones que se planeaba realizar en esta serie."
        )
    ]
    completed_reps: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Número de repeticiones efectivamente realizadas en esta serie, típicamente entre 6-20 para hipertrofia."
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
    tempo_eccentric: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tiempo en segundos de la fase excéntrica (bajada) del movimiento. Ejemplo: 3 segundos."
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
    rest_time_seconds: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Tiempo de descanso después de la serie en segundos. Típicamente 1-3 minutos para hipertrofia."
        )
    ]
    range_of_motion: Annotated[
        RangeOfMotion,
        BeforeValidator(coerce_null_string),
        Field(
            default=RangeOfMotion.FULL,
            description="Rango de movimiento utilizado: completo, parcial superior, parcial inferior, un cuarto, la mitad."
        )
    ]
    target_muscle: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Músculo objetivo principal del ejercicio basado en las demas propiedades del ejercicio. Ejemplo: 'pectoral', 'bíceps', 'cuádriceps'."
        )
    ]
    notes: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Información adicional: técnica utilizada, sensaciones musculares, ajustes en el equipo, conexión mente-músculo, etc."
        )
    ]

class HypertrophyLogCreate(HypertrophyLogBase):
    workout_id: int

class HypertrophyLogUpdate(BaseModel):
    exercise_name: Optional[str] = None
    set_number: Optional[int] = None
    target_reps: Optional[int] = None
    completed_reps: Optional[int] = None
    weight: Optional[float] = None
    weight_unit: Optional[WeightUnit] = None
    rpe: Optional[float] = None
    rir: Optional[int] = None
    tempo_eccentric: Optional[int] = None
    tempo_pause_bottom: Optional[int] = None
    tempo_concentric: Optional[int] = None
    rest_time_seconds: Optional[int] = None
    range_of_motion: Optional[RangeOfMotion] = None
    target_muscle: Optional[str] = None
    notes: Optional[str] = None

class HypertrophyLog(HypertrophyLogBase):
    id: int
    user_id: int
    workout_id: int
    exercise_date: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 