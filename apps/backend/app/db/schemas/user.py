from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re
from db.models.workout import TrainingDiscipline

# Base schema for User
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    preferred_discipline: TrainingDiscipline = TrainingDiscipline.HYPERTROPHY
    is_active: bool = True

# Schema for creating a User
class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        """
        Validates that the password meets complexity requirements.
        
        The password must:
        - Be at least 8 characters long
        - Contain at least one uppercase letter
        - Contain at least one lowercase letter
        - Contain at least one digit
        - Contain at least one special character from the following set: !@#$%^&*(),.?":{}|<>
        
        Args:
            v (str): The password value to validate.
        
        Raises:
            ValueError: If any of the password complexity conditions are not met.
        
        Returns:
            str: The validated password.
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

# Schema for updating a User
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    preferred_discipline: Optional[TrainingDiscipline] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        """
        Validates that the password meets complexity requirements (same as in UserCreate).
        
        Args:
            v (str): The password value to validate.
        
        Raises:
            ValueError: If any of the password complexity conditions are not met.
        
        Returns:
            str: The validated password, or None if not provided.
        """
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v

# Schema for User in the database
class UserInDB(UserBase):
    id: int
    hashed_password: str
    has_chat_history: bool = False
    system_message_needs_update: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Schema for User response
class User(UserBase):
    id: int
    has_chat_history: bool = False
    system_message_needs_update: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Schema for password reset
class PasswordReset(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, values):
        """
        Validates that the new password and confirm password match.
        
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
        Validates that the new password meets complexity requirements (same as in UserCreate).
        
        Args:
            v (str): The password value to validate.
        
        Raises:
            ValueError: If any of the password complexity conditions are not met.
        
        Returns:
            str: The validated new password.
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v
