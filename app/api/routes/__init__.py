"""
Rutas de la API para la aplicación FitCoach AI.
Contiene los endpoints disponibles para la interfaz REST.
"""

from fastapi import APIRouter
from .chat_router import chat_router
from .exercises_router import exercises_router
from .auth_router import auth_router

api_router = APIRouter()
api_router.include_router(chat_router)
api_router.include_router(exercises_router)
api_router.include_router(auth_router)