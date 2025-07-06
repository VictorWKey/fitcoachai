"""
Token schemas for the FitCoach AI application.

This module contains Pydantic schemas for JWT token management including:
- Token response schemas for authentication
- Token data schemas for payload validation
- Token blacklist schemas for logout functionality
- Request schemas for token operations
"""

# schemas/token.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """
    Schema for JWT token response.
    
    Contains access and refresh tokens with token type information.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Schema for JWT token payload data.
    
    Contains subject (user ID), JWT ID, and expiration time.
    """
    sub: int
    jti: str
    exp: Optional[datetime] = None

class TokenBlacklist(BaseModel):
    """
    Schema for blacklisted tokens.
    
    Used to track invalidated tokens for logout functionality.
    """
    jti: str
    exp: datetime
    created_at: datetime = datetime.now()

class LogoutRequest(BaseModel):
    """
    Schema for logout request payload.
    
    Contains the refresh token to be invalidated.
    """
    refresh_token: str

class RefreshRequest(BaseModel):
    """
    Schema for token refresh request.
    
    Contains the refresh token to generate a new access token.
    """
    refresh_token: str
