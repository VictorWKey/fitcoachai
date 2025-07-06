"""
Security configuration for FitCoach AI.

Manages JWT settings, account security, rate limiting,
CSRF protection, and Redis configuration.
"""

import os
from typing import Optional
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    """Configuration for CSRF protection."""
    secret_key: str = os.getenv("SECRET_KEY", "very_secret_key_for_csrf")
    token_location: Optional[str] = "header"
    cookie_secure: bool = False  # Should be True in production
    cookie_samesite: str = "lax"

class SecuritySettings:
    """Application security configuration."""
    
    # JWT configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "very_secret_key_for_csrf")
    if not SECRET_KEY:
        raise RuntimeError("No SECRET_KEY set in environment variables")
        
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    
    # Account security settings
    MAX_LOGIN_ATTEMPTS: int = 20
    ACCOUNT_LOCKOUT_MINUTES: int = 30
    
    # Rate limiting configuration
    RATE_LIMIT_DEFAULT: int = 10  # requests
    RATE_LIMIT_WINDOW: int = 60  # seconds (1 minute)
    
    # Paths protected by rate limiting
    RATE_LIMIT_PATHS: list = [
        "/auth/login",
        "/auth/register",
        "/auth/forgot-password",
        "/auth/resend-verification"
    ]
    
    # Redis for rate limiting
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # CSRF Settings
    CSRF_SETTINGS = CsrfSettings()

security_settings = SecuritySettings()
