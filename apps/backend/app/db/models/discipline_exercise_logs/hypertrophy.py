"""
Hypertrophy training model.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from ...base import Base
from .common import WeightUnit, RangeOfMotion
from .base import BaseExerciseLogMixin

class HypertrophyLog(Base, BaseExerciseLogMixin):
    """
    Model for recording hypertrophy training sessions (bodybuilding, fitness).
    """
    __tablename__ = "hypertrophy_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    set_number = Column(Integer, nullable=False)
    target_reps = Column(Integer, nullable=True)
    completed_reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    weight_unit = Column(Enum(WeightUnit), default=WeightUnit.KG)
    rpe = Column(Float, nullable=True)  # 1-10 scale
    rir = Column(Integer, nullable=True)  # 0-10+ reps in reserve
    tempo_eccentric = Column(Integer, nullable=True)  # seconds
    tempo_pause_bottom = Column(Integer, nullable=True)  # seconds
    tempo_concentric = Column(Integer, nullable=True)  # seconds
    rest_time_seconds = Column(Integer, nullable=True)
    range_of_motion = Column(Enum(RangeOfMotion), default=RangeOfMotion.FULL)
    target_muscle = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    exercise_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workout = relationship("Workout", back_populates="hypertrophy_logs")
    user = relationship("User", back_populates="hypertrophy_logs")
    
    __table_args__ = (
        Index("idx_hypertrophy_user_date", "user_id", "exercise_date"),
    ) 