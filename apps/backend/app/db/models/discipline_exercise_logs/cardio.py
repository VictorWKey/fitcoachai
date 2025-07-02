"""
Cardio training model.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Index

from ...base import Base
from .base import BaseExerciseLogMixin

class CardioLog(Base, BaseExerciseLogMixin):
    """
    Model for recording cardio training sessions (HIIT, LISS, spinning).
    """
    __tablename__ = "cardio_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    cardio_type = Column(String, nullable=False)  # HIIT, LISS, spinning
    total_duration_seconds = Column(Integer, nullable=False)
    intervals_completed = Column(Integer, nullable=True)
    work_rest_ratio = Column(String, nullable=True)  # "1:1", "1:2", "3:1", etc.
    avg_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)
    heart_rate_zones = Column(String, nullable=True)  # JSON string
    estimated_calories = Column(Integer, nullable=True)
    avg_power_watts = Column(Float, nullable=True)
    max_power_watts = Column(Float, nullable=True)
    avg_rpe = Column(Float, nullable=True)  # 1-10 scale
    avg_cadence = Column(Integer, nullable=True)
    resistance_level = Column(Integer, nullable=True)  # 0-100
    avg_speed_kmh = Column(Float, nullable=True)
    interval_rpe_data = Column(Text, nullable=True)  # JSON string of RPE per interval
    notes = Column(Text, nullable=True)
    exercise_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workout = relationship("Workout", back_populates="cardio_logs")
    user = relationship("User", back_populates="cardio_logs")
    
    __table_args__ = (
        Index("idx_cardio_user_date", "user_id", "exercise_date"),
    ) 