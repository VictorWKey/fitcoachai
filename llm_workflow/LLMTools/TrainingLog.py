from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal

class TrainingLog(BaseModel):
    """Registra una serie individual del entrenamiento del usuario, incluyendo ejercicio, repeticiones, peso, RIR y comentarios opcionales."""

    exercise: str = Field(
        description="Nombre del ejercicio realizado. Ejemplo: 'press de banca', 'remo con barra'."
    )
    serie_number: int = Field(
        description="Número de la serie dentro del ejercicio. Por ejemplo, 1 si es la primera serie, 2 si es la segunda, etc."
    )
    rep: int = Field(
        description="Cantidad de repeticiones realizadas en esta serie."
    )
    rir: Optional[int] = Field(
        default=None,
        description="Repeticiones en reserva (RIR) reportadas por el usuario. Puede ir de 0 a 10."
    )
    weight: float = Field(
        description="Peso utilizado por el usuario en esta serie."
    )
    weight_unit: Literal["kg", "lb"] = Field(
        description="Unidad del peso registrado. Debe ser 'kg' o 'lb'."
    )
    comment: Optional[str] = Field(
        default=None,
        description="Comentario opcional del usuario sobre esta serie. Ejemplos: 'me costó mucho', 'moví el asiento', etc."
    )
    date: str = Field(
        default_factory=lambda: datetime.now().date().isoformat(),
        description="Fecha del registro en formato ISO (YYYY-MM-DD). Se genera automáticamente al crear el registro."
    )