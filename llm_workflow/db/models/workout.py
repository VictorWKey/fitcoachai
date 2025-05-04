from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from ..base import Base

class MuscleGroup(enum.Enum):
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
    HYPERTROPHY = "hypertrophy"
    STRENGTH = "strength"
    ENDURANCE = "endurance"
    BALANCE = "balance"
    FLEXIBILITY = "flexibility"
    COORDINATION = "coordination"
    POWER = "power"

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    muscle_group = Column(Enum(MuscleGroup), nullable=False)
    category = Column(Enum(Category), nullable=False)

    start_time = Column(
        DateTime(timezone=True), 
        nullable=False, default=
        datetime.now(datetime.UTC)
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
    
    # Relaciones
    user = relationship("User", back_populates="workouts")
    exercise_logs = relationship("ExerciseLog", back_populates="workout", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Workout {self.id} - {self.created_at.date()}>"

