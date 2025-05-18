from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import Field
from db.models.exercise_log import WeightUnit
from utils.utils import coerce_null_string
from typing import Annotated
from pydantic import BeforeValidator

class ExerciseLogBase(BaseModel):
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
    rir: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Repeticiones en reserva (RIR) reportadas por el usuario. Puede ir de 0 a 10."
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


# Crear
class ExerciseLogCreate(ExerciseLogBase):
    user_id: int
    workout_id: int

# Actualizar
class ExerciseLogUpdate(BaseModel):
    exercise_name: Optional[str] = None
    set_number: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    weight_unit: Optional[WeightUnit] = None
    rir: Optional[int] = None
    notes: Optional[str] = None

# Respuesta
class ExerciseLog(ExerciseLogBase):
    id: int
    workout_id: int
    exercise_date: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
