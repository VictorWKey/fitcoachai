import os

class DatabaseSettings:
    """Database configuration."""
    
    # Get the database URL from environment variables
    raw_db_url: str = os.getenv("DATABASE_URL")
    
    # URL for SQLAlchemy (with asyncpg driver)
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """URL for SQLAlchemy with the asyncpg driver."""
        if not self.raw_db_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        if '+asyncpg' not in self.raw_db_url and self.raw_db_url.startswith('postgresql:'):
            return self.raw_db_url.replace('postgresql:', 'postgresql+asyncpg:', 1)
        return self.raw_db_url
    
    # URL for psycopg (without asyncpg driver)
    @property
    def PSYCOPG_DATABASE_URL(self) -> str:
        """URL for psycopg without the asyncpg driver."""
        if not self.raw_db_url:
            raise ValueError("DATABASE_URL environment variable not set")
            
        if '+asyncpg' in self.raw_db_url:
            return self.raw_db_url.replace('+asyncpg', '')
        return self.raw_db_url
    
    # Connection configuration
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 6
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 1800
    
    # psycopg configuration
    CONNECTION_KWARGS = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

db_settings = DatabaseSettings()
