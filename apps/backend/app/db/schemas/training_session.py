"""
Training session schemas for the FitCoach AI application.

This module contains Pydantic schemas for training session management including:
- Base schema with session metadata 
- Create schema for creating new training sessions
- Update schema for modifying existing training sessions
- Response schema for returning session data
- Session status schemas for tracking progress

All schemas support the session-based training system.
"""

from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List
from datetime import datetime
from db.models.training_session import SessionStatus

class TrainingSessionBase(BaseModel):
    """
    Base schema for training session data.
    
    Contains common session metadata fields.
    """
    name: str = Field(..., description="Name of the training session")
    day_of_week: Optional[int] = Field(None, description="Day of the week (1-7 for Monday-Sunday)")
    session_order: int = Field(..., description="Sequential order within program")
    description: Optional[str] = Field(None, description="Optional description of the session")

class TrainingSessionCreate(TrainingSessionBase):
    """
    Schema for creating a new training session.
    
    Extends the base schema with required week identification.
    """
    week_id: int = Field(..., description="ID of the training week this session belongs to")

class TrainingSessionUpdate(BaseModel):
    """
    Schema for updating an existing training session.
    
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = None
    day_of_week: Optional[int] = None
    session_order: Optional[int] = None
    description: Optional[str] = None

class TrainingSessionStatus(BaseModel):
    """
    Schema for training session execution status.
    
    Contains fields for tracking session progress and state.
    """
    session_status: SessionStatus = Field(default=SessionStatus.PENDING, description="Current status of the session")
    session_start_time: Optional[datetime] = Field(None, description="When the session was started")
    session_end_time: Optional[datetime] = Field(None, description="When the session was finished")
    session_duration_seconds: Optional[int] = Field(None, description="Total session duration from frontend timer")
    session_completion_percentage: int = Field(default=0, description="Completion percentage (0-100)")
    user_id: Optional[int] = Field(None, description="ID of user currently executing the session")
    last_activity: Optional[datetime] = Field(None, description="Last time user performed any action")

class TrainingSession(TrainingSessionBase):
    """
    Schema for training session response data.
    
    Includes database-generated fields like ID and timestamps.
    """
    id: int
    week_id: int
    created_at: datetime
    updated_at: datetime
    
    # Session status fields
    session_status: str = "pending"
    session_start_time: Optional[datetime] = None
    session_end_time: Optional[datetime] = None
    session_duration_seconds: Optional[int] = None
    session_completion_percentage: int = 0
    user_id: Optional[int] = None
    last_activity: Optional[datetime] = None

    class Config:
        from_attributes = True

class TrainingSessionWithLogs(TrainingSession):
    """
    Schema for training session with exercise logs included.
    
    Includes related strength and cardio logs for detailed session view.
    """
    strength_logs_count: int = Field(default=0, description="Number of strength exercise logs")
    cardio_logs_count: int = Field(default=0, description="Number of cardio exercise logs")

class SessionSummary(BaseModel):
    """
    Schema for session completion summary.
    
    Contains metrics and summary information for completed sessions.
    """
    session_id: int
    session_name: str
    duration_seconds: Optional[int]
    strength_sets_count: int
    cardio_exercises_count: int
    completion_percentage: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class TrainingSessionListResponse(BaseModel):
    """
    Schema for simplified training session list response.
    
    Contains only essential fields for session listing.
    """
    id: int = Field(..., description="ID of the training session")
    name: str = Field(..., description="Name of the training session")
    day_of_week: Optional[int] = Field(None, description="Day of the week (1-7 for Monday-Sunday)")
    session_status: str = Field(..., description="Current status of the session (pending, active, completed, abandoned)")

    @field_serializer('session_status')
    def serialize_session_status(self, session_status, _info):
        """Convert SessionStatus enum to string"""
        if hasattr(session_status, 'value'):
            return session_status.value
        return session_status

    class Config:
        from_attributes = True
