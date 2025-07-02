"""
ORM model for the users table.
Defines the structure and relationships of users in the database.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..base import Base
from .workout import TrainingDiscipline

class User(Base):
    """
    User model for the FitCoach AI application.
    
    Attributes:
        id: Unique identifier for the user
        username: Unique username
        email: Unique email address
        hashed_password: Hashed password (never stored in plain text)
        full_name: User's full name
        is_active: Indicates if the account is active
        is_verified: Indicates if the email has been verified
        has_chat_history: Indicates if the user has started their first chat conversation
        system_message_needs_update: Indicates if the system message needs to be updated
        verification_token: Token for email verification
        verification_token_expires: Expiration date of the verification token
        reset_password_token: Token for password reset
        reset_password_expires: Expiration date of the reset token
        failed_login_attempts: Counter for failed login attempts
        last_failed_login: Date of the last failed login attempt
        account_locked_until: Date until which the account is locked
        created_at: User creation date
        updated_at: Date of the last update to the user
        
    Relationships:
        workouts: Relationship with user's workouts
        exercise_logs: Relationship with user's exercise logs
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    preferred_discipline = Column(Enum(TrainingDiscipline), default=TrainingDiscipline.HYPERTROPHY, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    has_chat_history = Column(Boolean, default=False, nullable=False)
    system_message_needs_update = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(DateTime(timezone=True), nullable=True)
    reset_password_token = Column(String, nullable=True)
    reset_password_expires = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime(timezone=True), nullable=True)
    account_locked_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    
    # Fitness discipline relationships
    max_strength_logs = relationship("MaxStrengthLog", back_populates="user", cascade="all, delete-orphan")
    hypertrophy_logs = relationship("HypertrophyLog", back_populates="user", cascade="all, delete-orphan")
    flexibility_logs = relationship("FlexibilityLog", back_populates="user", cascade="all, delete-orphan")
    cardio_logs = relationship("CardioLog", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation of the user."""
        return f"<User {self.username}>"
