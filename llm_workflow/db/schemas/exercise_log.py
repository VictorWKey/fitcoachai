from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import Field

class WeightUnit(str, Enum):
    KG = "kg"
    LB = "lb"

# Base
class ExerciseLogBase(BaseModel):
    exercise_name: Optional[str] = Field(
        description="Nombre del ejercicio realizado. Ejemplo: 'press de banca', 'remo con barra'."
    )
    set_number: Optional[int] = Field(
        description="Número de la serie dentro del ejercicio. Por ejemplo, 1 si es la primera serie, 2 si es la segunda, etc."
    )
    reps: Optional[int] = Field(
        description="Cantidad de repeticiones realizadas en esta serie."
    )
    weight: Optional[float] = Field(
        description="Peso utilizado por el usuario en esta serie."
    )
    weight_unit: Optional[WeightUnit] = Field(
        description="Unidad del peso registrado."
    )
    rir: Optional[int] = Field(
        default=None,
        description="Repeticiones en reserva (RIR) reportadas por el usuario. Puede ir de 0 a 10."
    )
    notes: Optional[str] = Field(
        default=None,
        description="Información adicional *no* capturada por los otros campos: weight_unit, rir, serie_number, reps, series_number y exercise. Por ejemplo: técnica usada, sensaciones, ajustes en el equipo, o cualquier dato relevante. Si no hay nada extra, dejar vacío o null."
    )

# Crear
class ExerciseLogCreate(ExerciseLogBase):
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
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
