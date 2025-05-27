"""
Exceptions related to authentication and authorization.
"""

from fastapi import HTTPException, status

class AuthException(HTTPException):
    """Base exception for authentication and authorization errors."""
    def __init__(self, detail: str = "Authentication error", status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)

class InvalidCredentialsException(AuthException):
    """Exception for invalid credentials."""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class UserExistsException(AuthException):
    """Exception for when a user already exists."""
    def __init__(self, detail: str = "User already exists"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)

class TokenExpiredException(AuthException):
    """Exception for expired tokens."""
    def __init__(self, detail: str = "Token expired"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class InvalidTokenException(AuthException):
    """Exception for invalid tokens."""
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)

class NotVerifiedException(AuthException):
    """Exception for unverified users."""
    def __init__(self, detail: str = "User not verified"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)

class AccountLockedException(AuthException):
    """Exception for locked accounts."""
    def __init__(self, detail: str = "Account locked"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)
