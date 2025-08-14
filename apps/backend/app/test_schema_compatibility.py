#!/usr/bin/env python3
"""
Script para probar compatibilidad entre esquemas POST response y PUT request.
"""
import json
from pydantic import ValidationError
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, '/app')

from db.schemas.training_program import TrainingProgramUpdate, TrainingProgramResponse

def test_schema_compatibility():
    """Test that POST response can be used as PUT request body."""
    
    # Simular respuesta típica del POST
    post_response_data = {
        "id": 1,
        "name": "Programa de Prueba",
        "description": "Descripción del programa",
        "program_type": "strength",
        "duration_weeks": 2,
        "is_ai_generated": False,
        "user_id": 1,
        "created_at": "2025-08-14T20:36:11.329706Z",
        "updated_at": "2025-08-14T20:36:11.329706Z",
        "training_weeks": [
            {
                "id": 1,
                "week_number": 1,
                "description": "Semana 1",
                "program_id": 1,
                "created_at": "2025-08-14T20:36:11.329706Z",
                "updated_at": "2025-08-14T20:36:11.329706Z",
                "training_sessions": [
                    {
                        "id": 1,
                        "name": "Sesión Pecho",
                        "day_of_week": 1,
                        "session_order": 0,
                        "description": "Entrenamiento de pecho",
                        "week_id": 1,
                        "session_status": "scheduled",
                        "created_at": "2025-08-14T20:36:11.329706Z",
                        "updated_at": "2025-08-14T20:36:11.329706Z",
                        "programmed_exercises": [
                            {
                                "id": 1,
                                "block": "main",
                                "exercise_order": 0,
                                "tempo": "2-1-2-1",
                                "sets": 4,
                                "reps": 8,
                                "load_type": "rpe",
                                "rpe_target": 8.0,
                                "percentage_1rm": None,
                                "weight_range": None,
                                "rest_seconds": 120,
                                "notes": None,
                                "sets_type": "hypertrophy",
                                "session_id": 1,
                                "standard_exercise_id": 1,
                                "exercise_name": "Press de banca plano",
                                "created_at": "2025-08-14T20:36:11.329706Z",
                                "updated_at": "2025-08-14T20:36:11.329706Z"
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    print("=== TESTING SCHEMA COMPATIBILITY ===")
    
    try:
        # Intentar crear un TrainingProgramUpdate desde la respuesta del POST
        update_schema = TrainingProgramUpdate(**post_response_data)
        print("✅ SUCCESS: POST response is compatible with PUT request schema")
        print(f"Program name: {update_schema.name}")
        print(f"Weeks count: {len(update_schema.training_weeks)}")
        if update_schema.training_weeks:
            print(f"First week sessions: {len(update_schema.training_weeks[0].training_sessions)}")
            if update_schema.training_weeks[0].training_sessions:
                print(f"First session exercises: {len(update_schema.training_weeks[0].training_sessions[0].programmed_exercises)}")
        
        return True
        
    except ValidationError as e:
        print("❌ VALIDATION ERROR: POST response is NOT compatible with PUT request schema")
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
    success = test_schema_compatibility()
    sys.exit(0 if success else 1)
