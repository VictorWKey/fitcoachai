#!/usr/bin/env python3
"""
Script de prueba para verificar el ordenamiento automático.
Este script simula la creación de un programa sin especificar campos de orden.
"""

import json
import sys
from pathlib import Path

def test_auto_ordering():
    """Test que verifica que el JSON no contenga campos de orden."""
    
    # Cargar el archivo de prueba
    test_file = Path(__file__).parent / "test_auto_ordering.json"
    
    if not test_file.exists():
        print("❌ Archivo test_auto_ordering.json no encontrado")
        return False
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            program_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
        return False
    
    print("🧪 Verificando que NO se especifiquen campos de orden...")
    
    # Verificar weeks
    for week_idx, week in enumerate(program_data.get('training_weeks', [])):
        if 'week_number' in week:
            print(f"❌ week_number encontrado en semana {week_idx + 1}")
            return False
        
        # Verificar sessions
        for session_idx, session in enumerate(week.get('training_sessions', [])):
            if 'session_order' in session:
                print(f"❌ session_order encontrado en sesión {session_idx + 1} de semana {week_idx + 1}")
                return False
            
            # Verificar exercises
            for exercise_idx, exercise in enumerate(session.get('programmed_exercises', [])):
                if 'exercise_order' in exercise:
                    print(f"❌ exercise_order encontrado en ejercicio {exercise_idx + 1} de sesión {session_idx + 1}")
                    return False
    
    print("✅ Verificación exitosa: NO se encontraron campos de orden")
    print("\n📊 Resumen del programa:")
    print(f"   - Nombre: {program_data.get('name', 'N/A')}")
    print(f"   - Semanas: {len(program_data.get('training_weeks', []))}")
    
    total_sessions = sum(len(week.get('training_sessions', [])) 
                        for week in program_data.get('training_weeks', []))
    print(f"   - Sesiones totales: {total_sessions}")
    
    total_exercises = sum(
        len(session.get('programmed_exercises', []))
        for week in program_data.get('training_weeks', [])
        for session in week.get('training_sessions', [])
    )
    print(f"   - Ejercicios totales: {total_exercises}")
    
    print("\n🎯 Órdenes que se asignarán automáticamente:")
    for week_idx, week in enumerate(program_data.get('training_weeks', [])):
        print(f"   Semana {week_idx + 1}: week_number = {week_idx + 1}")
        for session_idx, session in enumerate(week.get('training_sessions', [])):
            print(f"     Sesión '{session.get('name', 'Sin nombre')}': session_order = {session_idx}")
            for exercise_idx, exercise in enumerate(session.get('programmed_exercises', [])):
                print(f"       Ejercicio ID {exercise.get('standard_exercise_id', 'N/A')}: exercise_order = {exercise_idx}")
    
    return True

def simulate_api_request():
    """Simula cómo se vería la petición al API."""
    
    test_file = Path(__file__).parent / "test_auto_ordering.json"
    
    with open(test_file, 'r', encoding='utf-8') as f:
        program_data = json.load(f)
    
    print("\n🚀 Simulación de petición API:")
    print("POST /api/v1/training/programs")
    print("Content-Type: application/json")
    print("Authorization: Bearer <token>")
    print("\nPayload (resumido):")
    print(f"{{")
    print(f'  "name": "{program_data["name"]}",')
    print(f'  "program_type": "{program_data["program_type"]}",')
    print(f'  "duration_weeks": {program_data["duration_weeks"]},')
    print(f'  "training_weeks": [')
    
    for week_idx, week in enumerate(program_data.get('training_weeks', [])):
        print(f'    {{ // Semana {week_idx + 1} (week_number se calculará automáticamente)')
        print(f'      "description": "{week.get("description", "")}",')
        print(f'      "training_sessions": [')
        
        for session_idx, session in enumerate(week.get('training_sessions', [])):
            print(f'        {{ // Sesión {session_idx + 1} (session_order se calculará automáticamente)')
            print(f'          "name": "{session.get("name", "")}",')
            exercise_count = len(session.get('programmed_exercises', []))
            print(f'          "programmed_exercises": [...] // {exercise_count} ejercicios (exercise_order automático)')
            print(f'        }}{"," if session_idx < len(week.get("training_sessions", [])) - 1 else ""}')
        
        print(f'      ]')
        print(f'    }}{"," if week_idx < len(program_data.get("training_weeks", [])) - 1 else ""}')
    
    print(f'  ]')
    print(f'}}')

if __name__ == "__main__":
    print("🧪 Test de Ordenamiento Automático")
    print("=" * 50)
    
    if test_auto_ordering():
        simulate_api_request()
        print("\n✅ El programa está listo para probar con el backend!")
        print("💡 Para probar realmente, ejecuta:")
        print("   curl -X POST 'http://localhost:8000/api/v1/training/programs' \\")
        print("        -H 'Authorization: Bearer <tu_token>' \\")
        print("        -H 'Content-Type: application/json' \\")
        print("        -d @test_auto_ordering.json")
    else:
        print("\n❌ Test falló")
        sys.exit(1)
