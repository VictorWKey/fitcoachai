"""
Módulo API para la interfaz REST de la aplicación.
"""

from .routes import api_router
from .services import (
    oauth2_scheme,
    get_current_user,
    get_current_verified_user
)

__all__ = [
    "api_router",
    "oauth2_scheme",
    "get_current_user",
    "get_current_verified_user"
] 