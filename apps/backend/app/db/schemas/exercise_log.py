"""
Combined schema for both strength and cardio exercise logs.
"""

from pydantic import BaseModel, Field
from typing import Union, Optional, Literal
from datetime import datetime
from .strength_log import StrengthLog, WeightUnit
from .cardio_log import CardioLog


class ExerciseLogBase(BaseModel):
    """Base class for exercise logs with common fields."""
    exercise_name: Optional[str] = Field(None, description="Name of the exercise")
    notes: Optional[str] = Field(None, description="Additional notes")
    exercise_date: datetime = Field(description="Date and time when the exercise was performed")
    type: Literal["strength", "cardio"] = Field(description="Type of exercise")


class StrengthExerciseLog(ExerciseLogBase):
    """Strength exercise log with specific fields."""
    type: Literal["strength"] = "strength"
    set_number: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    weight_unit: Optional[WeightUnit] = None
    one_rm_percentage: Optional[float] = None
    rir: Optional[int] = None
    rpe: Optional[float] = None
    tempo_eccentric: Optional[int] = None
    tempo_pause_bottom: Optional[int] = None
    tempo_concentric: Optional[int] = None
    rest_time_seconds: Optional[int] = None

    @classmethod
    def from_strength_log(cls, strength_log: StrengthLog) -> "StrengthExerciseLog":
        """Convert a StrengthLog to StrengthExerciseLog."""
        return cls(
            exercise_name=strength_log.exercise_name,
            notes=strength_log.notes,
            exercise_date=strength_log.exercise_date,
            set_number=strength_log.set_number,
            reps=strength_log.reps,
            weight=strength_log.weight,
            weight_unit=strength_log.weight_unit,
            one_rm_percentage=strength_log.one_rm_percentage,
            rir=strength_log.rir,
            rpe=strength_log.rpe,
            tempo_eccentric=strength_log.tempo_eccentric,
            tempo_pause_bottom=strength_log.tempo_pause_bottom,
            tempo_concentric=strength_log.tempo_concentric,
            rest_time_seconds=strength_log.rest_time_seconds,
        )


class CardioExerciseLog(ExerciseLogBase):
    """Cardio exercise log with specific fields."""
    type: Literal["cardio"] = "cardio"
    cardio_type: Optional[str] = None
    total_duration_seconds: Optional[int] = None
    intervals_completed: Optional[int] = None
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    heart_rate_zones: Optional[str] = None
    avg_power_watts: Optional[float] = None
    max_power_watts: Optional[float] = None
    avg_rpe: Optional[float] = None
    avg_cadence: Optional[int] = None
    resistance_level: Optional[int] = None
    avg_speed_kmh: Optional[float] = None
    interval_rpe_data: Optional[str] = None

    @classmethod
    def from_cardio_log(cls, cardio_log: CardioLog) -> "CardioExerciseLog":
        """Convert a CardioLog to CardioExerciseLog."""
        return cls(
            exercise_name=cardio_log.exercise_name,
            notes=cardio_log.notes,
            exercise_date=cardio_log.exercise_date,
            cardio_type=cardio_log.cardio_type,
            total_duration_seconds=cardio_log.total_duration_seconds,
            intervals_completed=cardio_log.intervals_completed,
            avg_heart_rate=cardio_log.avg_heart_rate,
            max_heart_rate=cardio_log.max_heart_rate,
            heart_rate_zones=getattr(cardio_log, 'heart_rate_zones', None),
            avg_power_watts=cardio_log.avg_power_watts,
            max_power_watts=getattr(cardio_log, 'max_power_watts', None),
            avg_rpe=cardio_log.avg_rpe,
            avg_cadence=getattr(cardio_log, 'avg_cadence', None),
            resistance_level=getattr(cardio_log, 'resistance_level', None),
            avg_speed_kmh=getattr(cardio_log, 'avg_speed_kmh', None),
            interval_rpe_data=getattr(cardio_log, 'interval_rpe_data', None),
        )


# Union type for exercise logs
ExerciseLog = Union[StrengthExerciseLog, CardioExerciseLog]


def convert_to_exercise_log(log) -> ExerciseLog:
    """Convert a database log to an ExerciseLog schema."""
    # Check if it's a StrengthLog by looking for strength-specific attributes
    if hasattr(log, 'reps') or hasattr(log, 'weight'):
        return StrengthExerciseLog.from_strength_log(log)
    else:
        return CardioExerciseLog.from_cardio_log(log) 