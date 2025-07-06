"""
Workout finishing tool for the FitCoach AI agent.

This module contains the tool for finalizing active workouts, analyzing
exercises performed to determine the main muscle group and workout category.
"""

from pydantic import BaseModel
from langchain_core.tools import tool
from db.crud.utils import finalize_workout
from db.crud.workout import get_active_workout
from db.models.workout import Workout
from db.session import db_session
from langgraph.prebuilt import InjectedState
from typing import Annotated, Optional, cast
from langchain_core.runnables import RunnableConfig

class FinishWorkoutResponse(BaseModel):
    """Response model for finish_workout tool."""
    success: bool
    message: str
    workout_id: Optional[int] = None
    muscle_group: Optional[str] = None
    category: Optional[str] = None

@tool("finish_workout")
async def finish_workout(
    config: RunnableConfig
) -> dict:
    """
    Finish the user's current workout by analyzing all performed exercises 
    to determine the main muscle group and workout category. Use this tool 
    when the user indicates they have finished their workout or want to end it.
    
    Args:
        config (RunnableConfig): Configuration containing user_id and llm instance.
        
    Returns:
        dict: Dictionary containing success status, message, and workout details.
    """
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id")
    llm = configurable.get("llm")
    
    if not user_id:
        return {
            "success": False,
            "message": "User ID not found in configuration."
        }
    
    async with db_session() as db:
        active_workout = await get_active_workout(db, user_id)
        
        if not active_workout:
            return {
                "success": False,
                "message": "You don't have an active workout to finish."
            }
        
        workout_id = cast(int, active_workout.id)
        
        updated_workout = await finalize_workout(db, workout_id, llm)
        
        if not updated_workout:
            return {
                "success": False,
                "message": "Could not finish the workout."
            }
        
        return {
            "success": True,
            "message": "Workout finished successfully.",
            "workout_id": updated_workout.id,
            "muscle_group": updated_workout.muscle_group.value,
            "category": updated_workout.category.value
        } 