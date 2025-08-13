"""
Pydantic schemas for training programs and related entities.
"""

from pydantic import BaseModel, field_serializer, model_serializer
from typing import List, Optional
from datetime import datetime
from enum import Enum
from db.models.training_program import ProgramType
from db.models.programmed_exercise import LoadType, BlockType
from db.models.strength_log import SetType


# Base schemas
class ProgrammedExerciseBase(BaseModel):
    """Base schema for programmed exercises."""
    block: BlockType
    tempo: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    load_type: Optional[LoadType] = None
    rpe_target: Optional[float] = None
    percentage_1rm: Optional[float] = None
    weight_range: Optional[str] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    sets_type: Optional[SetType] = None

class TrainingSessionBase(BaseModel):
    """Base schema for training sessions."""
    name: str
    day_of_week: Optional[int] = None
    session_order: int  # Sequential order within program (0,1,2,3...)
    description: Optional[str] = None

class TrainingWeekBase(BaseModel):
    """Base schema for training weeks."""
    week_number: int
    description: Optional[str] = None

class TrainingProgramBase(BaseModel):
    """Base schema for training programs."""
    name: str
    description: Optional[str] = None
    program_type: ProgramType
    duration_weeks: int
    is_ai_generated: bool = False
    

class ProgrammedExerciseCreate(ProgrammedExerciseBase):
    """Schema for creating a programmed exercise."""
    standard_exercise_id: int

class TrainingSessionCreate(TrainingSessionBase):
    """Schema for creating a training session."""
    programmed_exercises: List[ProgrammedExerciseCreate] = []

class TrainingWeekCreate(TrainingWeekBase):
    """Schema for creating a training week."""
    training_sessions: List[TrainingSessionCreate] = []

class TrainingProgramCreate(TrainingProgramBase):
    """Schema for creating a training program."""
    training_weeks: List[TrainingWeekCreate] = []

# Update schemas
class ProgrammedExerciseUpdate(BaseModel):
    """Schema for updating a programmed exercise."""
    block: Optional[BlockType] = None
    tempo: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    load_type: Optional[LoadType] = None
    rpe_target: Optional[float] = None
    percentage_1rm: Optional[float] = None
    weight_range: Optional[str] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    sets_type: Optional[SetType] = None

class TrainingSessionUpdate(BaseModel):
    """Schema for updating a training session."""
    name: Optional[str] = None
    day_of_week: Optional[int] = None
    description: Optional[str] = None

class TrainingWeekUpdate(BaseModel):
    """Schema for updating a training week."""
    description: Optional[str] = None

class TrainingProgramUpdate(BaseModel):
    """Schema for updating a training program."""
    name: Optional[str] = None
    description: Optional[str] = None
    program_type: Optional[ProgramType] = None
    duration_weeks: Optional[int] = None
    # ...existing code...

# Response schemas
class ProgrammedExerciseResponse(ProgrammedExerciseBase):
    """Schema for programmed exercise response."""
    id: int
    session_id: int
    exercise_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TrainingSessionResponse(TrainingSessionBase):
    """Schema for training session response."""
    id: int
    week_id: int
    session_status: str
    programmed_exercises: List[ProgrammedExerciseResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TrainingSessionListResponse(BaseModel):
    """Schema for simplified training session list response."""
    id: int
    name: str
    day_of_week: Optional[int] = None
    session_status: str

    @field_serializer('session_status')
    def serialize_session_status(self, session_status, _info):
        """Convert SessionStatus enum to string"""
        if hasattr(session_status, 'value'):
            return session_status.value
        return session_status

    class Config:
        from_attributes = True

class SessionExercisesResponse(BaseModel):
    """Schema for session exercises grouped by block type."""
    main: List[ProgrammedExerciseResponse] = []
    accessory: List[ProgrammedExerciseResponse] = []

    class Config:
        from_attributes = True

class TrainingWeekResponse(TrainingWeekBase):
    """Schema for training week response."""
    id: int
    program_id: int
    training_sessions: List[TrainingSessionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TrainingWeekListResponse(BaseModel):
    """Schema for simplified training week list response."""
    id: int
    week_number: int
    description: Optional[str] = None

    class Config:
        from_attributes = True

class TrainingProgramResponse(TrainingProgramBase):
    """Schema for training program response."""
    id: int
    user_id: int
    training_weeks: List[TrainingWeekResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Simplified response schemas (for listing without full nested data)
class TrainingProgramSimpleResponse(TrainingProgramBase):
    """Simplified schema for training program response (without nested data)."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TrainingProgramSummary(TrainingProgramSimpleResponse):
    """Summary schema for training program with basic statistics."""
    total_weeks: Optional[int] = None
    total_sessions: Optional[int] = None
    total_exercises: Optional[int] = None
    
    class Config:
        from_attributes = True