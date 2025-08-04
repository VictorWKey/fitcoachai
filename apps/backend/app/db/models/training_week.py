"""
ORM model for the training weeks table.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base

class TrainingWeek(Base):
    """
    Training Week model for the FitCoach AI application.
    
    Attributes:
        id: Unique identifier for the training week
        program_id: ID of the training program to which this week belongs
        week_number: Number of the week within the program (1, 2, 3, etc.)
        description: Optional description of the week
        created_at: Creation date of the record
        updated_at: Date of the last update to the record
        
    Relationships:
        training_program: Relationship with the parent training program
        training_sessions: Relationship with the sessions that make up the week
    """
    __tablename__ = "training_weeks"
    
    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("training_programs.id"), nullable=False)
    week_number = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    training_program = relationship("TrainingProgram", back_populates="training_weeks")
    training_sessions = relationship("TrainingSession", back_populates="training_week", cascade="all, delete-orphan")
    
    def __repr__(self):
        """String representation of the training week."""
        return f"<TrainingWeek {self.id}: Week {self.week_number} of Program {self.program_id}>" 