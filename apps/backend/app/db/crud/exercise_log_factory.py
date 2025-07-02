"""
Factory for exercise log CRUD operations.
Provides a centralized way to access CRUD operations for different fitness disciplines.
"""

from typing import Type, Any, Optional, List, Union, Dict, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.workout import TrainingDiscipline

# Import all discipline CRUD modules
from .discipline_exercise_logs import (
    # Hypertrophy
    get_hypertrophy_log, get_workout_hypertrophy_logs, update_hypertrophy_log, delete_hypertrophy_log,
    # Max Strength  
    get_max_strength_log, get_workout_max_strength_logs, update_max_strength_log, delete_max_strength_log,
    # Flexibility
    get_flexibility_log, get_workout_flexibility_logs, update_flexibility_log, delete_flexibility_log,
    # Cardio
    get_cardio_log, get_workout_cardio_logs, update_cardio_log, delete_cardio_log,
)

class ExerciseLogCRUDFactory:
    """Factory class to get appropriate CRUD functions based on discipline."""
    
    _discipline_crud_registry: Dict[TrainingDiscipline, Dict[str, Callable]] = {
        TrainingDiscipline.HYPERTROPHY: {
            'get_log': get_hypertrophy_log,
            'get_workout_logs': get_workout_hypertrophy_logs,
            'update_log': update_hypertrophy_log,
            'delete_log': delete_hypertrophy_log,
        },
        TrainingDiscipline.MAX_STRENGTH: {
            'get_log': get_max_strength_log,
            'get_workout_logs': get_workout_max_strength_logs,
            'update_log': update_max_strength_log,
            'delete_log': delete_max_strength_log,
        },
        TrainingDiscipline.FLEXIBILITY: {
            'get_log': get_flexibility_log,
            'get_workout_logs': get_workout_flexibility_logs,
            'update_log': update_flexibility_log,
            'delete_log': delete_flexibility_log,
        },
        TrainingDiscipline.CARDIO: {
            'get_log': get_cardio_log,
            'get_workout_logs': get_workout_cardio_logs,
            'update_log': update_cardio_log,
            'delete_log': delete_cardio_log,
        },
    }
    
    @classmethod
    async def get_exercise_log(
        cls, 
        db: AsyncSession,
        exercise_id: int,
        discipline: TrainingDiscipline
    ) -> Optional[Any]:
        """
        Get exercise log by ID and discipline.
        
        Args:
            db: Database session
            exercise_id: ID of the exercise log
            discipline: Training discipline
            
        Returns:
            Exercise log of the appropriate discipline or None if not found
        """
        crud_ops = cls._discipline_crud_registry.get(discipline)
        if not crud_ops:
            raise ValueError(f"Unsupported discipline: {discipline}")
        
        return await crud_ops['get_log'](db, exercise_id)
    
    @classmethod
    async def get_workout_logs(
        cls,
        db: AsyncSession,
        workout_id: int,
        discipline: TrainingDiscipline
    ) -> List[Any]:
        """
        Get all exercise logs for a workout by discipline.
        
        Args:
            db: Database session
            workout_id: ID of the workout
            discipline: Training discipline
            
        Returns:
            List of exercise logs of the appropriate discipline
        """
        crud_ops = cls._discipline_crud_registry.get(discipline)
        if not crud_ops:
            raise ValueError(f"Unsupported discipline: {discipline}")
        
        return await crud_ops['get_workout_logs'](db, workout_id)
    
    @classmethod
    async def update_exercise_log(
        cls,
        db: AsyncSession,
        exercise_id: int,
        discipline: TrainingDiscipline,
        update_data: Any
    ) -> Optional[Any]:
        """
        Update exercise log by ID and discipline.
        
        Args:
            db: Database session
            exercise_id: ID of the exercise log
            discipline: Training discipline
            update_data: Data to update
            
        Returns:
            Updated exercise log of the appropriate discipline or None if not found
        """
        crud_ops = cls._discipline_crud_registry.get(discipline)
        if not crud_ops:
            raise ValueError(f"Unsupported discipline: {discipline}")
        
        return await crud_ops['update_log'](db, exercise_id, update_data)
    
    @classmethod  
    async def delete_exercise_log(
        cls,
        db: AsyncSession,
        exercise_id: int,
        discipline: TrainingDiscipline
    ) -> bool:
        """
        Delete exercise log by ID and discipline.
        
        Args:
            db: Database session
            exercise_id: ID of the exercise log
            discipline: Training discipline
            
        Returns:
            True if deleted, False if not found
        """
        crud_ops = cls._discipline_crud_registry.get(discipline)
        if not crud_ops:
            raise ValueError(f"Unsupported discipline: {discipline}")
        
        return await crud_ops['delete_log'](db, exercise_id)
    
    @classmethod
    def get_supported_disciplines(cls) -> List[TrainingDiscipline]:
        """Get list of all supported training disciplines."""
        return list(cls._discipline_crud_registry.keys())
    
    @classmethod
    def is_discipline_supported(cls, discipline: TrainingDiscipline) -> bool:
        """Check if a discipline is supported by the factory."""
        return discipline in cls._discipline_crud_registry 