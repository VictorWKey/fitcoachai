"""
Base interface and mixins for all exercise logs.
Provides common functionality and protocols that all discipline exercise logs must implement.
"""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from datetime import datetime

@runtime_checkable
class ExerciseLogProtocol(Protocol):
    """Protocol that all exercise log models must implement."""
    id: int
    user_id: int
    workout_id: int
    exercise_name: str
    exercise_date: datetime
    updated_at: datetime
    notes: str | None

class BaseExerciseLogMixin:
    """Mixin with common methods for all exercise log models."""
    
    def get_common_fields(self) -> dict:
        """Returns dictionary with fields common to all exercise logs."""
        return {
            "id": getattr(self, 'id'),
            "user_id": getattr(self, 'user_id'),
            "workout_id": getattr(self, 'workout_id'),
            "exercise_name": getattr(self, 'exercise_name'),
            "exercise_date": getattr(self, 'exercise_date'),
            "updated_at": getattr(self, 'updated_at'),
            "notes": getattr(self, 'notes', None)
        }
    
    def get_discipline_name(self) -> str:
        """Returns the discipline name based on table name."""
        return getattr(self, '__tablename__', '').replace('_logs', '')
    
    def to_dict(self) -> dict:
        """Convert the exercise log to a dictionary with common fields."""
        base_dict = self.get_common_fields()
        base_dict["discipline"] = self.get_discipline_name()
        
        # Add discipline-specific fields dynamically
        for attr_name in dir(self):
            if not attr_name.startswith('_') and attr_name not in base_dict:
                attr_value = getattr(self, attr_name, None)
                # Only include simple types, not relationships or methods
                if not callable(attr_value) and not hasattr(attr_value, '_sa_instance_state'):
                    # Handle enum values
                    if attr_value is not None and hasattr(attr_value, 'value'):
                        base_dict[attr_name] = attr_value.value
                    else:
                        base_dict[attr_name] = attr_value
        
        return base_dict 