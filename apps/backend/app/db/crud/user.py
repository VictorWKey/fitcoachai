"""
CRUD operations for the User model.
Provides functions to create, read, update, and delete users.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from passlib.context import CryptContext
from sqlalchemy import select
from datetime import datetime, timezone

# Configuration for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Generates a secure hash for a password.
    
    Args:
        password: The plain text password
        
    Returns:
        str: The password hash
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies if a password matches its hash.
    
    Args:
        plain_password: The plain text password
        hashed_password: The stored password hash
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Gets a user by their ID.
    
    Args:
        db: Database session
        user_id: ID of the user to find
        
    Returns:
        User: User instance or None if it doesn't exist
    """
    result = await db.get(User, user_id)
    return result

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Gets a user by their email address.
    
    Args:
        db: Database session
        email: Email of the user to find
        
    Returns:
        User: User instance or None if it doesn't exist
    """
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Gets a user by their username.
    
    Args:
        db: Database session
        username: Username to find
        
    Returns:
        User: User instance or None if it doesn't exist
    """
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Gets a paginated list of users.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List[User]: List of users
    """
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    return list(result.scalars().all())

async def create_user(
    db: AsyncSession, 
    user: UserCreate, 
    verification_token: Optional[str] = None,
    verification_token_expires: Optional[datetime] = None
) -> User:
    """
    Creates a new user in the database.
    
    Args:
        db: Database session
        user: User data to create
        verification_token: Email verification token (optional)
        verification_token_expires: Token expiration date (optional)
        
    Returns:
        User: The created user
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires=verification_token_expires,
        failed_login_attempts=0,
        last_failed_login=None,
        account_locked_until=None
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, user_id: int, user: UserUpdate) -> Optional[User]:
    """
    Updates an existing user's data.
    
    Args:
        db: Database session
        user_id: ID of the user to update
        user: Updated user data
        
    Returns:
        User: The updated user or None if it doesn't exist
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Deletes a user from the database.
    
    Args:
        db: Database session
        user_id: ID of the user to delete
        
    Returns:
        bool: True if the user was deleted, False if it didn't exist
    """
    db_user = await get_user(db, user_id)
    if not db_user:
        return False

    await db.delete(db_user)
    await db.commit()
    return True
