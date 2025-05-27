"""
Excepciones personalizadas para la aplicación.
"""

from .auth_exceptions import AuthException, InvalidCredentialsException, UserExistsException
from .api_exceptions import APIException, RateLimitException, ValidationException

__all__ = [
    "AuthException",
    "InvalidCredentialsException",
    "UserExistsException",
    "APIException",
    "RateLimitException",
    "ValidationException"
] 