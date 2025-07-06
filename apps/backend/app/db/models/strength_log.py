"""
ORM model for the exercise logs table.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import Index
import enum

from ..base import Base

class WeightUnit(enum.Enum):
    """
    Enumeration of weight units for exercises.
    
    Attributes:
        KG: Kilograms
        LB: Pounds
    """
    KG = "kg"
    LB = "lb"

class ExerciseType(enum.Enum):
    """
    Enumeration of exercise categories.
    """
    STRENGTH = "strength"
    HIPERTROPHY = "hypertrophy"
    TECHNIQUE = "technique"

class StrengthLog(Base):
    """
    Model for recording exercises performed during a workout about strength or hypertrophy.
    
    Attributes:
        id: Unique identifier for the exercise log
        user_id: ID of the user who performed the exercise
        workout_id: ID of the workout to which the exercise belongs
        exercise_name: Name of the exercise performed
        set_number: Set number within the exercise
        reps: Number of repetitions performed
        weight: Weight used in the exercise
        weight_unit: Weight unit (kg or lb)
        rir: Reps in Reserve (RIR)
        notes: Notes or comments about the exercise
        exercise_date: Date and time when the exercise was performed
        updated_at: Date of the last update to the record
        
    Relationships:
        workout: Relationship with the workout to which it belongs
        user: Relationship with the user who performed the exercise
    """
    __tablename__ = "exercise_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_name = Column(String, nullable=True)
    exercise_type = Column(Enum(ExerciseType), nullable=True)
    set_number = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    weight_unit = Column(Enum(WeightUnit), nullable=True)
    one_rm_percentage = Column(Float, nullable=True)  # 30-120%
    rir = Column(Integer, nullable=True)
    rpe = Column(Float, nullable=True)  # 1-10 scale
    tempo = Column(String, nullable=True)  # Format: "E-B-C-T" (eccentric-bottom-concentric-top)
    rest_time_seconds = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    exercise_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    workout = relationship("Workout", back_populates="exercise_logs")
    user = relationship("User", back_populates="exercise_logs")
    
    __table_args__ = (
        Index("idx_user_exercise_date", "user_id", "exercise_date"),
    )
    
    def __repr__(self):
        """String representation of the exercise log."""
        return f"<ExerciseLog {self.id}: {self.exercise_name}>"
    
