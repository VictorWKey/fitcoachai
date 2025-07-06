"""
Exercise analysis service for the FitCoach AI application.

This module contains business logic for analyzing exercise data and inferring
exercise types, training zones, and other exercise-related insights.
"""

from typing import Optional, Literal, Dict, Union
from enum import Enum
from db.models.strength_log import ExerciseType, WeightUnit
from utils.tempo_utils import parse_tempo, validate_tempo


def infer_series_type(
    reps: Optional[int] = None,
    rir: Optional[int] = None,
    one_rm_percentage: Optional[float] = None,
    rpe: Optional[float] = None,
    tempo: Optional[str] = None,
    rest_time_seconds: Optional[int] = None,
) -> ExerciseType:
    """
    Infer the type of exercise series based on multiple parameters simultaneously.
    
    This function uses a sophisticated scoring system that evaluates multiple
    parameters together to determine if a series is focused on strength,
    hypertrophy, or technique. It considers combinations of parameters rather
    than evaluating them in isolation.
    
    Args:
        exercise_name: Name of the exercise
        set_number: Set number within the exercise
        reps: Number of repetitions performed
        weight: Weight used in the exercise
        weight_unit: Weight unit (kg or lb)
        rir: Reps in Reserve (RIR)
        one_rm_percentage: Percentage of 1RM used
        rpe: Rate of Perceived Exertion (1-10 scale)
        tempo_eccentric: Time in seconds for eccentric phase
        tempo_pause_bottom: Time in seconds for pause at bottom
        tempo_concentric: Time in seconds for concentric phase
        rest_time_seconds: Rest time in seconds after this set
        notes: Additional notes about the exercise
        
    Returns:
        ExerciseType: The inferred exercise type (STRENGTH, HIPERTROPHY, or TECHNIQUE)
    """
    
    def is_slow_tempo() -> bool:
        """Check if the tempo is slow (total >= 6 seconds)."""
        if not tempo or not validate_tempo(tempo):
            return False
            
        try:
            tempo_parts = parse_tempo(tempo)
            total_seconds = 0
            
            # Sum all numeric values
            for key, value in tempo_parts.items():
                if isinstance(value, int):
                    total_seconds += value
                    
            return total_seconds >= 6
        except ValueError:
            return False
    
    # Initialize scoring system
    strength_score = 0
    hypertrophy_score = 0
    technique_score = 0
    
    # 1. Evaluate 1RM percentage (high weight)
    if one_rm_percentage is not None:
        if one_rm_percentage >= 85:
            strength_score += 3
        elif 75 <= one_rm_percentage < 85:
            strength_score += 2
            hypertrophy_score += 1
        elif 60 <= one_rm_percentage < 75:
            hypertrophy_score += 2
            strength_score += 1
        elif one_rm_percentage < 60:
            technique_score += 2
    
    # 2. Evaluate RPE and RIR together
    if rpe is not None:
        if rpe >= 6:
            strength_score += 2
            hypertrophy_score += 2
        elif rpe < 6:
            technique_score += 2
    
    if rir is not None:
        if rir <= 4:
            strength_score += 2
            hypertrophy_score += 2
        elif rir > 4:
            technique_score += 2
    
    # 3. Evaluate reps in combination with other parameters
    if reps is not None:
        if reps <= 5:
            strength_score += 1
        elif 6 <= reps <= 12:
            hypertrophy_score += 1
        elif reps > 12:
            technique_score += 1
    
    # 4. Evaluate tempo
    if is_slow_tempo():
        technique_score += 2
        hypertrophy_score += 1
    
    # 5. Evaluate rest time
    if rest_time_seconds is not None:
        if rest_time_seconds > 240:
            strength_score += 2
        elif 90 <= rest_time_seconds <= 240:
            hypertrophy_score += 2
        elif rest_time_seconds < 90:
            technique_score += 2
    
    # High 1RM + Low RPE/RIR = Technique (not strength)
    if one_rm_percentage is not None and one_rm_percentage >= 75:
        if (rpe is not None and rpe < 6) or (rir is not None and rir > 4):
            technique_score += 3
            strength_score -= 2
    
    # Low 1RM + High RPE/RIR = Hypertrophy (not technique)
    if one_rm_percentage is not None and one_rm_percentage <= 60:
        if (rpe is not None and rpe >= 6) or (rir is not None and rir <= 3):
            hypertrophy_score += 3
            technique_score -= 2
    
    # High reps + High RPE = Hypertrophy (not technique)
    if reps is not None and reps >= 8:
        if (rpe is not None and rpe >= 6) or (rir is not None and rir <= 3):
            hypertrophy_score += 2
            technique_score -= 1
    
    # 9. Determine final type based on highest score
    scores = {
        ExerciseType.STRENGTH: strength_score,
        ExerciseType.HIPERTROPHY: hypertrophy_score,
        ExerciseType.TECHNIQUE: technique_score
    }
    
    # If all scores are equal or very close, default to hypertrophy
    max_score = max(scores.values())
    if max_score == 0:
        return ExerciseType.HIPERTROPHY  # Default fallback
    
    # Return the type with the highest score
    return max(scores.items(), key=lambda x: x[1])[0]