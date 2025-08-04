"""
CRUD operations for Training Sessions.
Manages active training sessions and exercise logging.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from db.models.training_session import TrainingSession, SessionStatus
from db.models.exercise_block import ExerciseBlock
from db.models.user import User

class TrainingSessionNotFoundError(Exception):
    """Raised when a training session is not found."""
    pass

class NoActiveSessionError(Exception):
    """Raised when no active session is found for logging."""
    pass

class SessionAlreadyActiveError(Exception):
    """Raised when trying to start a session while another is active."""
    pass

async def get_active_session_for_user(db: AsyncSession, user_id: int) -> Optional[TrainingSession]:
    """
    Get the currently active training session for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        TrainingSession if active, None otherwise
    """
    result = await db.execute(
        select(TrainingSession)
        .where(
            TrainingSession.user_id == user_id,
            TrainingSession.session_status == SessionStatus.ACTIVE
        )
        .options(
            selectinload(TrainingSession.exercise_blocks),
            selectinload(TrainingSession.strength_logs),
            selectinload(TrainingSession.cardio_logs)
        )
    )
    return result.scalar_one_or_none()

async def start_training_session(
    db: AsyncSession, 
    user_id: int, 
    session_id: int
) -> TrainingSession:
    """
    Start a training session for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        session_id: ID of the training session to start
        
    Returns:
        The activated training session
        
    Raises:
        TrainingSessionNotFoundError: If session doesn't exist
        SessionAlreadyActiveError: If user already has an active session
    """
    # Check if user already has an active session
    existing_active = await get_active_session_for_user(db, user_id)
    if existing_active:
        raise SessionAlreadyActiveError(
            f"User already has an active session: {existing_active.name}"
        )
    
    # Get the session to activate
    result = await db.execute(
        select(TrainingSession)
        .where(TrainingSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise TrainingSessionNotFoundError(f"Training session {session_id} not found")
    
    # Activate the session using update
    now = datetime.now(timezone.utc)
    await db.execute(
        update(TrainingSession)
        .where(TrainingSession.id == session_id)
        .values(
            user_id=user_id,
            session_status=SessionStatus.ACTIVE,
            session_start_time=now,
            session_end_time=None,
            session_duration_seconds=None
        )
    )
    
    await db.commit()
    
    # Refresh and return the session
    result = await db.execute(
        select(TrainingSession)
        .where(TrainingSession.id == session_id)
        .options(
            selectinload(TrainingSession.exercise_blocks),
            selectinload(TrainingSession.strength_logs),
            selectinload(TrainingSession.cardio_logs)
        )
    )
    
    return result.scalar_one()

async def finish_training_session(
    db: AsyncSession, 
    user_id: int,
    session_id: Optional[int] = None,
    frontend_duration_seconds: Optional[int] = None
) -> TrainingSession:
    """
    Finish the currently active training session for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        session_id: Optional specific session ID to finish
        frontend_duration_seconds: Optional duration calculated by frontend for timer-based sessions
        
    Returns:
        The finished training session
        
    Raises:
        NoActiveSessionError: If no active session found
        TrainingSessionNotFoundError: If specific session not found or not active
    """
    if session_id:
        # Finish specific session
        result = await db.execute(
            select(TrainingSession)
            .where(
                TrainingSession.id == session_id,
                TrainingSession.user_id == user_id,
                TrainingSession.session_status == SessionStatus.ACTIVE
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise TrainingSessionNotFoundError(
                f"Active session {session_id} not found for user {user_id}"
            )
        target_session_id = session_id
    else:
        # Finish any active session
        session = await get_active_session_for_user(db, user_id)
        if not session:
            raise NoActiveSessionError(f"No active session found for user {user_id}")
        target_session_id = session.id

    # Get session start time for duration calculation
    result = await db.execute(
        select(TrainingSession.session_start_time)
        .where(TrainingSession.id == target_session_id)
    )
    start_time = result.scalar_one_or_none()
    
    # Calculate session metrics
    now = datetime.now(timezone.utc)
    
    # Use frontend duration if provided, otherwise calculate from timestamps
    if frontend_duration_seconds is not None:
        # Frontend calculated duration (timer-based sessions)
        duration_seconds = frontend_duration_seconds
    else:
        # Calculate duration from timestamps (traditional sessions)
        duration_seconds = None
        if start_time:
            duration = now - start_time
            duration_seconds = int(duration.total_seconds())
    
    # Complete the session using update
    await db.execute(
        update(TrainingSession)
        .where(TrainingSession.id == target_session_id)
        .values(
            session_status=SessionStatus.COMPLETED,
            session_end_time=now,
            session_duration_seconds=duration_seconds,
            user_id=None
        )
    )
    
    await db.commit()
    
    # Return the updated session
    result = await db.execute(
        select(TrainingSession)
        .where(TrainingSession.id == target_session_id)
        .options(
            selectinload(TrainingSession.strength_logs),
            selectinload(TrainingSession.cardio_logs)
        )
    )
    
    return result.scalar_one()

async def get_user_session_history(
    db: AsyncSession, 
    user_id: int,
    limit: int = 10,
    offset: int = 0
) -> List[TrainingSession]:
    """
    Get the history of completed training sessions for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of sessions to return
        offset: Number of sessions to skip
        
    Returns:
        List of completed training sessions
    """
    result = await db.execute(
        select(TrainingSession)
        .where(
            TrainingSession.session_status == SessionStatus.COMPLETED
        )
        .join(TrainingSession.strength_logs)
        .filter(TrainingSession.strength_logs.any(user_id=user_id))
        .options(
            selectinload(TrainingSession.strength_logs),
            selectinload(TrainingSession.cardio_logs)
        )
        .order_by(TrainingSession.session_end_time.desc())
        .limit(limit)
        .offset(offset)
    )
    
    return list(result.scalars().all())

async def get_session_with_exercises(
    db: AsyncSession,
    session_id: int
) -> Optional[TrainingSession]:
    """
    Get a training session with all its exercise blocks and logs.
    
    Args:
        db: Database session
        session_id: ID of the training session
        
    Returns:
        TrainingSession with related data loaded
    """
    result = await db.execute(
        select(TrainingSession)
        .where(TrainingSession.id == session_id)
        .options(
            selectinload(TrainingSession.exercise_blocks).selectinload(ExerciseBlock.programmed_exercises),
            selectinload(TrainingSession.strength_logs),
            selectinload(TrainingSession.cardio_logs),
            selectinload(TrainingSession.training_week)
        )
    )
    
    return result.scalar_one_or_none()


# ============================================================================
# SESSION STATUS MANAGEMENT
# ============================================================================


async def abandon_session(db: AsyncSession, session_id: int, user_id: int) -> TrainingSession:
    """
    Mark a session as abandoned (not completed).
    
    Args:
        db: Database session
        session_id: ID of the training session
        user_id: ID of the user
        
    Returns:
        Updated TrainingSession
    """
    from db.models.training_session import SessionStatus
    
    result = await db.execute(
        select(TrainingSession)
        .where(
            TrainingSession.id == session_id,
            TrainingSession.user_id == user_id,
            TrainingSession.session_status == SessionStatus.ACTIVE
        )
    )
    
    session = result.scalar_one_or_none()
    if not session:
        raise TrainingSessionNotFoundError("Active session not found")
    
    # Calculate total duration
    total_duration_seconds = 0
    if session.session_start_time is not None:
        total_duration = datetime.now(timezone.utc) - session.session_start_time
        total_duration_seconds = int(total_duration.total_seconds()) - (session.total_pause_duration_seconds or 0)
    
    await db.execute(
        update(TrainingSession)
        .where(TrainingSession.id == session_id)
        .values(
            session_status=SessionStatus.ABANDONED,
            session_end_time=datetime.now(timezone.utc),
            session_duration_seconds=total_duration_seconds
        )
    )
    
    await db.commit()
    
    # Return updated session
    result = await db.execute(
        select(TrainingSession)
        .where(TrainingSession.id == session_id)
    )
    return result.scalar_one()


async def get_inactive_sessions(db: AsyncSession, inactive_minutes: int = 20) -> List[TrainingSession]:
    """
    Get sessions that have been inactive for more than specified minutes.
    
    Args:
        db: Database session
        inactive_minutes: Minutes of inactivity to consider
        
    Returns:
        List of inactive TrainingSession objects
    """
    from db.models.training_session import SessionStatus
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=inactive_minutes)
    
    result = await db.execute(
        select(TrainingSession)
        .where(
            TrainingSession.session_status == SessionStatus.ACTIVE,
        )
    )
    
    return list(result.scalars().all())


async def get_long_running_sessions(db: AsyncSession, hours_limit: int = 24) -> List[TrainingSession]:
    """
    Get sessions that have been running for more than specified hours.
    
    Args:
        db: Database session
        hours_limit: Hours limit to consider sessions as long-running
        
    Returns:
        List of long-running TrainingSession objects
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_limit)
    
    result = await db.execute(
        select(TrainingSession)
        .where(
            TrainingSession.session_status == SessionStatus.ACTIVE,
            TrainingSession.session_start_time < cutoff_time
        )
    )
    
    return list(result.scalars().all())
