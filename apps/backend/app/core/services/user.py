from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.user import User
from db.schemas.user import UserCreate
from db.crud.user import get_password_hash, verify_password, get_user_by_username
from exceptions.auth import (
    UserExistsException,
    InvalidCredentialsException,
    AccountLockedException
)
from config.security_settings import security_settings
import logging

logger = logging.getLogger(__name__)

class CoreUserService:
    """
    Service for handling business logic related to users.
    """
    
    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate,
        verification_token: Optional[str] = None,
        verification_token_expires: Optional[datetime] = None
    ) -> User:
        """
        Creates a new user in the database.
        
        Args:
            db: Database session
            user_data: Data of the user to create
            verification_token: Optional verification token
            verification_token_expires: Expiration date of the token
            
        Returns:
            The created user
            
        Raises:
            UserExistsException: If the user already exists
        """
        # Check if the email already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalars().first():
            raise UserExistsException(f"The email {user_data.email} is already registered")

        # Check if the username already exists
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalars().first():
            raise UserExistsException(f"The username {user_data.username} is already in use")

        # Create the user
        hashed_password = get_password_hash(user_data.password)
        
        # Create the user with the verification token
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            created_at=datetime.now(timezone.utc),
            is_active=True,
            is_verified=False,
            verification_token=verification_token,
            verification_token_expires=verification_token_expires
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return db_user
    
    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username_or_email: str,
        password: str
    ) -> Tuple[Optional[User], bool]:
        """
        Authenticates a user.
        
        Args:
            db: Database session
            username_or_email: Username or email
            password: User's password
            
        Returns:
            Tuple (user, is_valid)
            
        Raises:
            InvalidCredentialsException: If the credentials are invalid
            AccountLockedException: If the account is locked
        """

        # Look for user by email or username
        stmt = select(User).where(
            (User.email == username_or_email) | (User.username == username_or_email)
        )
        result = await db.execute(stmt)
        user = result.scalars().first()

        
        if not user or not user.is_active:
            raise InvalidCredentialsException("Incorrect username or password")

        logger.info(f"User authenticated: {user.username}")
        
        # Check if the account is locked
        if user.failed_login_attempts >= security_settings.MAX_LOGIN_ATTEMPTS:
            if user.account_locked_until and user.account_locked_until > datetime.now(timezone.utc):
                lockout_minutes = (user.account_locked_until - datetime.now(timezone.utc)).seconds // 60
                logger.warning(f"Login attempt on locked account: {user.username}")
                raise AccountLockedException(
                    f"Account locked due to too many failed attempts. Try again in {lockout_minutes} minutes."
                )
            else:
                # Reset failed attempts if the lockout period has passed
                user.failed_login_attempts = 0
                user.account_locked_until = None
                await db.commit()
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed attempts counter
            user.failed_login_attempts += 1
            user.last_failed_login = datetime.now(timezone.utc)
            
            # Lock the account if the limit is exceeded
            if user.failed_login_attempts >= security_settings.MAX_LOGIN_ATTEMPTS:
                user.account_locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=security_settings.ACCOUNT_LOCKOUT_MINUTES
                )
                logger.warning(f"Account locked due to multiple failed attempts: {user.username}")
                
            await db.commit()
            raise InvalidCredentialsException("Incorrect username or password")


            
        # Reset failed attempts on successful login
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            user.last_failed_login = None
            user.account_locked_until = None
            await db.commit()


            
        return user, True
        
    @staticmethod
    async def get_user_profile(db: AsyncSession, user_id: int) -> Optional[User]:
        """
        Gets the full profile of a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User or None if not found
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
        
    @staticmethod
    async def update_user_profile(
        db: AsyncSession, 
        user_id: int, 
        update_data: dict
    ) -> Optional[User]:
        """
        Updates a user's profile.
        
        Args:
            db: Database session
            user_id: User ID
            update_data: Data to update
            
        Returns:
            Updated user or None if not found
        """
        user = await CoreUserService.get_user_profile(db, user_id)
        if not user:
            return None
            
        # Update allowed fields
        allowed_fields = {'name', 'bio', 'preferences', 'avatar_url'}
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
