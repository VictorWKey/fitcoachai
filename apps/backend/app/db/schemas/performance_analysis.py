"""
Performance Analysis schemas for the FitCoach AI application.

This module contains Pydantic schemas for performance analysis including:
- Base schema with performance metrics
- Create schema for creating new performance analyses
- Update schema for modifying existing performance analyses
- Response schema for returning performance analysis data

Used to compare programmed vs. actual performance for training optimization.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class PerformanceAnalysisBase(BaseModel):
    """
    Base schema for performance analysis data.
    
    Contains common fields for comparing programmed vs. actual performance.
    """
    user_id: int
    training_session_id: int
    programmed_exercise_id: int
    strength_log_id: int
    weight_achievement: Optional[float] = None
    reps_achievement: Optional[float] = None
    volume_achievement: Optional[float] = None
    notes: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class PerformanceAnalysisCreate(PerformanceAnalysisBase):
    """
    Schema for creating a new performance analysis.
    
    Inherits all fields from the base schema.
    """
    pass

class PerformanceAnalysisUpdate(BaseModel):
    """
    Schema for updating an existing performance analysis.
    
    All fields are optional to allow partial updates.
    """
    weight_achievement: Optional[float] = None
    reps_achievement: Optional[float] = None
    volume_achievement: Optional[float] = None
    notes: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None

class PerformanceAnalysis(PerformanceAnalysisBase):
    """
    Schema for performance analysis response data.
    
    Includes database-generated fields like ID and timestamps.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
