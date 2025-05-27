"""
Base configuration for the data access layer.
Defines the connection to the database and the base class for ORM models.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from config.db_settings import db_settings

# Create the asynchronous database engine
engine = create_async_engine(
    db_settings.SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=6,
    pool_timeout=30,
    pool_recycle=1800,
)

# Base class for ORM models
Base = declarative_base()

# Session factory for interacting with the database
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
