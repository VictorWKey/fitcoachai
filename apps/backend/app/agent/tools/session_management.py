"""
Training session management tools for the FitCoach AI agent.

These tools allow users to start and finish training sessions,
which are required for logging exercises.
"""

from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.tools import tool
from db.session import db_session
from db.crud.training_session import (
    start_training_session, 
    finish_training_session,
    get_active_session_for_user,
    TrainingSessionNotFoundError,
    SessionAlreadyActiveError,
    NoActiveSessionError
)
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig

class StartSessionInput(BaseModel):
    """Input schema for starting a training session."""
    session_id: int = Field(..., description="ID of the training session to start")

class FinishSessionInput(BaseModel):
    """Input schema for finishing a training session."""
    session_id: Optional[int] = Field(None, description="Optional specific session ID to finish. If not provided, finishes the active session.")

@tool
async def start_training_session_tool(
    input: StartSessionInput,
    config: Annotated[RunnableConfig, InjectedState]
) -> str:
    """
    Start a training session for exercise logging.
    
    This tool activates a specific training session from the user's program,
    enabling them to log exercises to that session.
    
    Args:
        input: Contains the session ID to start
        config: Configuration containing user context
        
    Returns:
        str: Confirmation message with session details
    """
    # Get user from config
    user_id = config.get('configurable', {}).get('user_id')
    if not user_id:
        return "❌ Error: No user found in context"
    
    try:
        async with db_session() as db:
            # Start the training session
            session = await start_training_session(db, user_id, input.session_id)
            
            return (
                f"🚀 **Training Session Started**\\n\\n"
                f"**Session:** {session.name}\\n"
                f"**Week:** {session.training_week.week_number if session.training_week else 'N/A'}\\n"
                f"**Day:** {session.day_of_week}\\n"
                f"**Status:** Active and ready for exercise logging\\n\\n"
                f"You can now start logging your exercises! 💪"
            )
            
    except SessionAlreadyActiveError as e:
        return f"❌ **Session Already Active**\\n\\n{str(e)}\\n\\nPlease finish your current session first."
    except TrainingSessionNotFoundError as e:
        return f"❌ **Session Not Found**\\n\\n{str(e)}"
    except Exception as e:
        return f"❌ Error starting session: {str(e)}"

@tool
async def finish_training_session_tool(
    input: FinishSessionInput,
    config: Annotated[RunnableConfig, InjectedState]
) -> str:
    """
    Finish the currently active training session.
    
    This tool completes the active training session, calculating metrics
    and preventing further exercise logging to that session.
    
    Args:
        input: Optional session ID to finish (if not provided, finishes active session)
        config: Configuration containing user context
        
    Returns:
        str: Completion summary with session metrics
    """
    # Get user from config
    user_id = config.get('configurable', {}).get('user_id')
    if not user_id:
        return "❌ Error: No user found in context"
    
    try:
        async with db_session() as db:
            # Finish the training session
            session = await finish_training_session(db, user_id, input.session_id)
            
            # Calculate session summary
            total_sets = len(session.strength_logs) if session.strength_logs else 0
            total_cardio = len(session.cardio_logs) if session.cardio_logs else 0
            
            duration_str = "N/A"
            if session.session_duration_seconds is not None:
                minutes = session.session_duration_seconds // 60
                seconds = session.session_duration_seconds % 60
                duration_str = f"{minutes}m {seconds}s"
            
            return (
                f"🏁 **Training Session Completed**\\n\\n"
                f"**Session:** {session.name}\\n"
                f"**Duration:** {duration_str}\\n"
                f"**Strength Sets:** {total_sets}\\n"
                f"**Cardio Exercises:** {total_cardio}\\n"
                f"Great work! Your session has been saved. 🎉"
            )
            
    except NoActiveSessionError as e:
        return f"❌ **No Active Session**\\n\\n{str(e)}"
    except TrainingSessionNotFoundError as e:
        return f"❌ **Session Not Found**\\n\\n{str(e)}"
    except Exception as e:
        return f"❌ Error finishing session: {str(e)}"

@tool
async def get_active_session_status(
    config: Annotated[RunnableConfig, InjectedState]
) -> str:
    """
    Get the status of the currently active training session.
    
    This tool shows information about the user's active session,
    including progress and logged exercises.
    
    Args:
        config: Configuration containing user context
        
    Returns:
        str: Status information about the active session
    """
    # Get user from config
    user_id = config.get('configurable', {}).get('user_id')
    if not user_id:
        return "❌ Error: No user found in context"
    
    try:
        async with db_session() as db:
            # Get active session
            session = await get_active_session_for_user(db, user_id)
            
            if not session:
                return (
                    "📋 **No Active Session**\\n\\n"
                    "You don't have any active training sessions. "
                    "Start a session from your training program to begin logging exercises."
                )
            
            # Calculate session info
            total_sets = len(session.strength_logs) if session.strength_logs else 0
            total_cardio = len(session.cardio_logs) if session.cardio_logs else 0
            
            duration_str = "N/A"
            if session.session_start_time is not None:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                duration = now - session.session_start_time
                minutes = duration.seconds // 60
                duration_str = f"{minutes}m"
            
            return (
                f"📊 **Active Session Status**\\n\\n"
                f"**Session:** {session.name}\\n"
                f"**Week:** {session.training_week.week_number if session.training_week else 'N/A'}\\n"
                f"**Duration:** {duration_str}\\n"
                f"**Strength Sets Logged:** {total_sets}\\n"
                f"**Cardio Exercises:** {total_cardio}\\n\\n"
                f"Ready for exercise logging! 💪"
            )
            
    except Exception as e:
        return f"❌ Error getting session status: {str(e)}"

# Export tools
__all__ = [
    "start_training_session_tool", 
    "finish_training_session_tool", 
    "get_active_session_status",
    "StartSessionInput",
    "FinishSessionInput"
]
