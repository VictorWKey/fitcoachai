"""
Standard Exercise schemas for the FitCoach AI application.

Este módulo contiene los esquemas Pydantic para las operaciones relacionadas con los ejercicios estándar:
- Esquema base
- Esquema para creación
- Esquema para actualización
- Esquema para respuesta (API)
- Esquema para la base de datos (InDB)

Incluye validación de campos y enums consistentes con el modelo ORM.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from db.models.standard_exercises import MuscleGroupEnum, EquipmentEnum, StandardExerciseType

# Esquema base
class StandardExerciseBase(BaseModel):
    """
    Esquema base para los ejercicios estándar.
    """
    standard_name: str = Field(..., description="Nombre estándar del ejercicio. Debe ser único.")
    main_muscle_group: MuscleGroupEnum = Field(..., description="Grupo muscular principal involucrado.")
    equipment: EquipmentEnum = Field(..., description="Equipo principal utilizado.")
    type: StandardExerciseType = Field(..., description="Tipo de ejercicio: Compuesto o Aislado")

# Esquema para creación
class StandardExerciseCreate(StandardExerciseBase):
    """
    Esquema para crear un nuevo ejercicio estándar.
    """
    pass

# Esquema para actualización
class StandardExerciseUpdate(BaseModel):
    """
    Esquema para actualizar un ejercicio estándar existente. Todos los campos son opcionales.
    """
    standard_name: Optional[str] = Field(None, description="Nombre estándar del ejercicio.")
    main_muscle_group: Optional[MuscleGroupEnum] = Field(None, description="Grupo muscular principal involucrado.")
    equipment: Optional[EquipmentEnum] = Field(None, description="Equipo principal utilizado.")

# Esquema para la base de datos
class StandardExerciseInDB(StandardExerciseBase):
    """
    Esquema para representar el modelo en la base de datos.
    """
    id: int
    model_config = ConfigDict(from_attributes=True)

# Esquema para respuesta (API)
class StandardExercise(StandardExerciseBase):
    """
    Esquema para respuesta de API, seguro para exponer.
    """
    id: int
    model_config = ConfigDict(from_attributes=True) 