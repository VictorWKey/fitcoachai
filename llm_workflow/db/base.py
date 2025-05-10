from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
  DATABASE_URL,
  pool_size=5,
  max_overflow=5,
  pool_timeout=30,
  pool_recycle=1800,
  )

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)