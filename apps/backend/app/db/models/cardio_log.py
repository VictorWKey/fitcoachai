"""
Cardio training model.
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import enum

from ..base import Base

class DistanceUnit(enum.Enum):
    """
    Enumeration of distance units for cardio exercises.
    
    Attributes:
        KM: Kilometers
        MI: Miles
    """
    KM = "km"
    MI = "mi"

class CardioType(enum.Enum):
    """
    Enumeration of cardio training types.
    
    Attributes:
        HIIT: High-Intensity Interval Training (includes Tabata)
        STEADY_STATE: Constant intensity cardio (includes LISS and MISS)
    """
    HIIT = "hiit"
    STEADY_STATE = "steady_state"

class CardioLog(Base):
    """
    Model for recording cardio training sessions as complementary work for strength/hypertrophy athletes.
    """
    __tablename__ = "cardio_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_name = Column(String, nullable=False)  # Treadmill, bike, elliptical, rowing, etc.
    cardio_type = Column(Enum(CardioType), nullable=False)
    total_duration_seconds = Column(Integer, nullable=False)
    distance = Column(Float, nullable=True)
    distance_unit = Column(Enum(DistanceUnit), default=DistanceUnit.KM, nullable=True)
    calories_burned = Column(Integer, nullable=True)
    avg_heart_rate = Column(Integer, nullable=True)
    avg_rpe = Column(Float, nullable=True)  # 1-10 scale
    
    # Campos optimizados para equipos de gimnasio
    intensity_level = Column(Integer, nullable=True)  # Nivel de velocidad/resistencia (1-20 típicamente)
    incline_level = Column(Integer, nullable=True)  # Nivel de inclinación en máquinas (0-15 típicamente)
    
    notes = Column(Text, nullable=True)
    exercise_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workout = relationship("Workout", back_populates="cardio_logs")
    user = relationship("User", back_populates="cardio_logs")
    
    __table_args__ = (
        Index("idx_cardio_user_date", "user_id", "exercise_date"),
    ) 