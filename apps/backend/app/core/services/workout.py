"""
Core workout service for FitCoach AI.

Handles workout creation, exercise logging (strength and cardio),
and workout statistics with user-specific data management.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from db.models.workout import Workout
from db.models.strength_log import StrengthLog
from db.models.cardio_log import CardioLog
from db.models.user import User
from exceptions.api import NotFoundException

class CoreWorkoutService:
    """
    Service for handling business logic related to workouts.
    """
    
    @staticmethod
    async def create_workout(
        db: AsyncSession,
        user_id: int,
        name: str,
        description: Optional[str] = None,
        date: Optional[datetime] = None
    ) -> Workout:
        """
        Creates a new workout.
        
        Args:
            db: Database session
            user_id: User ID
            name: Name of the workout
            description: Optional description
            date: Date of the workout (defaults to now)
            
        Returns:
            The created workout
            
        Raises:
            NotFoundException: If the user does not exist
        """
        # Verify that the user exists
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        workout = Workout(
            user_id=user_id,
            name=name,
            description=description,
            date=date or datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        db.add(workout)
        await db.commit()
        await db.refresh(workout)
        
        return workout
    
    @staticmethod
    async def log_strength_exercise(
        db: AsyncSession,
        workout_id: int,
        user_id: int,
        exercise_name: str,
        sets: int,
        reps: int,
        weight: Optional[float] = None,
        notes: Optional[str] = None
    ) -> StrengthLog:
        """
        Logs a strength exercise in a workout.
        
        Args:
            db: Database session
            workout_id: Workout ID
            user_id: User ID
            exercise_name: Name of the exercise
            sets: Number of sets
            reps: Number of reps
            weight: Optional weight
            notes: Optional notes
            
        Returns:
            The created strength exercise log
            
        Raises:
            NotFoundException: If the workout does not exist or does not belong to the user
        """
        # Verify that the workout exists and belongs to the user
        result = await db.execute(
            select(Workout).where(
                and_(
                    Workout.id == workout_id,
                    Workout.user_id == user_id
                )
            )
        )
        workout = result.scalars().first()
        if not workout:
            raise NotFoundException(f"Workout with ID {workout_id} not found for this user")
        
        exercise_log = StrengthLog(
            user_id=user_id,
            workout_id=workout_id,
            exercise_name=exercise_name,
            reps=reps,
            weight=weight,
            notes=notes,
            exercise_date=datetime.now(timezone.utc)
        )
        
        db.add(exercise_log)
        await db.commit()
        await db.refresh(exercise_log)
        
        return exercise_log

    @staticmethod
    async def log_cardio_exercise(
        db: AsyncSession,
        workout_id: int,
        user_id: int,
        exercise_name: str,
        cardio_type: Optional[str] = None,
        total_duration_seconds: Optional[int] = None,
        avg_heart_rate: Optional[int] = None,
        notes: Optional[str] = None
    ) -> CardioLog:
        """
        Logs a cardio exercise in a workout.
        
        Args:
            db: Database session
            workout_id: Workout ID
            user_id: User ID
            exercise_name: Name of the exercise
            cardio_type: Type of cardio (HIIT, LISS, etc.)
            total_duration_seconds: Duration in seconds
            avg_heart_rate: Average heart rate
            notes: Optional notes
            
        Returns:
            The created cardio exercise log
            
        Raises:
            NotFoundException: If the workout does not exist or does not belong to the user
        """
        # Verify that the workout exists and belongs to the user
        result = await db.execute(
            select(Workout).where(
                and_(
                    Workout.id == workout_id,
                    Workout.user_id == user_id
                )
            )
        )
        workout = result.scalars().first()
        if not workout:
            raise NotFoundException(f"Workout with ID {workout_id} not found for this user")
        
        exercise_log = CardioLog(
            user_id=user_id,
            workout_id=workout_id,
            exercise_name=exercise_name,
            cardio_type=cardio_type,
            total_duration_seconds=total_duration_seconds,
            avg_heart_rate=avg_heart_rate,
            notes=notes,
            exercise_date=datetime.now(timezone.utc)
        )
        
        db.add(exercise_log)
        await db.commit()
        await db.refresh(exercise_log)
        
        return exercise_log
    
    @staticmethod
    async def get_user_workouts(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Workout]:
        """
        Retrieves the workouts of a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Limit of records to return
            
        Returns:
            List of workouts
        """
        result = await db.execute(
            select(Workout)
            .where(Workout.user_id == user_id)
            .order_by(Workout.date.desc())
            .offset(skip)
            .limit(limit)
        )
        
        return list(result.scalars().all())
    
    @staticmethod
    async def get_workout_stats(
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Retrieves workout statistics for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with statistics
        """
        # Count total workouts
        workout_count = await db.execute(
            select(func.count(Workout.id)).where(Workout.user_id == user_id)
        )
        total_workouts = workout_count.scalar_one()
        
        # Count total strength exercises
        strength_exercise_count = await db.execute(
            select(func.count(StrengthLog.id))
            .join(Workout, StrengthLog.workout_id == Workout.id)
            .where(Workout.user_id == user_id)
        )
        total_strength_exercises = strength_exercise_count.scalar_one()
        
        # Count total cardio exercises
        cardio_exercise_count = await db.execute(
            select(func.count(CardioLog.id))
            .join(Workout, CardioLog.workout_id == Workout.id)
            .where(Workout.user_id == user_id)
        )
        total_cardio_exercises = cardio_exercise_count.scalar_one()
        
        total_exercises = total_strength_exercises + total_cardio_exercises
        
        # Get the most frequent strength exercises
        top_strength_exercises = await db.execute(
            select(
                StrengthLog.exercise_name,
                func.count(StrengthLog.id).label("count")
            )
            .join(Workout, StrengthLog.workout_id == Workout.id)
            .where(Workout.user_id == user_id)
            .group_by(StrengthLog.exercise_name)
            .order_by(func.count(StrengthLog.id).desc())
            .limit(3)
        )
        
        # Get the most frequent cardio exercises
        top_cardio_exercises = await db.execute(
            select(
                CardioLog.exercise_name,
                func.count(CardioLog.id).label("count")
            )
            .join(Workout, CardioLog.workout_id == Workout.id)
            .where(Workout.user_id == user_id)
            .group_by(CardioLog.exercise_name)
            .order_by(func.count(CardioLog.id).desc())
            .limit(3)
        )
        
        # Combine top exercises
        top_exercises_list = []
        
        for name, count in top_strength_exercises.all():
            if name:
                top_exercises_list.append({"name": name, "count": count, "type": "strength"})
        
        for name, count in top_cardio_exercises.all():
            if name:
                top_exercises_list.append({"name": name, "count": count, "type": "cardio"})
        
        # Sort by count and limit to top 5
        top_exercises_list.sort(key=lambda x: x["count"], reverse=True)
        top_exercises_list = top_exercises_list[:5]
        
        return {
            "total_workouts": total_workouts,
            "total_exercises": total_exercises,
            "total_strength_exercises": total_strength_exercises,
            "total_cardio_exercises": total_cardio_exercises,
            "top_exercises": top_exercises_list
        }
