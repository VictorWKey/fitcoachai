"""
CRUD operations for training programs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any

from ..models.training_program import TrainingProgram
from ..models.training_week import TrainingWeek
from ..models.training_session import TrainingSession
from ..models.programmed_exercise import ProgrammedExercise
from ..schemas.training_program import (
    TrainingProgramCreate, TrainingProgramUpdate,
    TrainingWeekCreate, TrainingSessionCreate,
    ProgrammedExerciseCreate
)
from core.services.exercise_analysis import infer_series_type
from typing import cast
import logging

logger = logging.getLogger(__name__)

async def get_training_program(db: AsyncSession, program_id: int) -> Optional[TrainingProgram]:
    """Get a training program by ID with all related data."""
    query = (
        select(TrainingProgram)
        .options(
            selectinload(TrainingProgram.training_weeks)
            .options(selectinload(TrainingWeek.training_sessions)
                    .options(selectinload(TrainingSession.programmed_exercises)
                            .selectinload(ProgrammedExercise.standard_exercise)))
        )
        .filter(TrainingProgram.id == program_id)
    )
    result = await db.execute(query)
    program = result.scalars().first()
    
    # Si encontramos el programa, agregar los nombres de los ejercicios y ordenar correctamente
    if program:
        # Ordenar las semanas por week_number
        program.training_weeks.sort(key=lambda w: w.week_number)
        
        for week in program.training_weeks:
            # Ordenar las sesiones por session_order
            week.training_sessions.sort(key=lambda s: s.session_order)
            
            for session in week.training_sessions:
                # Ordenar los ejercicios por exercise_order
                session.programmed_exercises.sort(key=lambda e: e.exercise_order or 0)
                
                for exercise in session.programmed_exercises:
                    if exercise.standard_exercise:
                        # Agregar el nombre del ejercicio estándar como exercise_name
                        exercise.exercise_name = exercise.standard_exercise.standard_name
    
    return program

async def get_training_program_simple(db: AsyncSession, program_id: int) -> Optional[TrainingProgram]:
    """Get a training program by ID without loading related data."""
    query = select(TrainingProgram).filter(TrainingProgram.id == program_id)
    result = await db.execute(query)
    return result.scalars().first()

async def get_program_summary(db: AsyncSession, program_id: int) -> Optional[Dict[str, Any]]:
    """Get a summary of a training program with basic statistics."""
    # Get the basic program data
    program = await get_training_program_simple(db, program_id)
    if not program:
        return None
    
    # Count total weeks
    weeks_query = select(TrainingWeek).filter(TrainingWeek.program_id == program_id)
    weeks_result = await db.execute(weeks_query)
    weeks = list(weeks_result.scalars().all())
    total_weeks = len(weeks)
    
    # Count total sessions
    sessions_query = (
        select(TrainingSession)
        .join(TrainingWeek, TrainingWeek.id == TrainingSession.week_id)
        .filter(TrainingWeek.program_id == program_id)
    )
    sessions_result = await db.execute(sessions_query)
    sessions = list(sessions_result.scalars().all())
    total_sessions = len(sessions)
    
    # Count total exercises
    exercises_query = (
        select(ProgrammedExercise)
        .join(TrainingSession, TrainingSession.id == ProgrammedExercise.session_id)
        .join(TrainingWeek, TrainingWeek.id == TrainingSession.week_id)
        .filter(TrainingWeek.program_id == program_id)
    )
    exercises_result = await db.execute(exercises_query)
    exercises = list(exercises_result.scalars().all())
    total_exercises = len(exercises)
    
    # Create a summary object
    summary = {
        **program.__dict__,
        "total_weeks": total_weeks,
        "total_sessions": total_sessions,
        "total_exercises": total_exercises
    }
    
    return summary

async def get_user_training_programs(db: AsyncSession, user_id: int) -> List[TrainingProgram]:
    """Get all training programs for a user."""
    query = (
        select(TrainingProgram)
        .filter(TrainingProgram.user_id == user_id)
        .order_by(TrainingProgram.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())

async def create_training_program(
    db: AsyncSession, 
    program_data: TrainingProgramCreate, 
    user_id: int
) -> TrainingProgram:
    """Create a new training program with all related entities."""
    try:
        logger.info(f"Starting creation of training program '{program_data.name}' for user {user_id}")
        
        # Create the program
        db_program = TrainingProgram(
            user_id=user_id,
            name=program_data.name,
            description=program_data.description,
            program_type=program_data.program_type,
            duration_weeks=program_data.duration_weeks,
            # ...existing code...
            is_ai_generated=program_data.is_ai_generated
        )
        db.add(db_program)
        await db.flush()
        
        logger.info(f"Training program created with ID: {db_program.id}")
        
        # Create weeks
        logger.info(f"Creating {len(program_data.training_weeks)} weeks")
        for i, week_data in enumerate(program_data.training_weeks):
            logger.info(f"Creating week {i+1}: {week_data.week_number}")
            db_week = await create_training_week(db, week_data, cast(int, db_program.id))
            logger.info(f"Week {i+1} created with ID: {db_week.id}")
        
        logger.info("Committing transaction")
        await db.commit()
        
        logger.info("Reloading program with relationships")
        # Reload the program with all relationships
        result = await db.execute(
            select(TrainingProgram)
            .options(
                selectinload(TrainingProgram.training_weeks)
                .selectinload(TrainingWeek.training_sessions)
                .selectinload(TrainingSession.programmed_exercises)
                .selectinload(ProgrammedExercise.standard_exercise)
            )
            .where(TrainingProgram.id == db_program.id)
        )
        db_program = result.scalar_one()
        
        # Agregar los nombres de los ejercicios
        for week in db_program.training_weeks:
            for session in week.training_sessions:
                for exercise in session.programmed_exercises:
                    if exercise.standard_exercise:
                        exercise.exercise_name = exercise.standard_exercise.standard_name
        
        logger.info(f"Training program creation completed successfully. Final ID: {db_program.id}")
        return db_program
        
    except Exception as e:
        logger.error(f"Error creating training program: {str(e)}")
        logger.exception("Full exception traceback:")
        await db.rollback()
        raise

async def create_training_week(
    db: AsyncSession, 
    week_data: TrainingWeekCreate, 
    program_id: int
) -> TrainingWeek:
    """Create a new training week with all related entities."""
    try:
        logger.info(f"Creating training week {week_data.week_number} for program {program_id}")
        
        # Calculate week_number if not provided
        week_number = week_data.week_number
        if week_number is None:
            # Get the highest week_number in the program and add 1
            stmt = select(func.coalesce(func.max(TrainingWeek.week_number), 0)).where(
                TrainingWeek.program_id == program_id
            )
            result = await db.execute(stmt)
            max_week_number = result.scalar()
            week_number = max_week_number + 1
        
        db_week = TrainingWeek(
            program_id=program_id,
            week_number=week_number,
            description=week_data.description
        )
        db.add(db_week)
        await db.flush()
        
        logger.info(f"Training week created with ID: {db_week.id}")
        
        # Create sessions in chronological order (sorted by day_of_week)
        logger.info(f"Creating {len(week_data.training_sessions)} sessions for week {db_week.id}")
        
        # Sort sessions by day_of_week for proper chronological ordering
        sessions_to_create = list(week_data.training_sessions)
        sessions_to_create.sort(key=lambda s: s.day_of_week if s.day_of_week is not None else 999)
        
        for i, session_data in enumerate(sessions_to_create):
            # Set session_order based on chronological position if not provided
            if not hasattr(session_data, 'session_order') or session_data.session_order is None:
                from ..schemas.training_program import TrainingSessionCreate
                session_data_dict = session_data.model_dump() if hasattr(session_data, 'model_dump') else session_data.__dict__.copy()
                session_data_dict['session_order'] = i  # Use chronological position as session_order
                session_data = TrainingSessionCreate(**session_data_dict)
            
            logger.info(f"Creating session {i+1}: {session_data.name} (day {session_data.day_of_week})")
            db_session = await create_training_session(db, session_data, cast(int, db_week.id))
            logger.info(f"Session {i+1} created with ID: {db_session.id}")
        
        logger.info(f"Training week {week_number} creation completed")
        return db_week
        
    except Exception as e:
        logger.error(f"Error creating training week {week_data.week_number}: {str(e)}")
        logger.exception("Full exception traceback:")
        raise

async def create_training_session(
    db: AsyncSession, 
    session_data: TrainingSessionCreate, 
    week_id: int
) -> TrainingSession:
    """Create a new training session with all related entities."""
    try:
        logger.info(f"Creating training session '{session_data.name}' for week {week_id}")
        
        # Calculate session_order if not provided
        session_order = session_data.session_order
        if session_order is None:
            if session_data.day_of_week is not None:
                # Calculate session_order based on chronological position within the week
                # Get all existing sessions in this week to determine the chronological order
                stmt = select(TrainingSession).where(
                    TrainingSession.week_id == week_id
                ).order_by(TrainingSession.day_of_week)
                result = await db.execute(stmt)
                existing_sessions = result.scalars().all()
                
                # Find the chronological position for this day_of_week
                days_in_week = [s.day_of_week for s in existing_sessions if s.day_of_week is not None]
                days_in_week.append(session_data.day_of_week)
                days_in_week.sort()
                
                # The session_order is the position in the sorted days list
                session_order = days_in_week.index(session_data.day_of_week)
            else:
                # Fallback: Get the highest session_order in the week and add 1
                stmt = select(func.coalesce(func.max(TrainingSession.session_order), -1)).where(
                    TrainingSession.week_id == week_id
                )
                result = await db.execute(stmt)
                max_order = result.scalar()
                session_order = max_order + 1
        
        db_session = TrainingSession(
            week_id=week_id,
            name=session_data.name,
            day_of_week=session_data.day_of_week,
            session_order=session_order,
            description=session_data.description
        )
        db.add(db_session)
        await db.flush()
        
        logger.info(f"Training session created with ID: {db_session.id}")
        
        # Create exercises directly
        logger.info(f"Creating {len(session_data.programmed_exercises)} exercises for session {db_session.id}")
        for i, exercise_data in enumerate(session_data.programmed_exercises):
            logger.info(f"Creating exercise {i+1}")
            db_exercise = await create_programmed_exercise(db, exercise_data, cast(int, db_session.id))
            logger.info(f"Exercise {i+1} created with ID: {db_exercise.id}")
        
        logger.info(f"Training session '{session_data.name}' creation completed")
        return db_session
        
    except Exception as e:
        logger.error(f"Error creating training session '{session_data.name}': {str(e)}")
        logger.exception("Full exception traceback:")
        raise

async def create_programmed_exercise(
    db: AsyncSession, 
    exercise_data: ProgrammedExerciseCreate, 
    session_id: int
) -> ProgrammedExercise:
    """Create a new programmed exercise."""
    
    # Calculate exercise_order if not provided
    exercise_order = exercise_data.exercise_order
    if exercise_order is None:
        # Get the highest order in the session and add 1
        stmt = select(func.coalesce(func.max(ProgrammedExercise.exercise_order), -1)).where(
            ProgrammedExercise.session_id == session_id
        )
        result = await db.execute(stmt)
        max_order = result.scalar()
        exercise_order = max_order + 1
    
    # Calculate sets_type automatically if not provided
    calculated_sets_type = exercise_data.sets_type
    if calculated_sets_type is None:
        calculated_sets_type = infer_series_type(
            reps=exercise_data.reps,
            one_rm_percentage=exercise_data.percentage_1rm,
            rpe=exercise_data.rpe_target,
            tempo=exercise_data.tempo,
            rest_time_seconds=exercise_data.rest_seconds
        )
    
    db_exercise = ProgrammedExercise(
        session_id=session_id,
        standard_exercise_id=exercise_data.standard_exercise_id,
        block=exercise_data.block,
        exercise_order=exercise_order,
        tempo=exercise_data.tempo,
        sets=exercise_data.sets,
        reps=exercise_data.reps,
        load_type=exercise_data.load_type,
        rpe_target=exercise_data.rpe_target,
        percentage_1rm=exercise_data.percentage_1rm,
        weight_range=exercise_data.weight_range,
        rest_seconds=exercise_data.rest_seconds,
        sets_type=calculated_sets_type
    )
    db.add(db_exercise)
    await db.flush()
    
    return db_exercise

async def update_training_program(
    db: AsyncSession, 
    program_id: int, 
    program_data: TrainingProgramUpdate
) -> Optional[TrainingProgram]:
    """Update a training program's basic information."""
    # Prepare update data
    update_data = program_data.dict(exclude_unset=True)
    if not update_data:
        return await get_training_program(db, program_id)
    
    # Update the program
    query = (
        update(TrainingProgram)
        .where(TrainingProgram.id == program_id)
        .values(**update_data)
    )
    await db.execute(query)
    await db.commit()
    
    return await get_training_program(db, program_id)

async def delete_training_program(db: AsyncSession, program_id: int) -> bool:
    """Delete a training program and all related entities."""
    # Get the program instance first to trigger cascade deletes
    program = await get_training_program_simple(db, program_id)
    if not program:
        return False
    
    # Delete using the ORM instance to trigger cascade relationships
    await db.delete(program)
    await db.commit()
    
    return True

# Additional CRUD operations for individual components
async def get_training_week(db: AsyncSession, week_id: int) -> Optional[TrainingWeek]:
    """Get a training week by ID with all related data."""
    query = (
        select(TrainingWeek)
        .options(
            selectinload(TrainingWeek.training_sessions)
            .selectinload(TrainingSession.programmed_exercises)
        )
        .filter(TrainingWeek.id == week_id)
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_training_session(db: AsyncSession, session_id: int) -> Optional[TrainingSession]:
    """Get a training session by ID with all related data."""
    query = (
        select(TrainingSession)
        .options(
            selectinload(TrainingSession.programmed_exercises)
            .selectinload(ProgrammedExercise.standard_exercise)
        )
        .filter(TrainingSession.id == session_id)
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_programmed_exercise(db: AsyncSession, exercise_id: int) -> Optional[ProgrammedExercise]:
    """Get a programmed exercise by ID."""
    query = select(ProgrammedExercise).filter(ProgrammedExercise.id == exercise_id)
    result = await db.execute(query)
    return result.scalars().first()
    return result.scalars().first() 