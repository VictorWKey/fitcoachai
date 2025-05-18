from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import enum

from ..base import Base

class WeightUnit(enum.Enum):
    KG = "kg"
    LB = "lb"

class ExerciseLog(Base):
    __tablename__ = "exercise_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_name = Column(String, nullable=True)
    set_number = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    weight_unit = Column(Enum(WeightUnit), nullable=True)  # <- Nueva columna
    rir = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    exercise_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workout = relationship("Workout", back_populates="exercise_logs")
    user = relationship("User", back_populates="exercise_logs")
    
    __table_args__ = (
        Index("idx_user_exercise_date", "user_id", "exercise_date"),
    )  
    
