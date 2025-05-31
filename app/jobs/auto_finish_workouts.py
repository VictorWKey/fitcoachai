"""
Job to automatically finish inactive workouts.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import select, and_
from db.models.workout import Workout
from db.models.exercise_log import ExerciseLog
from db.session import db_session
from db.crud.workout import finalize_workout

async def auto_finish_workouts(llm=None):
    """
    Automatically finishes workouts that have been inactive for a certain period.
    
    Args:
        llm: Optional language model for inference
    """
    # Define the inactivity threshold (1.5 hours)
    inactivity_threshold = datetime.now(timezone.utc) - timedelta(hours=1.5)
    
    async with db_session() as db:
        # Find unfinished workouts with last exercise log older than the threshold
        subquery = (
            select(ExerciseLog.workout_id, ExerciseLog.exercise_date.label("last_activity"))
            .order_by(ExerciseLog.workout_id, ExerciseLog.exercise_date.desc())
            .distinct(ExerciseLog.workout_id)
            .subquery()
        )
        
        query = (
            select(Workout)
            .join(subquery, Workout.id == subquery.c.workout_id)
            .where(
                and_(
                    Workout.is_finished == False,
                    subquery.c.last_activity < inactivity_threshold
                )
            )
        )
        
        result = await db.execute(query)
        inactive_workouts = result.scalars().all()
        
        # Finalize each inactive workout
        for workout in inactive_workouts:
            await finalize_workout(db, workout.id, llm)
            print(f"Auto-finished workout {workout.id} due to inactivity")

async def setup_auto_finish_job(app):
    """
    Sets up the auto-finish job to run periodically.
    
    Args:
        app: FastAPI application instance with llm in state
    """
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    
    scheduler = AsyncIOScheduler()
    
    # Add the job to run every 15 minutes
    scheduler.add_job(
        lambda: auto_finish_workouts(app.state.llm),
        IntervalTrigger(minutes=15)
    )
    
    # Start the scheduler
    scheduler.start()
    
    # Store the scheduler in the app state so it can be shut down properly
    app.state.scheduler = scheduler 