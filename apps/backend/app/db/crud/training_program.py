"""
CRUD operations for training programs.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any

from ..models.training_program import TrainingProgram
from ..models.training_week import TrainingWeek
from ..models.training_session import TrainingSession
from ..models.exercise_block import ExerciseBlock
from ..models.programmed_exercise import ProgrammedExercise
from ..schemas.training_program import (
    TrainingProgramCreate, TrainingProgramUpdate,
    TrainingWeekCreate, TrainingSessionCreate,
    ExerciseBlockCreate, ProgrammedExerciseCreate
)
from typing import cast

async def get_training_program(db: AsyncSession, program_id: int) -> Optional[TrainingProgram]:
    """Get a training program by ID with all related data."""
    query = (
        select(TrainingProgram)
        .options(
            selectinload(TrainingProgram.training_weeks)
            .selectinload(TrainingWeek.training_sessions)
            .selectinload(TrainingSession.exercise_blocks)
            .selectinload(ExerciseBlock.programmed_exercises)
            .selectinload(ProgrammedExercise.standard_exercise)
        )
        .filter(TrainingProgram.id == program_id)
    )
    result = await db.execute(query)
    program = result.scalars().first()
    
    # Si encontramos el programa, agregar los nombres de los ejercicios
    if program:
        for week in program.training_weeks:
            for session in week.training_sessions:
                for block in session.exercise_blocks:
                    for exercise in block.programmed_exercises:
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
        .join(ExerciseBlock, ExerciseBlock.id == ProgrammedExercise.block_id)
        .join(TrainingSession, TrainingSession.id == ExerciseBlock.session_id)
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
    
    # Create weeks
    for week_data in program_data.training_weeks:
        db_week = await create_training_week(db, week_data, cast(int, db_program.id))
    
    await db.commit()
    
    # Reload the program with all relationships
    result = await db.execute(
        select(TrainingProgram)
        .options(
            selectinload(TrainingProgram.training_weeks)
            .selectinload(TrainingWeek.training_sessions)
            .selectinload(TrainingSession.exercise_blocks)
            .selectinload(ExerciseBlock.programmed_exercises)
            .selectinload(ProgrammedExercise.standard_exercise)
        )
        .where(TrainingProgram.id == db_program.id)
    )
    db_program = result.scalar_one()
    
    # Agregar los nombres de los ejercicios
    for week in db_program.training_weeks:
        for session in week.training_sessions:
            for block in session.exercise_blocks:
                for exercise in block.programmed_exercises:
                    if exercise.standard_exercise:
                        exercise.exercise_name = exercise.standard_exercise.standard_name
    
    return db_program

async def create_training_week(
    db: AsyncSession, 
    week_data: TrainingWeekCreate, 
    program_id: int
) -> TrainingWeek:
    """Create a new training week with all related entities."""
    db_week = TrainingWeek(
        program_id=program_id,
        week_number=week_data.week_number,
        description=week_data.description
    )
    db.add(db_week)
    await db.flush()
    
    # Create sessions
    for session_data in week_data.training_sessions:
        db_session = await create_training_session(db, session_data, cast(int, db_week.id))
    
    return db_week

async def create_training_session(
    db: AsyncSession, 
    session_data: TrainingSessionCreate, 
    week_id: int
) -> TrainingSession:
    """Create a new training session with all related entities."""
    db_session = TrainingSession(
        week_id=week_id,
        name=session_data.name,
        day_of_week=session_data.day_of_week,
        session_order=session_data.session_order,
        description=session_data.description
    )
    db.add(db_session)
    await db.flush()
    
    # Create blocks
    for block_data in session_data.exercise_blocks:
        db_block = await create_exercise_block(db, block_data, cast(int, db_session.id))
    
    return db_session

async def create_exercise_block(
    db: AsyncSession, 
    block_data: ExerciseBlockCreate, 
    session_id: int
) -> ExerciseBlock:
    """Create a new exercise block with all related entities."""
    db_block = ExerciseBlock(
        session_id=session_id,
        name=block_data.name,
        block_type=block_data.block_type,
        order=block_data.order,
        description=block_data.description
    )
    db.add(db_block)
    await db.flush()
    
    # Create exercises
    for exercise_data in block_data.programmed_exercises:
        db_exercise = await create_programmed_exercise(db, exercise_data, cast(int, db_block.id))
    
    return db_block

async def create_programmed_exercise(
    db: AsyncSession, 
    exercise_data: ProgrammedExerciseCreate, 
    block_id: int
) -> ProgrammedExercise:
    """Create a new programmed exercise."""
    db_exercise = ProgrammedExercise(
        block_id=block_id,
        standard_exercise_id=exercise_data.standard_exercise_id,
        tempo=exercise_data.tempo,
        sets=exercise_data.sets,
        reps=exercise_data.reps,
        load_type=exercise_data.load_type,
        rpe_target=exercise_data.rpe_target,
        percentage_1rm=exercise_data.percentage_1rm,
        weight_range=exercise_data.weight_range,
        rest_seconds=exercise_data.rest_seconds,
        sets_type=exercise_data.sets_type,
        custom_parameters=exercise_data.custom_parameters
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
    query = delete(TrainingProgram).where(TrainingProgram.id == program_id)
    result = await db.execute(query)
    await db.commit()
    
    return result.rowcount > 0

# Additional CRUD operations for individual components
async def get_training_week(db: AsyncSession, week_id: int) -> Optional[TrainingWeek]:
    """Get a training week by ID with all related data."""
    query = (
        select(TrainingWeek)
        .options(
            selectinload(TrainingWeek.training_sessions)
            .selectinload(TrainingSession.exercise_blocks)
            .selectinload(ExerciseBlock.programmed_exercises)
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
            selectinload(TrainingSession.exercise_blocks)
            .selectinload(ExerciseBlock.programmed_exercises)
        )
        .filter(TrainingSession.id == session_id)
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_exercise_block(db: AsyncSession, block_id: int) -> Optional[ExerciseBlock]:
    """Get an exercise block by ID with all related data."""
    query = (
        select(ExerciseBlock)
        .options(selectinload(ExerciseBlock.programmed_exercises))
        .filter(ExerciseBlock.id == block_id)
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_programmed_exercise(db: AsyncSession, exercise_id: int) -> Optional[ProgrammedExercise]:
    """Get a programmed exercise by ID."""
    query = select(ProgrammedExercise).filter(ProgrammedExercise.id == exercise_id)
    result = await db.execute(query)
    return result.scalars().first() 