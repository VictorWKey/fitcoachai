from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime
from db.models.workout import MuscleGroup, Category

class WorkoutBase(BaseModel):
    muscle_group: MuscleGroup
    category: Category
    is_finished: bool = False

class WorkoutCreate(WorkoutBase):
    user_id: int
    start_time: Optional[datetime] = None  

class WorkoutUpdate(BaseModel):
    muscle_group: Optional[MuscleGroup] = None
    category: Optional[Category] = None
    start_time: Optional[datetime] = None
    is_finished: Optional[bool] = None
    
# Response
class Workout(WorkoutBase):
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
    Schema para inferir el tipo de entrenamiento basado en ejercicios.
    Usado por el LLM para determinar grupo muscular y categoría.
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
            - hypertrophy: Hipertrofia o crecimiento muscular (típicamente 6-12 repeticiones con peso moderado)
            - endurance: Resistencia muscular (típicamente más de 12 repeticiones con peso bajo)
            - balance: Ejercicios de equilibrio
            - flexibility: Ejercicios de flexibilidad o estiramiento
            - coordination: Ejercicios que enfatizan la coordinación
            - power: Ejercicios de potencia (movimientos explosivos)
            """
        )
    ]
