from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime
from db.models.workout import MuscleGroup, TrainingDiscipline

class WorkoutBase(BaseModel):
    discipline: TrainingDiscipline
    muscle_group: MuscleGroup = MuscleGroup.FULL_BODY
    is_finished: bool = False

class WorkoutCreate(WorkoutBase):
    user_id: int
    start_time: Optional[datetime] = None  

class WorkoutUpdate(BaseModel):
    discipline: Optional[TrainingDiscipline] = None
    muscle_group: Optional[MuscleGroup] = None
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

# Schema for initializing workouts
class InitWorkout(BaseModel):
    """Schema for initializing a new workout with discipline."""
    discipline: TrainingDiscipline = Field(
        description="Disciplina de entrenamiento para el workout"
    )

