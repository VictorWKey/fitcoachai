"""
Exercise routes package for FitCoach AI.
Combines general exercise operations with specific fitness discipline routes.
"""

from fastapi import APIRouter
from .general import general_exercises_router
from .fitness_disciplines import fitness_disciplines_router

exercises_router = APIRouter(prefix="/exercises", tags=["exercises"])

# Include general exercise routes
exercises_router.include_router(general_exercises_router)

# Include fitness discipline specific routes
exercises_router.include_router(fitness_disciplines_router) 