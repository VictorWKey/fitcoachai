from pydantic import BaseModel
from langchain_core.tools import tool
from db.crud.workout import get_active_workout, finalize_workout
from db.session import db_session
from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain_core.runnables import RunnableConfig

class FinishWorkoutResponse(BaseModel):
    """Response model for finish_workout tool"""
    success: bool
    message: str
    workout_id: int = None
    muscle_group: str = None
    category: str = None

@tool("finish_workout")
async def finish_workout(
    config: RunnableConfig
) -> dict:
    """
    Finaliza el entrenamiento actual del usuario, analizando todos los ejercicios realizados para determinar
    el grupo muscular principal y la categoría del entrenamiento. Usa esta herramienta cuando el usuario
    indique que ha terminado su entrenamiento o quiera finalizarlo.
    """
    user_id: int = config["configurable"].get("user_id")
    llm = config["configurable"].get("llm")
    
    async with db_session() as db:
        # Find the user's active workout
        active_workout = await get_active_workout(db, user_id)
        
        if not active_workout:
            return {
                "success": False,
                "message": "No tienes un entrenamiento activo para finalizar."
            }
        
        # Finalize the workout
        updated_workout = await finalize_workout(db, active_workout.id, llm)
        
        if not updated_workout:
            return {
                "success": False,
                "message": "No se pudo finalizar el entrenamiento."
            }
        
        return {
            "success": True,
            "message": "Entrenamiento finalizado correctamente.",
            "workout_id": updated_workout.id,
            "muscle_group": updated_workout.muscle_group.value,
            "category": updated_workout.category.value
        } 