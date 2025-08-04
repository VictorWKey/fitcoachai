"""
ORM model for the exercise blocks table.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..base import Base
from db.models.standard_exercises import MuscleGroupEnum

class BlockType(enum.Enum):
    """
    Enumeration of exercise block types.
    
    Attributes:
        MAIN: Main exercises (e.g., squat, bench press, deadlift)
        ACCESSORY: Accessory exercises (e.g., leg press, chest flies)
    """
    MAIN = "main"
    ACCESSORY = "accessory"

class ExerciseBlock(Base):
    """
    Exercise Block model for the FitCoach AI application.
    
    Attributes:
        id: Unique identifier for the exercise block
        session_id: ID of the training session to which this block belongs
        name: Name of the block (e.g., "#1 Squat", "#2 Bench")
        block_type: Type of block (main or accessory)
        order: Order of the block within the session
        primary_muscle_group: Primary muscle group targeted by this block
        description: Optional description of the block
        created_at: Creation date of the record
        updated_at: Date of the last update to the record
        
    Relationships:
        training_session: Relationship with the parent training session
        programmed_exercises: Relationship with the exercises that make up the block
    """
    __tablename__ = "exercise_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)
    name = Column(String, nullable=False)
    block_type = Column(Enum(BlockType), nullable=False)
    order = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    training_session = relationship("TrainingSession", back_populates="exercise_blocks")
    programmed_exercises = relationship("ProgrammedExercise", back_populates="exercise_block", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of the exercise block."""
        return f"<ExerciseBlock {self.id}: {self.name}>"