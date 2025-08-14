#!/usr/bin/env python3
"""
Script para probar compatibilidad con datos reales de la API.
"""
import asyncio
import json
from pydantic import ValidationError
import sys

from db.session import db_session
from db.crud.training_program import get_training_program
from db.schemas.training_program import TrainingProgramUpdate

async def test_real_api_compatibility():
    """Test compatibility with real API data."""
    
    print("=== TESTING WITH REAL API DATA ===")
    
    try:
        async with db_session() as db:
            # Get real program data
            program = await get_training_program(db, 1)
            
            if not program:
                print("❌ No program found with ID 1")
                return False
            
            print(f"Found program: {program.name}")
            
            # Convert to dict (simulating JSON serialization/deserialization)
            from db.schemas.training_program import TrainingProgramResponse
            
            # Create response schema instance to serialize properly
            response_schema = TrainingProgramResponse.model_validate(program)
            program_dict = response_schema.model_dump()
            
            print(f"Program data keys: {list(program_dict.keys())}")
            print(f"Training weeks count: {len(program_dict.get('training_weeks', []))}")
            
            # Test if this can be used as PUT request body
            try:
                update_schema = TrainingProgramUpdate(**program_dict)
                print("✅ SUCCESS: Real API response is compatible with PUT request schema")
                
                # Check exercises specifically
                for week_idx, week in enumerate(update_schema.training_weeks):
                    print(f"Week {week.week_number} (ID: {week.id}): {len(week.training_sessions)} sessions")
                    for sess_idx, session in enumerate(week.training_sessions):
                        print(f"  Session '{session.name}' (ID: {session.id}): {len(session.programmed_exercises)} exercises")
                        for ex_idx, exercise in enumerate(session.programmed_exercises):
                            print(f"    Exercise {ex_idx} (ID: {exercise.id}): standard_exercise_id={exercise.standard_exercise_id}")
                
                return True
                
            except ValidationError as e:
                print("❌ VALIDATION ERROR: Real API response is NOT compatible")
                print("Errors:")
                for error in e.errors():
                    print(f"  - {error['loc']}: {error['msg']}")
                return False
                
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_real_api_compatibility())
    sys.exit(0 if success else 1)
