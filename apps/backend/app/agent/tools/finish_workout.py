from pydantic import BaseModel
from langchain_core.tools import tool
from db.crud.workout import get_active_workout, finalize_workout
from db.session import db_session
from langgraph.prebuilt import InjectedState
from typing import Annotated, Optional
from langchain_core.runnables import RunnableConfig

@tool("finish_workout")
async def finish_workout(
    config: RunnableConfig
) -> dict:
    """
    Usa esta herramienta cuando el usuario
    indique que ha terminado su entrenamiento o quiera finalizarlo.
    """
    user_id = config.get("configurable", {}).get("user_id")
    llm = config.get("configurable", {}).get("llm")
    
    if not user_id:
        return {
            "success": False,
            "message": "Usuario no identificado."
        }
    
    async with db_session() as db:
        active_workout = await get_active_workout(db, user_id)
        
        if not active_workout:
            return {
                "success": False,
                "message": "No tienes un entrenamiento activo para finalizar."
            }
        
        updated_workout = await finalize_workout(db, getattr(active_workout, 'id'), llm)
        
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