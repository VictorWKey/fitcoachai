"""
Core services for the FitCoach AI application.

This package contains business logic services that implement the core
functionality of the application, separated from API and database concerns.
"""

from .auth import CoreAuthService
from .exercise_analysis import infer_series_type
from .user import CoreUserService

__all__ = [
    "CoreAuthService",
    "infer_series_type",
    "CoreUserService"
]
