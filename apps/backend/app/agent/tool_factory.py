"""
Factory for creating discipline-specific tools for training coaching.
Provides mapping between training disciplines and their corresponding tool sets.
Now uses a unified strength tool for both hypertrophy and max strength training.
"""

from typing import List, Dict
from langchain_core.tools import BaseTool
from db.models.workout import TrainingDiscipline
from agent.tools import (
    exercise_log_strength,  # Unified tool for both hypertrophy and max strength
    exercise_log_cardio,
    exercise_log_flexibility,
    init_workout,
    finish_workout
)

def get_tools_for_discipline(discipline: TrainingDiscipline) -> List[BaseTool]:
    """
    Returns the appropriate tools based on the training discipline.
    
    Note: Both HYPERTROPHY and MAX_STRENGTH now use the unified exercise_log_strength tool
    which automatically infers the discipline based on reps, weight percentage, and rest time.
    
    Args:
        discipline: User's training discipline
        
    Returns:
        List[BaseTool]: List of tools available for the discipline
    """
    
    # Base tools available for all disciplines
    base_tools = [init_workout, finish_workout]
    
    # Mapping of disciplines to specific tools
    # Note: Hypertrophy and Max Strength now share the same unified tool
    discipline_tools = {
        TrainingDiscipline.HYPERTROPHY: base_tools + [exercise_log_strength],
        TrainingDiscipline.MAX_STRENGTH: base_tools + [exercise_log_strength],
        TrainingDiscipline.CARDIO: base_tools + [exercise_log_cardio],
        TrainingDiscipline.FLEXIBILITY: base_tools + [exercise_log_flexibility],
    }
    
    # Get specific tools for the discipline
    specific_tools = discipline_tools.get(discipline, [])  
    
    return base_tools + specific_tools

def get_available_disciplines() -> List[TrainingDiscipline]:
    """
    Returns all available training disciplines.
    
    Returns:
        List[TrainingDiscipline]: List of available disciplines
    """
    return list(TrainingDiscipline)

def get_tool_mapping_info() -> Dict[str, str]:
    """
    Returns information about the current tool mapping for each discipline.
    Useful for debugging and documentation.
    
    Returns:
        Dict[str, str]: Mapping of discipline names to their tool descriptions
    """
    return {
        "HYPERTROPHY": "Uses exercise_log_strength (unified tool with auto-detection)",
        "MAX_STRENGTH": "Uses exercise_log_strength (unified tool with auto-detection)", 
        "CARDIO": "Uses exercise_log_cardio (dedicated cardio tool)",
        "FLEXIBILITY": "Uses exercise_log_flexibility (dedicated flexibility tool)"
    }

def get_strength_tool_detection_rules() -> Dict[str, str]:
    """
    Returns the detection rules used by the unified strength tool.
    
    Returns:
        Dict[str, str]: Detection rules for discipline inference
    """
    return {
        "MAX_STRENGTH": "≤5 reps OR ≥85% 1RM OR ≥180 seconds rest",
        "HYPERTROPHY": "≥6 reps AND moderate intensity (default fallback)"
    } 