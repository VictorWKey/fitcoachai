"""
Functions for inferring workout type using LLM.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from db.models.workout import Workout, MuscleGroup, Category
from db.models.exercise_log import ExerciseLog
from db.schemas.workout import WorkoutTypeInference
from langchain_core.messages import SystemMessage, HumanMessage
import calendar

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
    # Get all exercise logs for this workout
    result = await db.execute(
        select(ExerciseLog)
        .where(ExerciseLog.workout_id == workout_id)
        .order_by(ExerciseLog.id)
    )
    
    exercise_logs = result.scalars().all()
    
    if not exercise_logs:
        return None
    
    if not llm:
        # Default to a safe fallback if no LLM is provided
        return WorkoutTypeInference(
            muscle_group=MuscleGroup.FULL_BODY,
            category=Category.HYPERTROPHY
        )
    
    # Create a summary of all exercises
    exercise_summaries = []
    
    for log in exercise_logs:
        summary = f"- {log.exercise_name or 'Ejercicio sin nombre'}"
        if log.reps:
            summary += f", {log.reps} repeticiones"
        if log.weight:
            weight_unit = log.weight_unit.value if log.weight_unit else "kg"
            summary += f", {log.weight} {weight_unit}"
        if log.rir:
            summary += f", RIR {log.rir}"
        exercise_summaries.append(summary)
    
    exercise_summary_text = "\n".join(exercise_summaries)
    
    # Create system prompt
    system_prompt = """
    Eres un experto en fitness y entrenamiento. Tu tarea es analizar un entrenamiento completo y determinar:
    
    1. El grupo muscular principal trabajado en este entrenamiento.
    2. La categoría de entrenamiento (fuerza, hipertrofia, etc.).
    
    Analiza todos los ejercicios realizados, sus repeticiones, pesos y otros detalles para hacer una evaluación precisa.
    """
    
    # Create user message
    user_message = f"""
    RESUMEN COMPLETO DEL ENTRENAMIENTO:
    {exercise_summary_text}
    
    Basándote en todos estos ejercicios, ¿cuál es el grupo muscular principal y la categoría de este entrenamiento?
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