"""
Módulo de acceso a datos para FitCoach AI.
Proporciona acceso a modelos, esquemas y operaciones CRUD.
"""

from .base import Base, engine
from .models import *

async def init_db():
    """
    Inicializa la base de datos, creando todas las tablas definidas en los modelos.
    Este método debe ser llamado durante el inicio de la aplicación.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
