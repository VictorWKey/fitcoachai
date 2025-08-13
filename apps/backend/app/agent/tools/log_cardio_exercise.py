"""
Cardio exercise logging tool for the FitCoach AI agent.

This module contains the tool for logging cardio exercises.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal
from db.schemas.cardio_log import CardioLogCreate
from langchain_core.tools import tool
from db.crud.cardio_log import create_cardio_log
from db.session import db_session
from db.crud.training_session import get_active_session_for_user, NoActiveSessionError
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig
from db.models.cardio_log import CardioType, DistanceUnit

class LogCardioExerciseInput(BaseModel):
    """Input schema for logging a cardio exercise."""
    exercise_name: str = Field(..., description="Name of the cardio exercise (treadmill, bike, elliptical, etc.)")
    cardio_type: Literal["hiit", "steady_state"] = Field(..., description="Type of cardio training")
    total_duration_seconds: int = Field(..., description="Total duration of the exercise in seconds")
    distance: Optional[float] = Field(None, description="Distance covered (if applicable)")
    distance_unit: Optional[Literal["km", "mi"]] = Field("km", description="Unit of distance measurement")
    calories_burned: Optional[int] = Field(None, description="Estimated calories burned")
    avg_heart_rate: Optional[int] = Field(None, description="Average heart rate during exercise")
    avg_rpe: Optional[float] = Field(None, description="Average Rate of Perceived Exertion (1-10 scale)")
    intensity_level: Optional[int] = Field(None, description="Machine intensity level (1-20 typically)")
    incline_level: Optional[int] = Field(None, description="Machine incline level (0-15 typically)")
    notes: Optional[str] = Field(None, description="Any additional notes about the exercise")

@tool
async def log_cardio_exercise(
    input: LogCardioExerciseInput,
    config: Annotated[RunnableConfig, InjectedState]
) -> str:
    """
    Log a cardio exercise to the currently active training session.
    
    This tool records cardio exercises with detailed metrics.
    It requires an active training session to be started by the user.
    
    Args:
        input: Cardio exercise details including type, duration, and performance metrics
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
            
            # Create cardio log (as free cardio, not linked to programmed exercise)
            log_data = CardioLogCreate(
                user_id=user_id,
                programmed_exercise_id=None,  # Free cardio
                training_session_id=active_session.id,
                exercise_name=input.exercise_name,
                cardio_type=CardioType(input.cardio_type),
                total_duration_seconds=input.total_duration_seconds,
                distance=input.distance,
                distance_unit=DistanceUnit(input.distance_unit) if input.distance_unit else None,
                calories_burned=input.calories_burned,
                avg_heart_rate=input.avg_heart_rate,
                avg_rpe=input.avg_rpe,
                intensity_level=input.intensity_level,
                incline_level=input.incline_level,
                notes=input.notes
            )
            
            # Create the log entry
            cardio_log = await create_cardio_log(db, log_data)
            
            # Format duration for display
            minutes = input.total_duration_seconds // 60
            seconds = input.total_duration_seconds % 60
            duration_str = f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
            
            # Format distance if provided
            distance_str = ""
            if input.distance:
                distance_str = f" | {input.distance} {input.distance_unit or 'km'}"
            
            # Format additional metrics
            metrics_str = ""
            if input.calories_burned:
                metrics_str += f" | {input.calories_burned} cal"
            if input.avg_heart_rate:
                metrics_str += f" | HR: {input.avg_heart_rate} bpm"
            if input.avg_rpe:
                metrics_str += f" | RPE: {input.avg_rpe}"
            
            return (
                f"✅ **Cardio Exercise Logged Successfully**\\n\\n"
                f"**Session:** {active_session.name}\\n"
                f"**Exercise:** {input.exercise_name}\\n"
                f"**Type:** {input.cardio_type.title()}\\n"
                f"**Duration:** {duration_str}{distance_str}{metrics_str}\\n\\n"
            )
            
    except NoActiveSessionError:
        return (
            "❌ **No Active Training Session**\\n\\n"
            "You need to start a training session before logging exercises. "
            "Please select and start a session from your training program first."
        )
    except Exception as e:
        return f"❌ Error logging cardio exercise: {str(e)}"

# Export for backwards compatibility
__all__ = ["log_cardio_exercise", "LogCardioExerciseInput"]
