"""
Utilities for CRUD operations.
Provides helper functions for common database operations.
Functions for inferring workout type using LLM.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from db.models.workout import Workout
from db.session import db_session
from db.models.workout import Category, MuscleGroup
from db.crud.workout import get_workout
from db.schemas.workout import WorkoutCreate
from typing import cast
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.models.workout import Workout, MuscleGroup, Category
from db.models.strength_log import StrengthLog
from db.models.cardio_log import CardioLog
from db.schemas.workout import WorkoutTypeInference
from langchain_core.messages import SystemMessage, HumanMessage
import calendar

# Time limit to consider a workout as active
WORKOUT_TIMEOUT_MINUTES = 90

async def get_or_create_workout_id(user_id: int, exercise_log_data=None, llm=None) -> int:
    """
    Gets the ID of the user's active workout or creates a new one if it doesn't exist.
    
    If this is the first exercise log of a new workout, tries to infer the workout type
    based on the exercise and historical data.
    
    A new workout will be created if:
    - There are no previous workouts
    - The last workout is older than WORKOUT_TIMEOUT_MINUTES
    - The last workout is marked as finished (is_finished=True)
    
    If the last workout is not finished but older than WORKOUT_TIMEOUT_MINUTES,
    it will be automatically finalized before creating a new one.
    
    Args:
        user_id: ID of the user
        exercise_log_data: Optional data for the current exercise log
        llm: Optional language model for inference
        
    Returns:
        int: ID of the active or newly created workout
    """
    now = datetime.now(timezone.utc)

    async with db_session() as db:
        # Find the user's last workout
        result = await db.execute(
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(Workout.created_at.desc())
            .limit(1)
        )
        last_workout = result.scalar_one_or_none()

        assert last_workout is not None

        # Check if we need to create a new workout
        create_new_workout = (
            last_workout is None or 
            cast(bool, last_workout.is_finished)
        )
        
        # Check if the last workout is inactive (older than timeout)
        inactive_workout = bool(
            last_workout is not None and
            not cast(bool, last_workout.is_finished) and
            (now - last_workout.created_at) > timedelta(minutes=WORKOUT_TIMEOUT_MINUTES)
        )
        
        # If the last workout is inactive but not finished, finalize it
        if inactive_workout:
            await finalize_workout(db, cast(int, last_workout.id), llm)
            create_new_workout = True
        
        if create_new_workout:
            # Default values
            muscle_group = MuscleGroup.FULL_BODY
            category = Category.HYPERTROPHY
            
            # If we have exercise data, use it to infer workout type
            if exercise_log_data and exercise_log_data.get('exercise_name') and llm:
                # Infer workout type using LLM
                inference_result = await infer_workout_type_from_first_exercise(
                    db=db,
                    user_id=user_id,
                    exercise_name=exercise_log_data.get('exercise_name'),
                    reps=exercise_log_data.get('reps'),
                    weight=exercise_log_data.get('weight'),
                    rir=exercise_log_data.get('rir'),
                    llm=llm
                )
                
                muscle_group = MuscleGroup(inference_result.muscle_group)
                category = Category(inference_result.category)
            
            # Create the new workout with the determined type
            new_workout = Workout(
                user_id=user_id, 
                category=category, 
                muscle_group=muscle_group, 
                start_time=now,
                is_finished=False
            )
            db.add(new_workout)
            await db.commit()
            await db.refresh(new_workout)
            return cast(int, new_workout.id)

        # If there is a recent one, reuse that workout_id
        return cast(int, last_workout.id)

async def get_recent_workouts_summary(db: AsyncSession, user_id: int, days: int = 14) -> str:
    """
    Get a humanized summary of recent workouts for a user.
    
    Args:
        db: Database session
        user_id: User ID
        days: Number of days to look back
        
    Returns:
        str: Humanized summary of recent workouts
    """
    # Calculate the date range
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    # Query recent workouts
    result = await db.execute(
        select(Workout)
        .where(
            Workout.user_id == user_id,
            Workout.start_time >= start_date
        )
        .order_by(desc(Workout.start_time))
    )
    
    recent_workouts = result.scalars().all()
    
    # If no recent workouts, return empty string
    if not recent_workouts:
        return "No has realizado entrenamientos en los últimos 14 días."
    
    # Format each workout in a human-readable way
    workout_summaries = []
    
    for workout in recent_workouts:
        # Get the day of the week
        day_name = calendar.day_name[workout.start_time.weekday()]
        
        # Calculate how many days ago
        days_ago = (now - workout.start_time).days
        
        # Format the date in a human-readable way
        if days_ago == 0:
            date_str = "Hoy"
        elif days_ago == 1:
            date_str = "Ayer"
        elif days_ago < 7:
            date_str = f"El {day_name} pasado"
        elif days_ago < 14:
            date_str = f"El {day_name} de la semana antepasada"
        else:
            date_str = f"Hace {days_ago} días ({day_name})"
        
        # Format the workout summary
        workout_summary = f"- {date_str}: {workout.muscle_group.value} ({workout.category.value})"
        workout_summaries.append(workout_summary)
    
    return "\n".join(workout_summaries)

async def infer_workout_type_from_first_exercise(
    db: AsyncSession, 
    user_id: int, 
    exercise_name: str, 
    reps: Optional[int] = None,
    weight: Optional[float] = None,
    rir: Optional[int] = None,
    llm = None
) -> WorkoutTypeInference:
    """
    Infer workout type based on the first exercise and workout history.
    
    Args:
        db: Database session
        user_id: User ID
        exercise_name: Name of the first exercise
        reps: Number of repetitions (optional)
        weight: Weight used (optional)
        rir: RIR value (optional)
        llm: Language model (optional)
        
    Returns:
        WorkoutTypeInference: Inferred muscle group and category
    """
    if not llm:
        # Default to a safe fallback if no LLM is provided
        return WorkoutTypeInference(
            muscle_group=MuscleGroup.FULL_BODY,
            category=Category.HYPERTROPHY
        )
    
    # Get workout history summary
    workout_history = await get_recent_workouts_summary(db, user_id)
    
    # Get current day of the week
    now = datetime.now(timezone.utc)
    current_day = calendar.day_name[now.weekday()]
    
    # Create exercise description
    exercise_desc = f"Ejercicio: {exercise_name}"
    if reps is not None:
        exercise_desc += f", {reps} repeticiones"
    if weight is not None:
        exercise_desc += f", {weight} kg"
    if rir is not None:
        exercise_desc += f", RIR {rir}"
    
    # Create system prompt
    system_prompt = """
    Eres un experto en fitness y entrenamiento. Tu tarea es analizar el primer ejercicio de un nuevo entrenamiento 
    y el historial reciente de entrenamientos del usuario para inferir:
    
    1. El grupo muscular principal más probable para el entrenamiento actual.
    2. La categoría de entrenamiento más probable.
    
    Usa el historial para identificar patrones, como:
    - Si el usuario sigue una rutina semanal (ej. lunes=pecho, martes=espalda)
    - Qué categoría de entrenamiento suele hacer para cada grupo muscular
    """
    
    # Create user message
    user_message = f"""
    PRIMER EJERCICIO DEL ENTRENAMIENTO ACTUAL:
    {exercise_desc}
    
    HOY ES: {current_day}
    
    HISTORIAL DE ENTRENAMIENTOS RECIENTES:
    {workout_history}
    
    Basándote en el primer ejercicio y el historial, ¿cuál es el grupo muscular y la categoría más probables para el entrenamiento actual?
    """
    
    # Create model with structured output
    model_with_structure = llm.with_structured_output(WorkoutTypeInference)
    
    # Call the model
    try:
        response = await model_with_structure.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        # The response is already validated against the WorkoutTypeInference schema
        return response
    except Exception as e:
        # Fallback to default values if something goes wrong
        print(f"Error inferring workout type: {e}")
        return WorkoutTypeInference(
            muscle_group=MuscleGroup.FULL_BODY,
            category=Category.HYPERTROPHY
        )

async def infer_workout_type_from_all_exercises(
    db: AsyncSession,
    workout_id: int,
    llm = None
) -> Optional[WorkoutTypeInference]:
    """
    Infer workout type based on all exercises in a workout.
    
    Args:
        db: Database session
        workout_id: Workout ID
        llm: Language model (optional)
        
    Returns:
        Optional[WorkoutTypeInference]: Inferred muscle group and category, or None if workout not found
    """
    # Get all strength exercise logs for this workout
    strength_result = await db.execute(
        select(StrengthLog)
        .where(StrengthLog.workout_id == workout_id)
        .order_by(StrengthLog.id)
    )
    strength_logs = strength_result.scalars().all()
    
    # Get all cardio exercise logs for this workout
    cardio_result = await db.execute(
        select(CardioLog)
        .where(CardioLog.workout_id == workout_id)
        .order_by(CardioLog.id)
    )
    cardio_logs = cardio_result.scalars().all()
    
    # If no exercises at all, return None
    if not strength_logs and not cardio_logs:
        return None
    
    if not llm:
        # Default to a safe fallback if no LLM is provided
        return WorkoutTypeInference(
            muscle_group=MuscleGroup.FULL_BODY,
            category=Category.HYPERTROPHY
        )
    
    # Create a summary of all exercises
    exercise_summaries = []
    
    # Add strength exercises
    for log in strength_logs:
        summary = f"- {log.exercise_name or 'Ejercicio de fuerza sin nombre'}"
        if log.reps is not None:
            summary += f", {log.reps} repeticiones"
        if log.weight is not None:
            weight_unit = log.weight_unit.value if log.weight_unit is not None else "kg"
            summary += f", {log.weight} {weight_unit}"
        if log.rir is not None:
            summary += f", RIR {log.rir}"
        summary += " (Fuerza/Hipertrofia)"
        exercise_summaries.append(summary)
    
    # Add cardio exercises
    for log in cardio_logs:
        summary = f"- {log.exercise_name or 'Ejercicio de cardio sin nombre'}"
        if log.cardio_type is not None:
            summary += f" ({log.cardio_type.value})"
        if log.total_duration_seconds is not None:
            duration_min = log.total_duration_seconds // 60
            summary += f", {duration_min} minutos"
        if log.distance is not None:
            distance_unit = log.distance_unit.value if log.distance_unit is not None else "km"
            summary += f", {log.distance} {distance_unit}"
        if log.intensity_level is not None:
            summary += f", nivel de intensidad {log.intensity_level}"
        if log.incline_level is not None:
            summary += f", inclinación {log.incline_level}"
        if log.avg_heart_rate is not None:
            summary += f", FC promedio {log.avg_heart_rate} bpm"
        summary += " (Cardio)"
        exercise_summaries.append(summary)
    
    exercise_summary_text = "\n".join(exercise_summaries)
    
    # Create system prompt
    system_prompt = """
    Eres un experto en fitness y entrenamiento. Tu tarea es analizar un entrenamiento completo y determinar:
    
    1. El grupo muscular principal trabajado en este entrenamiento.
    2. La categoría de entrenamiento (fuerza, hipertrofia, cardio, etc.).
    
    Analiza todos los ejercicios realizados, incluyendo ejercicios de fuerza/hipertrofia y ejercicios de cardio, 
    sus repeticiones, pesos, duración, distancia y otros detalles para hacer una evaluación precisa.
    
    Si el entrenamiento incluye principalmente ejercicios de cardio, clasifícalo como CARDIO.
    Si incluye principalmente ejercicios de fuerza, clasifícalo según las repeticiones (FUERZA para pocas reps, HIPERTROFIA para reps medias).
    Si es una mezcla equilibrada, considera el volumen total de cada tipo.
    """
    
    # Create user message
    user_message = f"""
    RESUMEN COMPLETO DEL ENTRENAMIENTO:
    {exercise_summary_text}
    
    Basándote en todos estos ejercicios (tanto de fuerza como de cardio), ¿cuál es el grupo muscular principal y la categoría de este entrenamiento?
    """
    
    # Create model with structured output
    model_with_structure = llm.with_structured_output(WorkoutTypeInference)
    
    # Call the model
    try:
        response = await model_with_structure.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ])
        
        # The response is already validated against the WorkoutTypeInference schema
        return response
    except Exception as e:
        # Fallback to default values if something goes wrong
        print(f"Error inferring workout type: {e}")
        return WorkoutTypeInference(
            muscle_group=MuscleGroup.FULL_BODY,
            category=Category.HYPERTROPHY
        ) 

async def finalize_workout(db: AsyncSession, workout_id: int, llm=None) -> Optional[Workout]:
    """
    Finalizes a workout by updating its muscle group and category based on all exercises,
    and marking it as finished.
    
    Args:
        db: Database session
        workout_id: ID of the workout to finalize
        llm: Optional language model for inference
        
    Returns:
        Workout: The updated workout or None if it doesn't exist
    """
    # Get the workout
    workout = await get_workout(db, workout_id)
    if not workout:
        return None
    
    # If the workout is already finished, just return it
    if cast(bool, workout.is_finished):
        return workout
    
    # Infer workout type from all exercises
    if llm:
        inference = await infer_workout_type_from_all_exercises(db, workout_id, llm)
        if inference:
            setattr(workout, "muscle_group", inference.muscle_group)
            setattr(workout, "category", inference.category)
    
    # Mark as finished
    setattr(workout, "is_finished", True)
    
    # Save changes
    await db.commit()
    await db.refresh(workout)
    return workout