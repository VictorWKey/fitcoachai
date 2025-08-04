"""
Agent configuration for training session management.

This module exports the tools for managing training sessions and logging exercises.
"""

# Session management tools
from .tools.session_management import (
    start_training_session_tool,
    finish_training_session_tool,
    get_active_session_status
)

# Exercise logging tools
from .tools.log_strength_exercise import log_strength_exercise
from .tools.log_cardio_exercise import log_cardio_exercise
from .tools.finish_session import finish_session

# Complete tool list for agent configuration
TRAINING_TOOLS = [
    start_training_session_tool,
    finish_training_session_tool,
    get_active_session_status,
    log_strength_exercise,
    log_cardio_exercise,
    finish_session
]

__all__ = [
    "TRAINING_TOOLS",
    "start_training_session_tool",
    "finish_training_session_tool", 
    "get_active_session_status",
    "log_strength_exercise",
    "log_cardio_exercise",
    "finish_session"
]
