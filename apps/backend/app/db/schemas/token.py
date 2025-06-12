# schemas/token.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: int
    jti: str
    exp: Optional[datetime] = None

class TokenBlacklist(BaseModel):
    jti: str
    exp: datetime
    created_at: datetime = datetime.now()

class LogoutRequest(BaseModel):
    """Payload para solicitar logout con el refresh token"""
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str
