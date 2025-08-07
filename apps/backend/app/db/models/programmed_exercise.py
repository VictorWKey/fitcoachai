"""
ORM model for the programmed exercises table.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..base import Base
from db.models.strength_log import SetType

class LoadType(enum.Enum):
    """
    Enumeration of load types for programmed exercises.
    
    Attributes:
        RPE: Rate of Perceived Exertion
        PERCENTAGE: Percentage of 1 Rep Max
        WEIGHT: Absolute weight
    """
    RPE = "rpe"
    PERCENTAGE = "percentage"
    WEIGHT = "weight"

class ProgrammedExercise(Base):
    """
    Programmed Exercise model for the FitCoach AI application.
    
    Attributes:
        id: Unique identifier for the programmed exercise
        block_id: ID of the exercise block to which this exercise belongs
        exercise_name: Name of the exercise
        standard_exercise_id: ID of the standard exercise (optional)
        variation: Optional variation of the exercise (e.g., "Tempo", "1 Ct Paused")
        sets: Number of sets
        reps: Number of repetitions
        load_type: Type of load (RPE, percentage, weight)
        load_value: Value of the load (e.g., "8" for RPE, "-15%" for percentage)
        rpe_target: Target RPE value
        percentage_1rm: Percentage of 1RM
        weight_range: Range of weight (e.g., "225-235")
        rest_seconds: Rest time in seconds
        exercise_type: Type of exercise (strength, hypertrophy, technique)
        created_at: Creation date of the record
        updated_at: Date of the last update to the record
        
    Relationships:
        exercise_block: Relationship with the parent exercise block
        standard_exercise: Relationship with the standard exercise definition
    """
    __tablename__ = "programmed_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(Integer, ForeignKey("exercise_blocks.id"), nullable=False)
    standard_exercise_id = Column(Integer, ForeignKey("standard_exercise.id"), nullable=True)
    tempo = Column(String, nullable=True)  # Format: "E-B-C-T" (eccentric-bottom-concentric-top)
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    load_type = Column(Enum(LoadType), nullable=True)
    rpe_target = Column(Float, nullable=True)
    percentage_1rm = Column(Float, nullable=True)
    weight_range = Column(String, nullable=True)
    rest_seconds = Column(Integer, nullable=True)
    sets_type = Column(Enum(SetType), nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    exercise_block = relationship("ExerciseBlock", back_populates="programmed_exercises")
    standard_exercise = relationship("StandardExercise", back_populates="programmed_exercises")
    exercise_logs = relationship("StrengthLog", back_populates="programmed_exercise")
    
    def __repr__(self):
        """String representation of the programmed exercise."""
        return f"<ProgrammedExercise {self.id}>"