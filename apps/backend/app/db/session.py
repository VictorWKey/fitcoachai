"""
Utilities for database session management.
Provides functions to obtain and manage SQLAlchemy sessions.
"""

from contextlib import asynccontextmanager
from .base import SessionLocal

@asynccontextmanager
async def db_session():
    """
    Manages a database session as a context manager, handling commit and rollback automatically.
    
    Example:
        ```
        async with db_session() as db:
            # Perform database operations
            # The commit is done automatically when exiting the block if there are no exceptions
        ```
    
    Yields:
        AsyncSession: An asynchronous SQLAlchemy session
    """
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise

async def get_db():
    """
    Dependency for FastAPI that provides a database session.
    
    Example:
        ```
        @app.get("/items/")
        async def read_items(db: AsyncSession = Depends(get_db)):
            # Use the db session for database operations
        ```
    
    Yields:
        AsyncSession: An asynchronous SQLAlchemy session
    """
    async with SessionLocal() as db:
        yield db
