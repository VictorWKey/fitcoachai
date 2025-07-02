"""
Unified strength training tool for both hypertrophy and max strength exercises.
Automatically infers the training discipline based on reps, percentage, and rest time.
"""

from datetime import datetime
from pydantic import BaseModel, Field, BeforeValidator
from typing import Optional, Literal, Annotated
from db.schemas.discipline_exercise_logs.hypertrophy import HypertrophyLogCreate
from db.schemas.discipline_exercise_logs.max_strength import MaxStrengthLogCreate
from db.models.discipline_exercise_logs.common import WeightUnit, RangeOfMotion
from db.models.workout import TrainingDiscipline
from langchain_core.tools import tool
from db.crud.discipline_exercise_logs.hypertrophy import create_hypertrophy_log
from db.crud.discipline_exercise_logs.max_strength import create_max_strength_log
from db.session import db_session
from db.crud.utils import get_or_create_workout_id
from db.crud.user import get_user_training_discipline
from utils.model_utils import coerce_null_string
from langchain_core.runnables import RunnableConfig


class StrengthLogBase(BaseModel):
    """
    Unified schema for strength training that covers both hypertrophy and max strength.
    """
    exercise_name: Annotated[
        str,
        BeforeValidator(coerce_null_string),
        Field(
            description="Name of the strength exercise performed. Examples: 'bench press', 'squat', 'deadlift', 'bicep curl', 'leg press'."
        )
    ]
    set_number: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Set number within the exercise. Resets to 1 when exercise changes."
        )
    ]
    reps: Annotated[
        int,
        BeforeValidator(coerce_null_string),
        Field(
            description="Number of repetitions completed in this set. 1-6 reps typically indicates max strength, 6+ reps indicates hypertrophy."
        )
    ]
    weight: Annotated[
        float,
        BeforeValidator(coerce_null_string),
        Field(
            description="Weight used in this set. Just the number, without unit."
        )
    ]
    weight_unit: Annotated[
        WeightUnit,
        BeforeValidator(coerce_null_string),
        Field(
            default=WeightUnit.KG,
            description="Unit of the recorded weight: kg or lb."
        )
    ]
    target_reps: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Target number of repetitions planned for this set (mainly for hypertrophy)."
        )
    ]
    rpe: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Rate of Perceived Exertion (RPE) on a scale of 1-10. How difficult the set felt."
        )
    ]
    rir: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Reps In Reserve (RIR). How many more reps the user could have done."
        )
    ]
    rest_time_seconds: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Rest time after the set in seconds. >180 seconds often indicates max strength training."
        )
    ]
    one_rm_percentage: Annotated[
        Optional[float],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Percentage of 1RM (one rep max) used in this set. Example: 85 for 85%. >85% typically indicates max strength."
        )
    ]
    exercise_type: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Specific type of strength exercise: squat, bench, deadlift, clean, jerk, snatch, etc."
        )
    ]
    tempo_eccentric: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Time in seconds for the eccentric (lowering) phase of the movement."
        )
    ]
    tempo_pause_bottom: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Time in seconds for the pause at the bottom position of the movement."
        )
    ]
    tempo_concentric: Annotated[
        Optional[int],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Time in seconds for the concentric (lifting) phase of the movement."
        )
    ]
    range_of_motion: Annotated[
        Optional[RangeOfMotion],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Range of motion used: full, partial, or other (mainly for hypertrophy)."
        )
    ]
    target_muscle: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Primary target muscle or muscle group (mainly for hypertrophy)."
        )
    ]
    notes: Annotated[
        Optional[str],
        BeforeValidator(coerce_null_string),
        Field(
            default=None,
            description="Additional information about the set: technique, sensations, equipment adjustments, etc."
        )
    ]


def infer_training_discipline(
    reps: int,
    one_rm_percentage: Optional[float] = None,
    rest_time_seconds: Optional[int] = None,
    user_discipline: Optional[TrainingDiscipline] = None
) -> TrainingDiscipline:
    """
    Infers the training discipline based on training parameters.
    
    Args:
        reps: Number of repetitions
        one_rm_percentage: Percentage of 1RM if provided
        rest_time_seconds: Rest time in seconds
        user_discipline: User's preferred discipline as fallback
        
    Returns:
        TrainingDiscipline: Inferred discipline
    """
    # Strong indicators for max strength
    if one_rm_percentage and one_rm_percentage >= 85:
        return TrainingDiscipline.MAX_STRENGTH
    
    if rest_time_seconds and rest_time_seconds >= 180:  # 3+ minutes
        return TrainingDiscipline.MAX_STRENGTH
    
    if reps <= 5:
        return TrainingDiscipline.MAX_STRENGTH
    
    # Strong indicators for hypertrophy
    if reps >= 6:
        return TrainingDiscipline.HYPERTROPHY
    
    # Fallback to user's preferred discipline or hypertrophy as default
    return user_discipline or TrainingDiscipline.HYPERTROPHY


@tool("exercise_log_strength", args_schema=StrengthLogBase)
async def exercise_log_strength(
    config: RunnableConfig,
    exercise_name: str,
    set_number: int,
    reps: int,
    weight: float,
    weight_unit: WeightUnit = WeightUnit.KG,
    target_reps: Optional[int] = None,
    rpe: Optional[float] = None,
    rir: Optional[int] = None,
    rest_time_seconds: Optional[int] = None,
    one_rm_percentage: Optional[float] = None,
    exercise_type: Optional[str] = None,
    tempo_eccentric: Optional[int] = None,
    tempo_pause_bottom: Optional[int] = None,
    tempo_concentric: Optional[int] = None,
    range_of_motion: Optional[RangeOfMotion] = None,
    target_muscle: Optional[str] = None,
    notes: Optional[str] = None
):
    """
    Records a strength training set in the database, automatically determining whether it's 
    hypertrophy or max strength training based on the parameters provided.
    
    This unified tool handles both hypertrophy (6+ reps, moderate weight) and max strength 
    (1-5 reps, heavy weight, high %1RM) training. It automatically saves to the appropriate 
    database table based on rep ranges, percentages, and rest times.
    
    Key auto-detection rules:
    - Max Strength: ≤5 reps, ≥85% 1RM, or ≥3min rest
    - Hypertrophy: ≥6 reps, moderate intensity
    """
    user_id = config.get("configurable", {}).get("user_id")
    llm = config.get("configurable", {}).get("llm")
    
    if not user_id:
        raise ValueError("user_id is required in config")
    
    workout_id = await get_or_create_workout_id(user_id, llm)
    
    # Get user's preferred discipline for fallback
    async with db_session() as db:
        user_discipline = await get_user_training_discipline(db, user_id)
    
    # Infer the actual discipline for this set
    inferred_discipline = infer_training_discipline(
        reps=reps,
        one_rm_percentage=one_rm_percentage,
        rest_time_seconds=rest_time_seconds,
        user_discipline=user_discipline
    )
    
    async with db_session() as db:
        if inferred_discipline == TrainingDiscipline.MAX_STRENGTH:
            # Save as max strength log
            await create_max_strength_log(
                db,
                MaxStrengthLogCreate(
                    workout_id=workout_id,
                    exercise_name=exercise_name,
                    set_number=set_number,
                    reps=reps,
                    weight=weight,
                    weight_unit=weight_unit,
                    rpe=rpe,
                    rir=rir,
                    rest_time_seconds=rest_time_seconds,
                    one_rm_percentage=one_rm_percentage,
                    exercise_type=exercise_type,
                    tempo_eccentric=tempo_eccentric,
                    tempo_pause_bottom=tempo_pause_bottom,
                    tempo_concentric=tempo_concentric,
                    notes=notes
                ),
                user_id
            )
            return f"Max strength set recorded: {exercise_name} - {reps} reps @ {weight}{weight_unit.value}"
        
        else:  # TrainingDiscipline.HYPERTROPHY
            # Save as hypertrophy log
            await create_hypertrophy_log(
                db,
                HypertrophyLogCreate(
                    workout_id=workout_id,
                    exercise_name=exercise_name,
                    set_number=set_number,
                    target_reps=target_reps,
                    completed_reps=reps,
                    weight=weight,
                    weight_unit=weight_unit,
                    rpe=rpe,
                    rir=rir,
                    tempo_eccentric=tempo_eccentric,
                    tempo_pause_bottom=tempo_pause_bottom,
                    tempo_concentric=tempo_concentric,
                    rest_time_seconds=rest_time_seconds,
                    range_of_motion=range_of_motion or RangeOfMotion.FULL,
                    target_muscle=target_muscle,
                    notes=notes
                ),
                user_id
            )
            return f"Hypertrophy set recorded: {exercise_name} - {reps} reps @ {weight}{weight_unit.value}" 