"""
User schemas for the FitCoach AI application.

This module contains Pydantic schemas for user-related operations including:
- User creation, update, and response models
- Password validation and complexity requirements
- Password reset functionality

All schemas follow the naming convention:
- Base: Base attributes for the model
- Create: Schema for creating new entities
- Update: Schema for updating existing entities
- InDB: Schema representing the database model
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re

def validate_password_complexity(password: str) -> str:
    """
    Validate that the password meets complexity requirements.
    
    The password must:
    - Be at least 8 characters long
    - Contain at least one digit
    
    Args:
        password (str): The password value to validate.
    
    Raises:
        ValueError: If any of the password complexity conditions are not met.
    
    Returns:
        str: The validated password.
    """
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if not re.search(r'[0-9]', password):
        raise ValueError('Password must contain at least one digit')
    return password

# Base schema for User
class UserBase(BaseModel):
    """
    Base schema for user data.
    
    Contains common user fields that are shared across all user schemas.
    """
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

# Schema for creating a User
class UserCreate(UserBase):
    """
    Schema for creating a new user.
    
    Extends the base schema with password field and validation.
    """
    password: str

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        """
        Validate that the password meets complexity requirements.
        
        Args:
            v (str): The password value to validate.
        
        Raises:
            ValueError: If any of the password complexity conditions are not met.
        
        Returns:
            str: The validated password.
        """
        return validate_password_complexity(v)

# Schema for updating a User
class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    
    All fields are optional to allow partial updates.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        """
        Validate that the password meets complexity requirements (same as in UserCreate).
        
        Args:
            v (str): The password value to validate.
        
        Raises:
            ValueError: If any of the password complexity conditions are not met.
        
        Returns:
            str: The validated password, or None if not provided.
        """
        if v is None:
            return v
        return validate_password_complexity(v)

# Schema for User in the database
class UserInDB(UserBase):
    """
    Schema for user data as stored in the database.
    
    Includes sensitive fields like hashed_password and database timestamps.
    """
    id: int
    hashed_password: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Schema for User response
class User(UserBase):
    """
    Schema for user response data.
    
    Safe for API responses, excludes sensitive information like password.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Schema for password reset
class PasswordReset(BaseModel):
    """
    Schema for password reset requests.
    
    Includes token validation and password confirmation.
    """
    token: str
    new_password: str
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, values):
        """
        Validate that the new password and confirm password match.
        
        Args:
            v (str): The confirm password value.
            values (dict): The dictionary of values already processed.
        
        Raises:
            ValueError: If the confirm password does not match the new password.
        
        Returns:
            str: The confirm password if valid.
        """
        if 'new_password' in values.data and v != values.data['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @field_validator('new_password')
    @classmethod
    def password_complexity(cls, v):
        """
        Validate that the new password meets complexity requirements (same as in UserCreate).
        
        Args:
            v (str): The password value to validate.
        
        Raises:
            ValueError: If any of the password complexity conditions are not met.
        
        Returns:
            str: The validated new password.
        """
        return validate_password_complexity(v)
