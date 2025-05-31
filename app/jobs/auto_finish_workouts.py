"""
Job to automatically finish inactive workouts.
This job serves as a backup mechanism to ensure workouts are properly finalized,
even if the primary finalization mechanism in get_or_create_workout_id fails.
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
    This is a backup mechanism for workouts that weren't properly finalized.
    
    Args:
        llm: Optional language model for inference
    """
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
            print(f"Auto-finished workout {workout.id} due to inactivity (backup job)")

async def setup_auto_finish_job(app, enable_job=False, interval_minutes=30):
    """
    Sets up the auto-finish job to run periodically if enabled.
    
    This job is now optional and serves as a backup mechanism to ensure
    workouts are properly finalized. The primary finalization happens
    in get_or_create_workout_id when a user starts a new workout.
    
    Args:
        app: FastAPI application instance with llm in state
        enable_job: Whether to enable the automatic job (default: False)
        interval_minutes: How often to run the job in minutes (default: 30)
    """
    if not enable_job:
        print("Auto-finish workouts job is disabled")
        return
    
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    
    scheduler = AsyncIOScheduler()
    
    scheduler.add_job(
        lambda: auto_finish_workouts(app.state.llm),
        IntervalTrigger(minutes=interval_minutes)
    )
    
    scheduler.start()
    print(f"Auto-finish workouts job scheduled to run every {interval_minutes} minutes")
    
    app.state.scheduler = scheduler 