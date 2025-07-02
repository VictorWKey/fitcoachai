"""
Base schemas for exercise logs.
Provides common response models and Union types for API responses.
"""

from typing import Union, Any, Dict
from datetime import datetime
from pydantic import BaseModel

# Import all discipline log schemas
from .hypertrophy import HypertrophyLog
from .max_strength import MaxStrengthLog
from .flexibility import FlexibilityLog
from .cardio import CardioLog

class BaseExerciseLogResponse(BaseModel):
    """Base response model for exercise logs with common fields."""
    id: int
    user_id: int
    workout_id: int
    exercise_name: str
    exercise_date: datetime
    updated_at: datetime
    discipline: str
    notes: str | None = None

    class Config:
        from_attributes = True

# Union type for all exercise log responses
ExerciseLogResponse = Union[
    HypertrophyLog,
    MaxStrengthLog, 
    FlexibilityLog,
    CardioLog
]

# Dictionary response for when we need a common format
class ExerciseLogDict(BaseModel):
    """Dictionary-style response for exercise logs."""
    data: Dict[str, Any]
    discipline: str
    
    class Config:
        from_attributes = True 