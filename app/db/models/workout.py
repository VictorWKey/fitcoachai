"""
ORM model for the workouts table.
Defines the structure and relationships of workouts in the database.
"""

from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from ..base import Base

class MuscleGroup(enum.Enum):
    """
    Enumeration of muscle groups for workout classification.
    
    Attributes:
        CHEST: Chest
        BACK: Back
        LEGS_IN_GENERAL: Legs in general
        LEGS_CUADRICEPS_ENPHASIS: Legs with emphasis on quadriceps
        LEGS_HAMSTRINGS_ENPHASIS: Legs with emphasis on hamstrings
        SHOULDERS: Shoulders
        ARMS: Arms
        ONLY_TRICEPS: Only triceps
        ONLY_BICEPS: Only biceps
        ABS: Abdominals
        CORE: Core
        FULL_BODY: Full body
        CARDIO: Cardio
    """
    CHEST = "chest"
    BACK = "back"
    LEGS_IN_GENERAL = "legs_in_general"
    LEGS_CUADRICEPS_ENPHASIS = "legs_cuadriceps_enphasis"
    LEGS_HAMSTRINGS_ENPHASIS = "legs_hamstrings_enphasis"
    SHOULDERS = "shoulders"
    ARMS = "arms"
    ONLY_TRICEPS = "only_triceps"
    ONLY_BICEPS = "only_biceps"
    ABS = "abs"
    CORE = "core"
    FULL_BODY = "full_body"
    CARDIO = "cardio"
    
class Category(enum.Enum):
    """
    Enumeration of workout categories.
    
    Attributes:
        HYPERTROPHY: Hypertrophy (muscle growth)
        STRENGTH: Strength
        ENDURANCE: Endurance
        BALANCE: Balance
        FLEXIBILITY: Flexibility
        COORDINATION: Coordination
        POWER: Power
    """
    HYPERTROPHY = "hypertrophy"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    BALANCE = "balance"
    FLEXIBILITY = "flexibility"
    COORDINATION = "coordination"
    POWER = "power"

class Workout(Base):
    """
    Workout model for the FitCoach AI application.
    
    Attributes:
        id: Unique identifier for the workout
        user_id: ID of the user who owns the workout
        muscle_group: Main muscle group of the workout
        category: Category of the workout (strength, hypertrophy, etc.)
        start_time: Start date and time of the workout
        is_finished: Indicates if the workout has been finished
        created_at: Creation date of the record
        updated_at: Date of the last update to the record
        
    Relationships:
        user: Relationship with the user who owns the workout
        exercise_logs: Relationship with the exercise logs of the workout
    """
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    muscle_group = Column(Enum(MuscleGroup), nullable=False)
    category = Column(Enum(Category), nullable=False)
    is_finished = Column(Boolean, default=False, nullable=False)

    start_time = Column(
        DateTime(timezone=True), 
        nullable=False, default=
        datetime.now(timezone.utc)
    )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # Relationships
    user = relationship("User", back_populates="workouts")
    exercise_logs = relationship("ExerciseLog", back_populates="workout", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation of the workout."""
        return f"<Workout {self.id} - {self.created_at.date()}>"

