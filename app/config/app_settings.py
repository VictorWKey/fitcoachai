import os
from typing import List

class AppSettings:
    """General application settings."""
    
    # Application information
    APP_TITLE: str = "FitCoach AI API"
    APP_DESCRIPTION: str = "API for the FitCoach AI application"
    APP_VERSION: str = "1.0.0"
    
    # Hosts and CORS configuration
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:3000").split(",")
    
    # LLM model configuration
    OLLAMA_API_BASE_URL: str = os.getenv("OLLAMA_API_BASE_URL")
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    
    # Other settings
    WEBSITE_URL: str = os.getenv("WEBSITE_URL", "http://localhost:8000")
    
    # LangSmith (optional)
    LANGSMITH_API_KEY: str = os.getenv("LANGSMITH_API_KEY", "")
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
    
    # OpenAI (for ChatOpenAI)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Workout auto-finish backup job settings
    ENABLE_AUTO_FINISH_JOB: bool = os.getenv("ENABLE_AUTO_FINISH_JOB", "false").lower() == "true"
    AUTO_FINISH_JOB_INTERVAL: int = int(os.getenv("AUTO_FINISH_JOB_INTERVAL", "30"))

settings = AppSettings()
