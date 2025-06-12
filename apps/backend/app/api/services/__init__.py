"""
API layer-specific services.

These services adapt core services for use in API routes.
"""

from .auth_service import (
    oauth2_scheme,
    authenticate_user,
    get_current_user,
    get_current_verified_user,
    check_user_exists,
)

from .chat_service import process_agent

__all__ = [
    "oauth2_scheme",
    "authenticate_user",
    "get_current_user",
    "get_current_verified_user",
    "check_user_exists",
    "process_agent"
]
