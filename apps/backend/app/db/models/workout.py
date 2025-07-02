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

class TrainingDiscipline(enum.Enum):
    """
    Disciplinas de entrenamiento disponibles.
    
    Attributes:
        MAX_STRENGTH: Entrenamiento de fuerza máxima/powerlifting
        HYPERTROPHY: Entrenamiento de hipertrofia/culturismo
        FLEXIBILITY: Entrenamiento de flexibilidad/mobility
        CARDIO: Entrenamiento cardiovascular
    """
    MAX_STRENGTH = "max_strength"
    HYPERTROPHY = "hypertrophy"
    FLEXIBILITY = "flexibility"
    CARDIO = "cardio"

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
    


class Workout(Base):
    """
    Workout model for the FitCoach AI application.
    
    Attributes:
        id: Unique identifier for the workout
        user_id: ID of the user who owns the workout
        discipline: Training discipline (max_strength, hypertrophy, cardio, etc.)
        muscle_group: Main muscle group of the workout
        is_finished: Indicates if the workout has been finished
        start_time: Start date and time of the workout
        created_at: Creation date of the record
        updated_at: Date of the last update to the record
        
    Relationships:
        user: Relationship with the user who owns the workout
        [discipline]_logs: Relationships with specific discipline exercise logs
    """
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    discipline = Column(Enum(TrainingDiscipline), nullable=False)
    muscle_group = Column(Enum(MuscleGroup), nullable=False, default=MuscleGroup.FULL_BODY)
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
    
    # Fitness discipline relationships - each workout can have logs from multiple disciplines
    # but typically will focus on one primary discipline
    max_strength_logs = relationship("MaxStrengthLog", back_populates="workout", cascade="all, delete-orphan")
    hypertrophy_logs = relationship("HypertrophyLog", back_populates="workout", cascade="all, delete-orphan")
    flexibility_logs = relationship("FlexibilityLog", back_populates="workout", cascade="all, delete-orphan")
    cardio_logs = relationship("CardioLog", back_populates="workout", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation of the workout."""
        return f"<Workout {self.id} - {self.discipline.value} - {self.created_at.date()}>"



    def get_all_exercise_logs(self):
        """
        Returns all exercise logs from all disciplines for this workout.
        
        Returns:
            List: All exercise logs associated with this workout
        """
        all_logs = []
        all_logs.extend(self.max_strength_logs)
        all_logs.extend(self.hypertrophy_logs)
        all_logs.extend(self.flexibility_logs)
        all_logs.extend(self.cardio_logs)
        
        # Sort by exercise_date if available
        return sorted(all_logs, key=lambda x: x.exercise_date if hasattr(x, 'exercise_date') else x.created_at)

