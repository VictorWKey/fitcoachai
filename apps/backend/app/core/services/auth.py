"""
Core authentication service for FitCoach AI.

Handles JWT token creation, validation, and management including
access tokens, refresh tokens, and token blacklisting.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Dict, Any
import secrets
import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from db.models.user import User
from db.models.token import TokenBlacklist
from db.schemas.token import TokenData
from exceptions.auth import (
    InvalidCredentialsException,
    InvalidTokenException,
    TokenExpiredException
)
from config.security_settings import security_settings
from typing import cast

logger = logging.getLogger(__name__)

class CoreAuthService:
    """
    Service for handling authentication and token management.
    """
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=security_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
        return jwt.encode(to_encode, security_settings.SECRET_KEY, algorithm=security_settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Creates a JWT refresh token.
        
        Args:
            data: Data to encode in the token
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=security_settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
        return jwt.encode(to_encode, security_settings.SECRET_KEY, algorithm=security_settings.ALGORITHM)

    @staticmethod
    def generate_verification_token() -> str:
        """
        Generates a random token for email verification or password reset.
        
        Returns:
            Unique and secure token
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        Decodes a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Token payload
            
        Raises:
            InvalidTokenException: If the token is invalid
        """
        try:
            payload = jwt.decode(
                token, 
                security_settings.SECRET_KEY, 
                algorithms=[security_settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"Error decoding token: {e}")
            raise InvalidTokenException("Invalid or tampered token")

    @staticmethod
    async def verify_token_not_blacklisted(db: AsyncSession, jti: str) -> bool:
        """
        Verifies that a token is not blacklisted.
        
        Args:
            db: Database session
            jti: Unique token identifier
            
        Returns:
            True if the token is not blacklisted
            
        Raises:
            InvalidTokenException: If the token is blacklisted
        """
        result = await db.execute(select(TokenBlacklist).where(TokenBlacklist.jti == jti))
        blacklisted_token = result.scalar_one_or_none()
        
        if blacklisted_token:
            raise InvalidTokenException("Revoked or expired token")
        
        return True

    @staticmethod
    async def revoke_token(db: AsyncSession, token: str) -> bool:
        """
        Adds a token to the blacklist.
        
        Args:
            db: Database session
            token: Token to revoke
            
        Returns:
            True if the operation was successful
        """
        try:
            payload = jwt.decode(
                token, 
                security_settings.SECRET_KEY, 
                algorithms=[security_settings.ALGORITHM]
            )
            jti = payload.get("jti")
            exp = datetime.fromtimestamp(cast(float, payload.get("exp")), tz=timezone.utc)
            
            if not jti:
                return False
                
            token_blacklist = TokenBlacklist(jti=jti, exp=exp)
            db.add(token_blacklist)
            await db.commit()
            return True
        except JWTError:
            return False

    @staticmethod
    async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> bool:
        """
        Revokes all tokens for a user.
        
        Args:
            db: Database session
            user_id: User's ID
            
        Returns:
            True if the operation was successful
        """
        try:
            # TODO
            logger.info(f"Revoking all tokens for user {user_id}")
            # In a complete implementation, all active tokens for the user would be added to the blacklist here.
            # For now, it's just a log.
            return True
        except Exception as e:
            logger.error(f"Error revoking user tokens: {str(e)}")
            return False
