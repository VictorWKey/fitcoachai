"""
ORM model for the users table.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..base import Base

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
        exercise_logs: Relationship with user's strength exercise logs
        cardio_logs: Relationship with user's cardio exercise logs
        training_programs: Relationship with user's training programs
        active_training_sessions: Relationship with training sessions currently being executed by the user
        chat_history: Relationship with user's chat history
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
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
    exercise_logs = relationship("StrengthLog", back_populates="user", cascade="all, delete-orphan")
    cardio_logs = relationship("CardioLog", back_populates="user", cascade="all, delete-orphan")
    training_programs = relationship("TrainingProgram", back_populates="user", cascade="all, delete-orphan")
    active_training_sessions = relationship("TrainingSession", back_populates="user")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        """String representation of the user."""
        return f"<User {self.username}>"
