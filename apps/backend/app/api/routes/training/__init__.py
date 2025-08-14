"""
Training API module

This module contains all training-related endpoints organized in separate files:
- programs.py: Training program management
- weeks.py: Training week management
- sessions.py: Training session management
- exercises.py: Programmed exercise management
- standard_exercises.py: Standard exercise catalog and utilities
- logs.py: Exercise logging endpoints
"""

from fastapi import APIRouter
from .programs import router as programs_router
from .weeks import router as weeks_router
from .sessions import router as sessions_router
from .exercises import router as exercises_router
from .standard_exercises import standard_exercises_router
from .logs import router as logs_router

training_router = APIRouter(prefix="/training", tags=["Training"])

training_router.include_router(programs_router)
training_router.include_router(weeks_router)
training_router.include_router(sessions_router)
training_router.include_router(exercises_router)
training_router.include_router(logs_router)
training_router.include_router(standard_exercises_router)
