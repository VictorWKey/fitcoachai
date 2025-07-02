from pydantic import BaseModel
from langchain_core.tools import tool
from db.crud.workout import get_active_workout, create_workout
from db.session import db_session
from langgraph.prebuilt import InjectedState
from typing import Annotated, Optional
from langchain_core.runnables import RunnableConfig
from db.schemas.workout import WorkoutCreate, InitWorkout
from db.models.workout import TrainingDiscipline, MuscleGroup
from db.crud.user import get_user_training_discipline


@tool("init_workout", args_schema=InitWorkout)
async def init_workout(
    config: RunnableConfig
) -> dict:
    """
    Inicia un nuevo entrenamiento para el usuario, para que sea posible registrar ejercicios.
    Usa esta herramienta cuando el usuario indique que quiere comenzar un nuevo entrenamiento.
    """
    user_id = config.get("configurable", {}).get("user_id")
    
    if not user_id:
        raise ValueError("user_id is required in config")
    
    async with db_session() as db:
        # Verificar si ya existe un entrenamiento activo
        active_workout = await get_active_workout(db, user_id)
        
        if active_workout:
            return {
                "success": False,
                "message": "Ya tienes un entrenamiento activo. Finaliza el entrenamiento actual antes de iniciar uno nuevo.",
                "workout_id": active_workout.id,
                "discipline": active_workout.discipline.value
            }
        
        # Obtener la disciplina preferida del usuario
        user_discipline = await get_user_training_discipline(db, user_id) or TrainingDiscipline.HYPERTROPHY
        
        # Crear un nuevo entrenamiento
        workout_data = WorkoutCreate(
            user_id=user_id,
            discipline=user_discipline,
            muscle_group=MuscleGroup.CHEST
        )
        
        new_workout = await create_workout(db, workout_data)
        
        if not new_workout:
            return {
                "success": False,
                "message": "No se pudo crear el entrenamiento."
            }
        
        return {
            "success": True,
            "message": f"Entrenamiento iniciado correctamente. Disciplina: {user_discipline.value}",
            "workout_id": new_workout.id,
            "discipline": new_workout.discipline.value
        }
    
