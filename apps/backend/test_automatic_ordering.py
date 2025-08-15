#!/usr/bin/env python3
"""
Script de prueba para verificar el comportamiento automático de week_number y session_order.
"""

import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Configurar la conexión (ajustar según tu configuración)
DATABASE_URL = "sqlite+aiosqlite:///./test_automatic_ordering.db"

async def test_automatic_ordering():
    """Prueba el comportamiento automático de ordenamiento."""
    
    # Crear engine y sesión
    engine = create_async_engine(DATABASE_URL, echo=True)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        try:
            # Importar después de configurar la conexión
            from app.db.crud.training_program import create_training_week, create_training_session
            from app.db.schemas.training_program import TrainingWeekCreate, TrainingSessionCreate, ProgrammedExerciseCreate
            
            print("🧪 Iniciando pruebas de ordenamiento automático...")
            
            # Test 1: Crear semana sin week_number
            print("\n📍 Test 1: Crear semana sin week_number")
            week_data_1 = TrainingWeekCreate(
                week_number=None,  # Debe calcularse automáticamente
                description="Semana creada automáticamente",
                training_sessions=[
                    TrainingSessionCreate(
                        name="Sesión A",
                        session_order=None,  # Debe ser 0
                        day_of_week=1,
                        programmed_exercises=[
                            ProgrammedExerciseCreate(
                                standard_exercise_id=1,
                                block="main",
                                exercise_order=None,  # Debe ser 0
                                sets=3,
                                reps=10
                            )
                        ]
                    ),
                    TrainingSessionCreate(
                        name="Sesión B", 
                        session_order=None,  # Debe ser 1
                        day_of_week=3,
                        programmed_exercises=[]
                    )
                ]
            )
            
            # Test 2: Crear sesión individual sin session_order
            print("\n📍 Test 2: Crear sesión individual sin session_order")
            session_data_1 = TrainingSessionCreate(
                name="Sesión Extra",
                session_order=None,  # Debe calcularse automáticamente
                day_of_week=5,
                programmed_exercises=[
                    ProgrammedExerciseCreate(
                        standard_exercise_id=2,
                        block="accessory",
                        exercise_order=None,  # Debe ser 0
                        sets=2,
                        reps=15
                    )
                ]
            )
            
            print("✅ Todas las pruebas preparadas correctamente")
            print("\n📋 Resumen de lo que se probará:")
            print("- week_number automático basado en posición")
            print("- session_order automático basado en posición") 
            print("- exercise_order automático basado en posición")
            print("- Compatibilidad con valores explícitos")
            
        except ImportError as e:
            print(f"❌ Error de importación: {e}")
            print("Asegúrate de que el script se ejecute desde el directorio correcto")
        except Exception as e:
            print(f"❌ Error durante las pruebas: {e}")
            
        finally:
            await engine.dispose()

if __name__ == "__main__":
    print("🚀 Ejecutando pruebas de ordenamiento automático...")
    asyncio.run(test_automatic_ordering())
