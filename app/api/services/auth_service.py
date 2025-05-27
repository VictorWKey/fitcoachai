from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple
import secrets
import uuid
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.user import get_user_by_email, get_user_by_username, get_user, verify_password
from db.schemas.token import TokenData, Token, TokenBlacklist as TokenBlacklistSchema
from db.models.token import TokenBlacklist
from db.session import get_db
from db.models.user import User
from core.services.auth_service import AuthService
from core.services.user_service import UserService
from exceptions.auth_exceptions import (
    InvalidCredentialsException, 
    InvalidTokenException,
    NotVerifiedException
)
from config.security_settings import security_settings

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# JWT Configuration
SECRET_KEY = security_settings.SECRET_KEY
if not SECRET_KEY:
    raise RuntimeError("No SECRET_KEY set in environment variables")
    
ALGORITHM = security_settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = security_settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = security_settings.REFRESH_TOKEN_EXPIRE_DAYS
MAX_LOGIN_ATTEMPTS = security_settings.MAX_LOGIN_ATTEMPTS
ACCOUNT_LOCKOUT_MINUTES = security_settings.ACCOUNT_LOCKOUT_MINUTES

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Tuple[Optional[User], bool]:
    """
    Authenticate a user.

    Args:
        db: Database session.
        username: Username or email.
        password: User's password.

    Returns:
        Tuple (user, is_valid).
    """
    try:
        return await UserService.authenticate_user(db, username, password)
    except (InvalidCredentialsException, HTTPException) as e:
        logger.warning(f"Failed login attempt for user: {username}")
        if isinstance(e, InvalidCredentialsException):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        raise e

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    """
    Get the current authenticated user from the JWT token.

    Args:
        token: JWT token.
        db: Database session.

    Returns:
        User: Authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = AuthService.decode_token(token)
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if user_id is None or jti is None:
            raise credentials_exception
        
        await AuthService.verify_token_not_blacklisted(db, jti)
            
        token_data = TokenData(sub=int(user_id), jti=jti)
        
    except (InvalidTokenException, JWTError) as e:
        logger.error(f"Error verifying token: {e}")
        raise credentials_exception

    user = await get_user(db, user_id=token_data.sub)
    if user is None:
        logger.warning(f"User not found: ID {token_data.sub}")
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        
    return user

async def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current user and verify their email.

    Args:
        current_user: Authenticated user.

    Returns:
        User: Authenticated and verified user.

    Raises:
        HTTPException: If the user's email is not verified.
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email."
        )
    return current_user

async def check_user_exists(db: AsyncSession, email: str, username: str) -> None:
    """
    Check if a user with the given email or username already exists.

    Args:
        db: Database session.
        email: Email to check.
        username: Username to check.

    Raises:
        HTTPException: If the user already exists.
    """
    db_user = await get_user_by_email(db, email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = await get_user_by_username(db, username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

