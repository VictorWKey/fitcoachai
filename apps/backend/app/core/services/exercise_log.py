"""
Core service for exercise log operations.
Provides high-level business logic for exercise log management across all disciplines.
"""

from typing import Any, List, Optional, Dict, Union
from sqlalchemy.ext.asyncio import AsyncSession
from db.crud.exercise_log_factory import ExerciseLogCRUDFactory
from db.crud.workout import get_workout
from db.models.workout import Workout
from exceptions.api import NotFoundError, ForbiddenError

class CoreExerciseLogService:
    """Core service for exercise log operations."""
    
    @staticmethod
    async def get_exercise_log_by_workout(
        db: AsyncSession,
        exercise_id: int,
        workout_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Any]:
        """
        Get exercise log by ID, automatically determining discipline from workout.
        
        Args:
            db: Database session
            exercise_id: ID of the exercise log
            workout_id: ID of the workout
            user_id: Optional user ID for authorization check
            
        Returns:
            Exercise log of the appropriate discipline or None if not found
            
        Raises:
            NotFoundError: If workout is not found
            ForbiddenError: If user doesn't own the workout
        """
        workout = await get_workout(db, workout_id)
        if not workout:
            raise NotFoundError("Workout not found")
        
        # Check authorization if user_id is provided
        if user_id and getattr(workout, 'user_id') != user_id:
            raise ForbiddenError("Not authorized to access this workout")
        
        exercise_log = await ExerciseLogCRUDFactory.get_exercise_log(
            db, exercise_id, getattr(workout, 'discipline')
        )
        
        # Verify that the exercise log belongs to the specified workout
        if exercise_log and getattr(exercise_log, 'workout_id') != workout_id:
            return None
        
        return exercise_log
    
    @staticmethod
    async def get_workout_exercise_logs(
        db: AsyncSession,
        workout_id: int,
        user_id: Optional[int] = None
    ) -> List[Any]:
        """
        Get all exercise logs for a workout.
        
        Args:
            db: Database session
            workout_id: ID of the workout
            user_id: Optional user ID for authorization check
            
        Returns:
            List of exercise logs of the appropriate discipline
            
        Raises:
            NotFoundError: If workout is not found
            ForbiddenError: If user doesn't own the workout
        """
        workout = await get_workout(db, workout_id)
        if not workout:
            raise NotFoundError("Workout not found")
        
        # Check authorization if user_id is provided
        if user_id and getattr(workout, 'user_id') != user_id:
            raise ForbiddenError("Not authorized to access this workout")
        
        return await ExerciseLogCRUDFactory.get_workout_logs(
            db, workout_id, getattr(workout, 'discipline')
        )
    
    @staticmethod
    async def update_exercise_log_by_workout(
        db: AsyncSession,
        exercise_id: int,
        workout_id: int,
        update_data: Any,
        user_id: Optional[int] = None
    ) -> Optional[Any]:
        """
        Update exercise log by ID, automatically determining discipline from workout.
        
        Args:
            db: Database session
            exercise_id: ID of the exercise log
            workout_id: ID of the workout
            update_data: Data to update
            user_id: Optional user ID for authorization check
            
        Returns:
            Updated exercise log of the appropriate discipline or None if not found
            
        Raises:
            NotFoundError: If workout or exercise log is not found
            ForbiddenError: If user doesn't own the workout
        """
        # First verify the exercise log exists and belongs to the workout
        existing_log = await CoreExerciseLogService.get_exercise_log_by_workout(
            db, exercise_id, workout_id, user_id
        )
        if not existing_log:
            raise NotFoundError("Exercise log not found")
        
        workout = await get_workout(db, workout_id)
        if not workout:
            raise NotFoundError("Workout not found")
        
        return await ExerciseLogCRUDFactory.update_exercise_log(
            db, exercise_id, getattr(workout, 'discipline'), update_data
        )
    
    @staticmethod
    async def delete_exercise_log_by_workout(
        db: AsyncSession,
        exercise_id: int,
        workout_id: int,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Delete exercise log by ID, automatically determining discipline from workout.
        
        Args:
            db: Database session
            exercise_id: ID of the exercise log
            workout_id: ID of the workout
            user_id: Optional user ID for authorization check
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            NotFoundError: If workout or exercise log is not found
            ForbiddenError: If user doesn't own the workout
        """
        # First verify the exercise log exists and belongs to the workout
        existing_log = await CoreExerciseLogService.get_exercise_log_by_workout(
            db, exercise_id, workout_id, user_id
        )
        if not existing_log:
            raise NotFoundError("Exercise log not found")
        
        workout = await get_workout(db, workout_id)
        if not workout:
            raise NotFoundError("Workout not found")
        
        return await ExerciseLogCRUDFactory.delete_exercise_log(
            db, exercise_id, getattr(workout, 'discipline')
        )
    
    @staticmethod
    async def get_exercise_logs_as_dicts(
        db: AsyncSession,
        workout_id: int,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all exercise logs for a workout as dictionaries with common format.
        
        Args:
            db: Database session
            workout_id: ID of the workout
            user_id: Optional user ID for authorization check
            
        Returns:
            List of exercise logs as dictionaries
        """
        logs = await CoreExerciseLogService.get_workout_exercise_logs(
            db, workout_id, user_id
        )
        
        # Convert to dictionaries using the mixin method if available
        result = []
        for log in logs:
            if hasattr(log, 'to_dict'):
                result.append(log.to_dict())
        
        return result
    
    @staticmethod
    def get_supported_disciplines() -> List[str]:
        """Get list of all supported training disciplines as strings."""
        disciplines = ExerciseLogCRUDFactory.get_supported_disciplines()
        return [discipline.value for discipline in disciplines] 