"""
Fitness disciplines routes package.
Includes routes for all specific fitness disciplines like max strength, hypertrophy, etc.
"""

from fastapi import APIRouter
from .max_strength import max_strength_router
from .hypertrophy import hypertrophy_router
from .flexibility import flexibility_router
from .cardio import cardio_router

fitness_disciplines_router = APIRouter(prefix="/disciplines", tags=["fitness-disciplines"])

# Include all discipline-specific routers
fitness_disciplines_router.include_router(max_strength_router)
fitness_disciplines_router.include_router(hypertrophy_router)
fitness_disciplines_router.include_router(flexibility_router)
fitness_disciplines_router.include_router(cardio_router)