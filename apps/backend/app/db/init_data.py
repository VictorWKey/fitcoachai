"""
Script de inicialización de datos para la base de datos.
Carga los ejercicios estándar desde el archivo JSON.
"""

import json
import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path para las importaciones
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
# Use relative imports instead of absolute imports
from .session import db_session
from .crud.standard_exercises import create_standard_exercise, get_standard_exercise_by_name
from .schemas.standard_exercises import StandardExerciseCreate

async def load_exercises_from_json(session: AsyncSession) -> None:
    """
    Carga los ejercicios desde el archivo JSON a la base de datos.
    Solo crea ejercicios que no existan ya.
    """
    # Ruta al archivo JSON
    json_path = Path(__file__).parent.parent / "core" / "exercises_dict.json"
    
    if not json_path.exists():
        print(f"Error: No se encontró el archivo {json_path}")
        return
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            exercises_data = json.load(f)
        
        created_count = 0
        skipped_count = 0
        
        for exercise_data in exercises_data:
            # Verificar si el ejercicio ya existe
            existing_exercise = await get_standard_exercise_by_name(
                session, exercise_data["standard_name"]
            )
            
            if existing_exercise:
                skipped_count += 1
                continue
            
            # Crear el nuevo ejercicio
            try:
                exercise_create = StandardExerciseCreate(
                    standard_name=exercise_data["standard_name"],
                    main_muscle_group=exercise_data["main_muscle_group"],
                    equipment=exercise_data["equipment"],
                    type=exercise_data["type"]
                )
                
                await create_standard_exercise(session, exercise_create)
                created_count += 1
                print(f"✓ Creado: {exercise_data['standard_name']}")
                
            except Exception as e:
                print(f"✗ Error al crear {exercise_data['standard_name']}: {e}")
        
        print(f"\nResumen de inicialización:")
        print(f"- Ejercicios creados: {created_count}")
        print(f"- Ejercicios existentes (omitidos): {skipped_count}")
        print(f"- Total procesados: {len(exercises_data)}")
        
    except Exception as e:
        print(f"Error al cargar ejercicios: {e}")

async def init_database() -> None:
    """
    Función principal para inicializar la base de datos.
    """
    print("Inicializando base de datos con ejercicios estándar...")
    
    async with db_session() as session:
        try:
            await load_exercises_from_json(session)
        except Exception as e:
            print(f"Error en la inicialización: {e}")

if __name__ == "__main__":
    asyncio.run(init_database()) 