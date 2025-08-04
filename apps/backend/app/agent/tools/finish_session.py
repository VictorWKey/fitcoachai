"""
Session finishing tool for the FitCoach AI agent.

This module contains the tool for finalizing active training sessions.
"""

from pydantic import BaseModel
from langchain_core.tools import tool
from db.crud.training_session import (
    finish_training_session, 
    get_active_session_for_user,
    NoActiveSessionError
)
from db.session import db_session
from langgraph.prebuilt import InjectedState
from typing import Annotated, Optional
from langchain_core.runnables import RunnableConfig

class FinishSessionResponse(BaseModel):
    """Response model for finish_session tool."""
    success: bool
    message: str
    session_id: Optional[int] = None
    session_name: Optional[str] = None
    duration_seconds: Optional[int] = None
    completion_percentage: Optional[int] = None

@tool("finish_session")
async def finish_session(
    config: RunnableConfig
) -> dict:
    """
    Finish the currently active training session.
    
    This tool should only be called when the user explicitly indicates they
    want to finish their training session. It calculates session metrics
    and marks the session as completed.
    
    Args:
        config: Configuration containing user context
        
    Returns:
        dict: Response with session completion details
    """
    # Get user from config
    user_id = config.get('configurable', {}).get('user_id')
    if not user_id:
        return FinishSessionResponse(
            success=False,
            message="❌ Error: No user found in context"
        ).dict()
    
    try:
        async with db_session() as db:
            # Check if user has an active session
            active_session = await get_active_session_for_user(db, user_id)
            if not active_session:
                return FinishSessionResponse(
                    success=False,
                    message=(
                        "❌ **No Active Session**\\n\\n"
                        "You don't have any active training sessions to finish."
                    )
                ).dict()
            
            # Finish the session
            finished_session = await finish_training_session(db, user_id)
            
            # Calculate summary metrics
            total_strength_sets = len(finished_session.strength_logs) if finished_session.strength_logs else 0
            total_cardio_exercises = len(finished_session.cardio_logs) if finished_session.cardio_logs else 0
            
            # Format duration
            duration_str = "N/A"
            if finished_session.session_duration_seconds is not None:
                minutes = finished_session.session_duration_seconds // 60
                seconds = finished_session.session_duration_seconds % 60
                duration_str = f"{minutes}m {seconds}s" if seconds > 0 else f"{minutes}m"
            
            success_message = (
                f"🏁 **Training Session Completed!**\\n\\n"
                f"**Session:** {finished_session.name}\\n"
                f"**Duration:** {duration_str}\\n"
                f"**Strength Sets:** {total_strength_sets}\\n"
                f"**Cardio Exercises:** {total_cardio_exercises}\\n"
                f"Great work! Your session has been saved and you can now start a new one. 🎉"
            )
            
            return FinishSessionResponse(
                success=True,
                message=success_message,
                session_id=finished_session.id,
                session_name=finished_session.name,
                duration_seconds=finished_session.session_duration_seconds
            ).dict()
            
    except NoActiveSessionError:
        return FinishSessionResponse(
            success=False,
            message=(
                "❌ **No Active Session**\\n\\n"
                "You don't have any active training sessions to finish."
            )
        ).dict()
    except Exception as e:
        return FinishSessionResponse(
            success=False,
            message=f"❌ Error finishing session: {str(e)}"
        ).dict()

# Export for backwards compatibility
__all__ = ["finish_session", "FinishSessionResponse"]
