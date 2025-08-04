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

class SetType(enum.Enum):
    """
    Enumeration of exercise set types.
    """
    STRENGTH = "strength"
    HIPERTROPHY = "hypertrophy"
    TECHNIQUE = "technique"

class StrengthLog(Base):
    """
    Model for recording exercises performed during a training session.
    
    Attributes:
        id: Unique identifier for the exercise log
        user_id: ID of the user who performed the exercise
        training_session_id: ID of the training session to which this log belongs
        programmed_exercise_id: ID of the programmed exercise (if this log is part of a training program)
        standard_exercise_id: ID of the standard exercise from the exercise database
        set_number: Set number within the exercise
        set_type: Type of set (strength, hypertrophy, technique)
        repetitions_done: Number of repetitions performed
        used_weight: Weight used in the exercise
        used_weight_unit: Weight unit (kg or lb)
        perceived_rir: Reps in Reserve (RIR) perceived by the user
        perceived_rpe: Rate of Perceived Exertion (RPE)
        tempo: Tempo of the exercise (format: "E-B-C-T")
        rest_time_seconds: Rest time taken after this set
        notes: Notes or comments about the exercise
        exercise_date: Date and time when the exercise was performed
        updated_at: Date of the last update to the record
        
    Relationships:
        training_session: Relationship with the training session to which it belongs
        user: Relationship with the user who performed the exercise
        standard_exercise: Relationship with the standard exercise from the database
        programmed_exercise: Relationship with the programmed exercise (if part of a program)
    """
    __tablename__ = "strength_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    training_session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)
    standard_exercise_id = Column(Integer, ForeignKey("standard_exercise.id"), nullable=False)
    programmed_exercise_id = Column(Integer, ForeignKey("programmed_exercises.id"), nullable=True)
    set_number = Column(Integer, nullable=False)
    set_type = Column(Enum(SetType), nullable=True)
    repetitions_done = Column(Integer, nullable=False)
    used_weight = Column(Float, nullable=False)
    used_weight_unit = Column(Enum(WeightUnit), nullable=False)
    perceived_rir = Column(Integer, nullable=True)
    perceived_rpe = Column(Float, nullable=True)  
    tempo = Column(String, nullable=True)  # Format: "E-B-C-T" (eccentric-bottom-concentric-top)
    rest_time_seconds = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    exercise_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    training_session = relationship("TrainingSession", back_populates="strength_logs")
    user = relationship("User", back_populates="exercise_logs")
    standard_exercise = relationship("StandardExercise", back_populates="exercise_logs")
    programmed_exercise = relationship("ProgrammedExercise", back_populates="exercise_logs")
    
    __table_args__ = (
        Index("idx_user_exercise_date", "user_id", "exercise_date"),
    )
    
    def __repr__(self):
        """String representation of the strength log."""
        return f"<StrengthLog {self.id}>"

