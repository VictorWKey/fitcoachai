"""
ORM model for the training sessions table.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from ..base import Base

class SessionStatus(enum.Enum):
    """
    Enumeration of training session statuses.
    
    Attributes:
        PENDING: Sesión creada pero no iniciada por el usuario
        ACTIVE: Usuario activamente entrenando (timer corriendo en frontend)
        COMPLETED: Terminada exitosamente
        ABANDONED: No finalizada (app cerrada durante entrenamiento)
    """
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class TrainingSession(Base):
    """
    Training Session model for the FitCoach AI application.
    
    Attributes:
        id: Unique identifier for the training session
        week_id: ID of the training week to which this session belongs
        name: Name of the session (e.g., "Squat Day", "Bench Day")
        day_of_week: Day of the week (1-7 for Monday-Sunday, nullable for flexibility)
        session_order: Sequential order within program (0,1,2,3...)
        description: Optional description of the session
        
        # Session execution state (per user instance)
        user_id: ID of the user currently executing this session (nullable)
        session_status: Current status (active, completed, abandoned)
        session_start_time: When the user started executing this session
        session_end_time: When the user finished executing this session
        session_duration_seconds: Total duration calculated by frontend timer
        session_completion_percentage: 0-100% completion of the session
        last_activity: Last time user performed any action in this session
        
        # Computed properties:
        session_status: Current status (pending, active, completed, abandoned)
        is_session_pending: Whether this session is pending (not started yet)
        is_session_active: Whether this session is currently active
        is_session_completed: Whether this session is completed
        is_session_finished: Whether this session is finished (completed or abandoned)
        
        created_at: Creation date of the record
        updated_at: Date of the last update to the record
        
    Relationships:
        training_week: Relationship with the parent training week
        exercise_blocks: Relationship with the exercise blocks that make up the session
        strength_logs: Relationship with strength exercise logs recorded during this session
        cardio_logs: Relationship with cardio exercise logs recorded during this session
        user: Relationship with the user currently executing this session
    """
    __tablename__ = "training_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("training_weeks.id"), nullable=False)
    name = Column(String, nullable=False)
    day_of_week = Column(Integer, nullable=True)  # 1-7 for Monday-Sunday, nullable for flexibility
    session_order = Column(Integer, nullable=False)  # Sequential order within program (0,1,2,3...)
    description = Column(String, nullable=True)
    
    # Session execution state (per user instance)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User currently executing this session
    session_start_time = Column(DateTime(timezone=True), nullable=True)  # When user started the session
    session_end_time = Column(DateTime(timezone=True), nullable=True)    # When user finished the session
    session_duration_seconds = Column(Integer, nullable=True)             # Total duration from frontend timer
    session_completion_percentage = Column(Integer, default=0, nullable=False)  # 0-100% completion
    
    # Session status management
    session_status = Column(Enum(SessionStatus), default=SessionStatus.PENDING, nullable=False)  # Current status
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Last user activity
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    training_week = relationship("TrainingWeek", back_populates="training_sessions")
    exercise_blocks = relationship("ExerciseBlock", back_populates="training_session", cascade="all, delete-orphan")
    strength_logs = relationship("StrengthLog", back_populates="training_session", cascade="all, delete-orphan")
    cardio_logs = relationship("CardioLog", back_populates="training_session", cascade="all, delete-orphan")
    user = relationship("User", back_populates="active_training_sessions")
    
    # Computed properties for backward compatibility and convenience
    @property
    def is_session_pending(self):
        """Check if the session is pending (not started yet)."""
        return self.session_status == SessionStatus.PENDING
    
    @property
    def is_session_active(self):
        """Check if the session is currently active."""
        return self.session_status == SessionStatus.ACTIVE
    
    @property
    def is_session_completed(self):
        """Check if the session is completed successfully."""
        return self.session_status == SessionStatus.COMPLETED
    
    @property
    def is_session_finished(self):
        """Check if the session is finished (completed or abandoned)."""
        return self.session_status in [SessionStatus.COMPLETED, SessionStatus.ABANDONED]
    
    def __repr__(self):
        """String representation of the training session."""
        return f"<TrainingSession {self.id}: {self.name}>"