"""
Flexibility training model.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from ...base import Base
from .common import StretchType
from .base import BaseExerciseLogMixin

class FlexibilityLog(Base, BaseExerciseLogMixin):
    """
    Model for recording flexibility and mobility sessions (stretching, yoga).
    """
    __tablename__ = "flexibility_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    joint_name = Column(String, nullable=False)
    rom_degrees = Column(Float, nullable=True)  # 0-360 degrees
    stretch_time_seconds = Column(Integer, nullable=False)
    intensity_scale = Column(Float, nullable=True)  # 1-10 scale
    stretch_type = Column(Enum(StretchType), nullable=True)
    pain_level = Column(Float, nullable=True)  # 0-10 scale
    pre_session_feeling = Column(String, nullable=True)
    post_session_feeling = Column(String, nullable=True)
    improvement_percentage = Column(Float, nullable=True)  # -90 to +500%
    ambient_temperature = Column(Float, nullable=True)
    body_temperature_feeling = Column(String, nullable=True)  # cold, warm, hot
    notes = Column(Text, nullable=True)
    exercise_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workout = relationship("Workout", back_populates="flexibility_logs")
    user = relationship("User", back_populates="flexibility_logs")
    
    __table_args__ = (
        Index("idx_flexibility_user_date", "user_id", "exercise_date"),
    ) 