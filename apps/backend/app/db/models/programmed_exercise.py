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

class BlockType(enum.Enum):
    """
    Enumeration of exercise block types.
    
    Attributes:
        MAIN: Main exercises (e.g., squat, bench press, deadlift)
        ACCESSORY: Accessory exercises (e.g., leg press, chest flies)
    """
    MAIN = "main"
    ACCESSORY = "accessory"

class ProgrammedExercise(Base):
    """
    Programmed Exercise model for the FitCoach AI application.
    
    Attributes:
        id: Unique identifier for the programmed exercise
        session_id: ID of the training session to which this exercise belongs
        standard_exercise_id: ID of the standard exercise (optional)
        block: Type of block - "main" or "accessory" (replaces exercise_block table)
        tempo: Exercise tempo
        sets: Number of sets
        reps: Number of repetitions
        load_type: Type of load (RPE, percentage, weight)
        rpe_target: Target RPE value
        percentage_1rm: Percentage of 1RM
        weight_range: Range of weight (e.g., "225-235")
        rest_seconds: Rest time in seconds
        sets_type: Type of sets (strength, hypertrophy, technique)
        notes: Optional notes
        created_at: Creation date of the record
        updated_at: Date of the last update to the record
        
    Relationships:
        training_session: Relationship with the parent training session
        standard_exercise: Relationship with the standard exercise definition
        exercise_logs: Relationship with strength logs
        cardio_logs: Relationship with cardio logs
    """
    __tablename__ = "programmed_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)
    standard_exercise_id = Column(Integer, ForeignKey("standard_exercise.id"), nullable=True)
    
    # Block type (replaces exercise_block table)
    block = Column(Enum(BlockType), nullable=False)
    
    # Exercise order within the session (0, 1, 2, 3...)
    exercise_order = Column(Integer, nullable=False, default=0)
    
    # Exercise properties
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
    training_session = relationship("TrainingSession", back_populates="programmed_exercises")
    standard_exercise = relationship("StandardExercise", back_populates="programmed_exercises")
    exercise_logs = relationship("StrengthLog", back_populates="programmed_exercise")
    cardio_logs = relationship("CardioLog", back_populates="programmed_exercise")
    
    def __repr__(self):
        """String representation of the programmed exercise."""
        return f"<ProgrammedExercise {self.id}: {self.block}>"
    
    def __repr__(self):
        """String representation of the programmed exercise."""
        return f"<ProgrammedExercise {self.id}>"