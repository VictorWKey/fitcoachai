"""
Módulo de acceso a datos para FitCoach AI.
Proporciona acceso a modelos, esquemas y operaciones CRUD.
"""

from .base import Base, engine
# Avoid circular imports by not importing everything at module level
# from .models import *
from .session import db_session

async def init_db():
    """
    Inicializa la base de datos, creando todas las tablas definidas en los modelos.
    Este método debe ser llamado durante el inicio de la aplicación.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Inicializar datos de ejercicios estándar
    print("Inicializando ejercicios estándar...")
    
    # Import here to avoid circular imports
    from .init_data import load_exercises_from_json
    
    async with db_session() as session:
        try:
            await load_exercises_from_json(session)
        except Exception as e:
            print(f"Error al inicializar ejercicios: {e}")
