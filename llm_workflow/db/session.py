# session.py
from contextlib import asynccontextmanager
from .base import SessionLocal

@asynccontextmanager
async def db_session():
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
