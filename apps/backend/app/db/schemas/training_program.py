"""
Pydantic schemas for training programs and related entities.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from db.models.training_program import ProgramType
from db.models.exercise_block import BlockType
from db.models.programmed_exercise import LoadType
from db.models.strength_log import SetType


# Base schemas
class ProgrammedExerciseBase(BaseModel):
    """Base schema for programmed exercises."""
    standard_exercise_id: Optional[int] = None
    tempo: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    load_type: Optional[LoadType] = None
    load_value: Optional[str] = None
    rpe_target: Optional[float] = None
    percentage_1rm: Optional[float] = None
    weight_range: Optional[str] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    sets_type: Optional[SetType] = None
    custom_parameters: Optional[Dict[str, Any]] = None

class ExerciseBlockBase(BaseModel):
    """Base schema for exercise blocks."""
    name: str
    block_type: BlockType 
    order: int
    description: Optional[str] = None

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

class ExerciseBlockCreate(ExerciseBlockBase):
    """Schema for creating an exercise block."""
    programmed_exercises: List[ProgrammedExerciseCreate] = []

class TrainingSessionCreate(TrainingSessionBase):
    """Schema for creating a training session."""
    exercise_blocks: List[ExerciseBlockCreate] = []

class TrainingWeekCreate(TrainingWeekBase):
    """Schema for creating a training week."""
    training_sessions: List[TrainingSessionCreate] = []

class TrainingProgramCreate(TrainingProgramBase):
    """Schema for creating a training program."""
    training_weeks: List[TrainingWeekCreate] = []

# Update schemas
class ProgrammedExerciseUpdate(BaseModel):
    """Schema for updating a programmed exercise."""
    exercise_name: Optional[str] = None
    variation: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None
    load_type: Optional[LoadType] = None
    load_value: Optional[str] = None
    rpe_target: Optional[float] = None
    percentage_1rm: Optional[float] = None
    weight_range: Optional[str] = None
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    custom_parameters: Optional[Dict[str, Any]] = None

class ExerciseBlockUpdate(BaseModel):
    """Schema for updating an exercise block."""
    name: Optional[str] = None
    block_type: Optional[BlockType] = None
    order: Optional[int] = None
    description: Optional[str] = None

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
    block_id: int
    created_at: datetime
    updated_at: datetime
    # Campo para el nombre del ejercicio estándar
    exercise_name: Optional[str] = None

    class Config:
        from_attributes = True

class ExerciseBlockResponse(ExerciseBlockBase):
    """Schema for exercise block response."""
    id: int
    session_id: int
    programmed_exercises: List[ProgrammedExerciseResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TrainingSessionResponse(TrainingSessionBase):
    """Schema for training session response."""
    id: int
    week_id: int
    exercise_blocks: List[ExerciseBlockResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TrainingSessionListResponse(BaseModel):
    """Schema for simplified training session list response."""
    name: str
    day_of_week: Optional[int] = None
    is_session_active: bool
    is_session_completed: bool

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