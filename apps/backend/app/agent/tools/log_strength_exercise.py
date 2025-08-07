"""
Strength exercise logging tool for the FitCoach AI agent.

This module contains the tool for logging individual strength training sets,
including exercises, sets, reps, weight, and other performance metrics.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.strength_log import StrengthLogCreate
from langchain_core.tools import tool
from db.crud.strength_log import create_strength_log
from db.session import db_session
from db.schemas.strength_log import StrengthLogAgent
from db.crud.training_session import get_active_session_for_user, NoActiveSessionError
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig
from db.models.strength_log import WeightUnit
from core.services.exercise_analysis import infer_series_type
from utils.tempo_utils import fix_tempo_format
from db.models.standard_exercises import MuscleGroupEnum, EquipmentEnum
from db.crud.standard_exercises import get_standard_exercise_by_name, get_standard_exercises_by_equipment_and_muscle_group
from db.models.programmed_exercise import ProgrammedExercise
from db.models.exercise_block import ExerciseBlock
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from config.app_settings import settings
# from core.services.program_integration import link_log_to_program_by_id  # TODO: Reimplement for sessions
from typing import cast

class LogStrengthExerciseInput(BaseModel):
    """Input schema for logging a strength exercise set."""
    exercise_name: str = Field(..., description="Name of the exercise performed")
    set_number: int = Field(..., description="Set number within the exercise (1, 2, 3, etc.)")
    repetitions_done: int = Field(..., description="Number of repetitions completed in this set")
    used_weight: float = Field(..., description="Weight used for this set")
    used_weight_unit: Literal["kg", "lb"] = Field(default="kg", description="Unit of weight measurement")
    perceived_rir: Optional[int] = Field(None, description="Reps in Reserve (RIR) - how many more reps could be done")
    perceived_rpe: Optional[float] = Field(None, description="Rate of Perceived Exertion (RPE) on 1-10 scale")
    tempo: Optional[str] = Field(None, description="Tempo of the exercise in format 'E-B-C-T' (eccentric-bottom-concentric-top)")
    rest_time_seconds: Optional[int] = Field(None, description="Rest time after this set in seconds")
    notes: Optional[str] = Field(None, description="Any additional notes about this set")

@tool
async def log_strength_exercise(
    input: LogStrengthExerciseInput,
    config: Annotated[RunnableConfig, InjectedState]
) -> str:
    """
    Log a strength training exercise set to the currently active training session.
    
    This tool records individual sets of strength exercises with detailed metrics.
    It requires an active training session to be started by the user.
    
    Args:
        input: Exercise details including name, reps, weight, and performance metrics
        config: Configuration containing user context
        
    Returns:
        str: Confirmation message with exercise details and session progress
        
    Raises:
        NoActiveSessionError: If user has no active training session
    """
    # Get user from config
    user_id = config.get('configurable', {}).get('user_id')
    if not user_id:
        return "❌ Error: No user found in context"
    
    try:
        async with db_session() as db:
            # Check for active training session
            active_session = await get_active_session_for_user(db, user_id)
            if not active_session:
                return (
                    "❌ **No Active Training Session**\\n\\n"
                    "You need to start a training session before logging exercises. "
                    "Please select and start a session from your training program first."
                )
            
            # Find the programmed exercise in the active session by exercise name
            stmt = select(ProgrammedExercise).join(
                ExerciseBlock, ProgrammedExercise.block_id == ExerciseBlock.id
            ).options(
                selectinload(ProgrammedExercise.standard_exercise)
            ).where(
                ExerciseBlock.session_id == getattr(active_session, 'id')
            )
            
            result = await db.execute(stmt)
            programmed_exercises = result.scalars().all()
            
            # Find matching exercise by name
            matching_exercise = None
            for pe in programmed_exercises:
                if pe.standard_exercise and pe.standard_exercise.name.lower() == input.exercise_name.lower():
                    matching_exercise = pe
                    break
            
            if not matching_exercise:
                available_exercises = [pe.standard_exercise.name for pe in programmed_exercises if pe.standard_exercise]
                return (
                    f"❌ Exercise '{input.exercise_name}' is not programmed in your current session.\\n\\n"
                    f"**Available exercises in this session:**\\n" + 
                    "\\n".join([f"• {name}" for name in available_exercises])
                )
            
            # Fix tempo format if provided
            tempo = None
            if input.tempo:
                try:
                    tempo = fix_tempo_format(input.tempo)
                except ValueError as e:
                    return f"❌ Invalid tempo format: {e}"
            
            # Infer set type from the exercise data
            set_type = infer_series_type(
                reps=input.repetitions_done,
                rir=input.perceived_rir,
                rpe=input.perceived_rpe,
                tempo=tempo,
                rest_time_seconds=input.rest_time_seconds
            )
            
            # Create strength log
            log_data = StrengthLogCreate(
                programmed_exercise_id=cast(int, matching_exercise.id),
                set_number=input.set_number,
                set_type=set_type,
                repetitions_done=input.repetitions_done,
                used_weight=input.used_weight,
                used_weight_unit=WeightUnit(input.used_weight_unit),
                perceived_rir=input.perceived_rir,
                perceived_rpe=input.perceived_rpe,
                tempo=tempo,
                rest_time_seconds=input.rest_time_seconds,
                notes=input.notes
            )
            
            # Create the log entry
            strength_log = await create_strength_log(
                db=db, 
                log_data=log_data,
                user_id=user_id,
                training_session_id=getattr(active_session, 'id')
            )
            
            # Note: Program linking would happen here in a complete implementation
            # but is optional for basic functionality
            
            # Format confirmation message
            weight_str = f"{input.used_weight}{input.used_weight_unit}"
            rir_str = f" (RIR: {input.perceived_rir})" if input.perceived_rir is not None else ""
            rpe_str = f" (RPE: {input.perceived_rpe})" if input.perceived_rpe is not None else ""
            tempo_str = f" | Tempo: {tempo}" if tempo else ""
            rest_str = f" | Rest: {input.rest_time_seconds}s" if input.rest_time_seconds else ""
            
            return (
                f"✅ **Set Logged Successfully**\\n\\n"
                f"**Session:** {active_session.name}\\n"
                f"**Exercise:** {input.exercise_name}\\n"
                f"**Set {input.set_number}:** {input.repetitions_done} reps @ {weight_str}{rir_str}{rpe_str}\\n"
                f"**Type:** {set_type.value.title() if set_type else 'Unknown'}{tempo_str}{rest_str}\\n\\n"
            )
            
    except NoActiveSessionError:
        return (
            "❌ **No Active Training Session**\\n\\n"
            "You need to start a training session before logging exercises. "
            "Please select and start a session from your training program first."
        )
    except Exception as e:
        return f"❌ Error logging exercise: {str(e)}"

# Export for backwards compatibility
__all__ = ["log_strength_exercise", "LogStrengthExerciseInput"]
