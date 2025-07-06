"""
Workout schemas for the FitCoach AI application.

This module contains Pydantic schemas for workout management including:
- Base schema with workout metadata (muscle group, category, etc.)
- Create schema for creating new workouts
- Update schema for modifying existing workouts
- Response schema for returning workout data
- Workout type inference schema for LLM processing

All schemas support the workout tracking and classification system.
"""

from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime
from db.models.workout import MuscleGroup, Category

class WorkoutBase(BaseModel):
    """
    Base schema for workout data.
    
    Contains common workout metadata fields.
    """
    muscle_group: MuscleGroup
    category: Category
    is_finished: bool = False

class WorkoutCreate(WorkoutBase):
    """
    Schema for creating a new workout.
    
    Extends the base schema with required user identification and optional start time.
    """
    user_id: int
    start_time: Optional[datetime] = None  

class WorkoutUpdate(BaseModel):
    """
    Schema for updating an existing workout.
    
    All fields are optional to allow partial updates.
    """
    muscle_group: Optional[MuscleGroup] = None
    category: Optional[Category] = None
    start_time: Optional[datetime] = None
    is_finished: Optional[bool] = None
    
# Response
class Workout(WorkoutBase):
    """
    Schema for workout response data.
    
    Includes database-generated fields like ID and timestamps.
    """
    id: int
    user_id: int
    start_time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for workout type inference
class WorkoutTypeInference(BaseModel):
    """
    Schema to infer workout type based on exercises.
    Used by the LLM to determine muscle group and category.
    """
    muscle_group: Annotated[
        MuscleGroup,
        Field(
            description="""
            El grupo muscular principal del entrenamiento. Debe ser uno de los siguientes valores:
            - chest: Ejercicios principalmente para pecho (press de banca, aperturas, etc.)
            - back: Ejercicios principalmente para espalda (dominadas, remo, pull-downs, etc.)
            - legs_in_general: Ejercicios para piernas sin énfasis específico
            - legs_cuadriceps_enphasis: Ejercicios para piernas con énfasis en cuádriceps (sentadillas, prensa, etc.)
            - legs_hamstrings_enphasis: Ejercicios para piernas con énfasis en isquiotibiales (peso muerto, curl de piernas, etc.)
            - shoulders: Ejercicios para hombros (press militar, elevaciones laterales, etc.)
            - arms: Ejercicios para brazos en general
            - only_triceps: Ejercicios específicamente para tríceps
            - only_biceps: Ejercicios específicamente para bíceps
            - abs: Ejercicios para abdominales
            - core: Ejercicios para el núcleo (abdominales, oblicuos, espalda baja)
            - full_body: Entrenamiento de cuerpo completo
            - cardio: Ejercicios cardiovasculares
            """
        )
    ]
    category: Annotated[
        Category,
        Field(
            description="""
            La categoría del entrenamiento basada en las repeticiones, peso y tipo de ejercicios:
            - strength: Fuerza (típicamente 1-5 repeticiones con peso alto)
            - hypertrophy: Hipertrofia o crecimiento muscular (típicamente 6-15 repeticiones con peso moderado)
            """
        )
    ]
