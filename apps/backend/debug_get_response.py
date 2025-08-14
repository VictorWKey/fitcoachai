#!/usr/bin/env python3
"""
Script para debug: revisar qué campos se devuelven en el GET de un programa.
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, '/home/victorwkey/desktop/fitcoachai/apps/backend')

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.crud.training_program import get_training_program

async def debug_get_response():
    """Debug function to check what fields are returned in GET response."""
    async with AsyncSessionLocal() as db:
        try:
            # Get program with ID 1 (assuming it exists)
            program = await get_training_program(db, 1)
            
            if program:
                print("=== PROGRAM DEBUG INFO ===")
                print(f"Program ID: {program.id}")
                print(f"Program Name: {program.name}")
                
                for week in program.training_weeks:
                    print(f"\nWeek {week.week_number} (ID: {week.id}):")
                    
                    for session in week.training_sessions:
                        print(f"  Session: {session.name} (ID: {session.id})")
                        
                        for exercise in session.programmed_exercises:
                            print(f"    Exercise ID: {exercise.id}")
                            print(f"    Standard Exercise ID: {exercise.standard_exercise_id}")
                            print(f"    Exercise Name: {getattr(exercise, 'exercise_name', 'NOT SET')}")
                            print(f"    Block: {exercise.block}")
                            print(f"    Standard Exercise Object: {exercise.standard_exercise}")
                            if exercise.standard_exercise:
                                print(f"    Standard Exercise Name: {exercise.standard_exercise.standard_name}")
                            print("    ---")
            else:
                print("No program found with ID 1")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_get_response())
