"""
Excepciones personalizadas para la aplicación.
"""

from .auth import AuthException, InvalidCredentialsException, UserExistsException
from .api import APIException, RateLimitException, ValidationException

__all__ = [
    "AuthException",
    "InvalidCredentialsException",
    "UserExistsException",
    "APIException",
    "RateLimitException",
    "ValidationException"
] 