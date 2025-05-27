from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class MuscleGroup(str, Enum):
    CHEST = "chest"
    BACK = "back"
    LEGS_IN_GENERAL = "legs_in_general"
    LEGS_CUADRICEPS_ENPHASIS = "legs_cuadriceps_enphasis"
    LEGS_HAMSTRINGS_ENPHASIS = "legs_hamstrings_enphasis"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    ONLY_TRICEPS = "only_triceps"
    ONLY_BICEPS = "only_biceps"
    ABS = "abs"
    CORE = "core"
    FULL_BODY = "full_body"
    CARDIO = "cardio"
    
class Category(str, Enum):
    HYPERTROPHY = "hypertrophy"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    BALANCE = "balance"
    FLEXIBILITY = "flexibility"
    COORDINATION = "coordination"
    POWER = "power"

# Base
class WorkoutBase(BaseModel):
    muscle_group: MuscleGroup
    category: Category
# Crear
class WorkoutCreate(WorkoutBase):
    user_id: int
    start_time: Optional[datetime] = None  

# Actualizar
class WorkoutUpdate(BaseModel):
    muscle_group: Optional[MuscleGroup] = None
    category: Optional[Category] = None
    start_time: Optional[datetime] = None
    
# Respuesta
class Workout(WorkoutBase):
    id: int
    user_id: int
    start_time: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
