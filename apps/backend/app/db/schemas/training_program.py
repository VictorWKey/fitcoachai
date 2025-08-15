"""
Pydantic schemas for training programs and related entities.
"""

from pydantic import BaseModel, field_serializer, model_serializer, field_validator
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
    exercise_order: Optional[int] = None  # Position within session (0, 1, 2...)
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
    session_order: Optional[int] = None  # Sequential order within program (0,1,2,3...) - auto-calculated if not provided
    description: Optional[str] = None

class TrainingWeekBase(BaseModel):
    """Base schema for training weeks."""
    week_number: Optional[int] = None  # Week number within program (1,2,3...) - auto-calculated if not provided
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
    id: Optional[int] = None  # If provided, update; if None, create new
    standard_exercise_id: int

class TrainingSessionCreate(TrainingSessionBase):
    """Schema for creating a training session."""
    id: Optional[int] = None  # If provided, update; if None, create new
    programmed_exercises: List[ProgrammedExerciseCreate] = []

class TrainingWeekCreate(TrainingWeekBase):
    """Schema for creating a training week."""
    id: Optional[int] = None  # If provided, update; if None, create new
    training_sessions: List[TrainingSessionCreate] = []

class TrainingProgramCreate(TrainingProgramBase):
    """Schema for creating a training program."""
    training_weeks: List[TrainingWeekCreate] = []

# Update schemas
class ProgrammedExerciseUpdate(ProgrammedExerciseBase):
    """Schema for updating/creating a programmed exercise."""
    id: Optional[int] = None  # If provided, update; if None, create new
    standard_exercise_id: Optional[int] = None  # Optional for updates, required for new
    
    # Fields that will be ignored from POST response (metadata)
    session_id: Optional[int] = None  # Ignored - determined by parent session
    exercise_name: Optional[str] = None  # Ignored - calculated from standard_exercise
    created_at: Optional[datetime] = None  # Ignored - metadata
    updated_at: Optional[datetime] = None  # Ignored - metadata
    
    @field_validator('standard_exercise_id')
    @classmethod
    def validate_standard_exercise_id(cls, v, info):
        """Validate that standard_exercise_id is provided for new exercises."""
        # Skip validation if we're in a context where we can't access the full data
        if not hasattr(info, 'data') or info.data is None:
            return v
            
        # Get the id field from the model data
        exercise_id = info.data.get('id')
        
        # If no id (new exercise) and no standard_exercise_id, it's invalid
        # If id exists (updating), standard_exercise_id can be None (we'll preserve existing)
        if exercise_id is None and v is None:
            raise ValueError('standard_exercise_id is required for new exercises')
        return v
    
    class Config:
        extra = "ignore"  # Ignore extra fields from POST response

class TrainingSessionUpdate(TrainingSessionBase):
    """Schema for updating a training session."""
    id: Optional[int] = None  # If provided, update; if None, create new
    programmed_exercises: List[ProgrammedExerciseUpdate] = []

class ExerciseReorderItem(BaseModel):
    """Schema for reordering exercises."""
    id: int
    exercise_order: int

class ExerciseReorderRequest(BaseModel):
    """Schema for exercise reorder request."""
    exercises: List[ExerciseReorderItem]

class TrainingSessionUpdate(TrainingSessionBase):
    """Schema for updating a training session."""
    id: Optional[int] = None  # If provided, update; if None, create new
    programmed_exercises: List[ProgrammedExerciseUpdate] = []
    
    # Fields that will be ignored from POST response (metadata)
    week_id: Optional[int] = None  # Ignored - determined by parent week
    session_status: Optional[str] = None  # Ignored - managed by system
    created_at: Optional[datetime] = None  # Ignored - metadata
    updated_at: Optional[datetime] = None  # Ignored - metadata
    
    class Config:
        extra = "ignore"  # Ignore extra fields from POST response

class TrainingWeekUpdate(TrainingWeekBase):
    """Schema for updating a training week."""
    id: Optional[int] = None  # If provided, update; if None, create new
    training_sessions: List[TrainingSessionUpdate] = []
    
    # Fields that will be ignored from POST response (metadata)
    program_id: Optional[int] = None  # Ignored - determined by parent program
    created_at: Optional[datetime] = None  # Ignored - metadata
    updated_at: Optional[datetime] = None  # Ignored - metadata
    
    class Config:
        extra = "ignore"  # Ignore extra fields from POST response

class TrainingProgramUpdate(TrainingProgramBase):
    """Schema for updating a training program."""
    training_weeks: List[TrainingWeekUpdate] = []
    
    # Fields that will be ignored from POST response (metadata)
    id: Optional[int] = None  # Ignored in updates - comes from URL
    user_id: Optional[int] = None  # Ignored - determined by authentication
    created_at: Optional[datetime] = None  # Ignored - metadata
    updated_at: Optional[datetime] = None  # Ignored - metadata
    
    class Config:
        extra = "ignore"  # Ignore extra fields from POST response

# Response schemas (compatible with Update schemas)
class ProgrammedExerciseResponse(ProgrammedExerciseBase):
    """Schema for programmed exercise response - compatible with Update schema."""
    id: int
    session_id: int  # This will be ignored in updates
    standard_exercise_id: Optional[int] = None  # Fully compatible with Update
    exercise_name: Optional[str] = None  # Additional field for display
    created_at: datetime  # Metadata - ignored in updates
    updated_at: datetime  # Metadata - ignored in updates

    class Config:
        from_attributes = True

class TrainingSessionResponse(TrainingSessionBase):
    """Schema for training session response - compatible with Update schema."""
    id: int
    week_id: int  # Metadata - ignored in updates
    session_order: int  # Show actual value in response
    session_status: str  # Metadata - ignored in updates
    programmed_exercises: List[ProgrammedExerciseResponse] = []
    created_at: datetime  # Metadata - ignored in updates
    updated_at: datetime  # Metadata - ignored in updates

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
    """Schema for training week response - compatible with Update schema."""
    id: int
    program_id: int  # Metadata - ignored in updates
    week_number: int  # Show actual value in response
    training_sessions: List[TrainingSessionResponse] = []
    created_at: datetime  # Metadata - ignored in updates
    updated_at: datetime  # Metadata - ignored in updates

    class Config:
        from_attributes = True
    created_at: datetime  # Metadata - ignored in updates
    updated_at: datetime  # Metadata - ignored in updates

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
    """Schema for training program response - compatible with Update schema."""
    id: int
    user_id: int  # Metadata - ignored in updates
    training_weeks: List[TrainingWeekResponse] = []
    created_at: datetime  # Metadata - ignored in updates
    updated_at: datetime  # Metadata - ignored in updates

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