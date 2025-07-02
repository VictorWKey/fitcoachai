"""
Max strength training model.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from ...base import Base
from .common import WeightUnit
from .base import BaseExerciseLogMixin

class MaxStrengthLog(Base, BaseExerciseLogMixin):
    """
    Model for recording maximum strength training sessions (powerlifting, olympic).
    """
    __tablename__ = "max_strength_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)
    rpe = Column(Float, nullable=True)  # 1-10 scale
    rir = Column(Integer, nullable=True)  # 0-10+ reps in reserve
    rest_time_seconds = Column(Integer, nullable=True)  # 30-1200+ seconds
    one_rm_percentage = Column(Float, nullable=True)  # 30-120%
    exercise_type = Column(String, nullable=True)  # squat, bench, deadlift, etc.
    notes = Column(Text, nullable=True)
    tempo_eccentric = Column(Integer, nullable=True)  # seconds
    tempo_pause_bottom = Column(Integer, nullable=True)  # seconds
    tempo_concentric = Column(Integer, nullable=True)  # seconds
    exercise_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workout = relationship("Workout", back_populates="max_strength_logs")
    user = relationship("User", back_populates="max_strength_logs")
    
    __table_args__ = (
        Index("idx_max_strength_user_date", "user_id", "exercise_date"),
    ) 