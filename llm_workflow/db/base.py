from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


raw_db_url = os.getenv("DATABASE_URL")
if raw_db_url and '+asyncpg' not in raw_db_url:
    if raw_db_url.startswith('postgresql:'):
        DATABASE_URL = raw_db_url.replace('postgresql:', 'postgresql+asyncpg:', 1)
    else:
        DATABASE_URL = raw_db_url
else:
    DATABASE_URL = raw_db_url

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=6,
    pool_timeout=30,
    pool_recycle=1800,
)

Base = declarative_base()

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
