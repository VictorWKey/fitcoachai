"""
Exceptions related to API and data validation.
"""

from fastapi import HTTPException, status

class APIException(HTTPException):
    """Base exception for API errors."""
    def __init__(self, detail: str = "API Error", status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class RateLimitException(APIException):
    """Exception for rate limit exceeded."""
    def __init__(self, detail: str = "Too many requests", retry_after: int = 60):
        super().__init__(
            detail=detail, 
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
        self.headers = {"Retry-After": str(retry_after)}

class ValidationException(APIException):
    """Exception for data validation errors."""
    def __init__(self, detail: str = "Data validation error"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class NotFoundException(APIException):
    """Exception for resource not found."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class DatabaseException(APIException):
    """Exception for database errors."""
    def __init__(self, detail: str = "Database error"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ExternalServiceException(APIException):
    """Exception for errors in external services."""
    def __init__(self, detail: str = "External service error"):
        super().__init__(detail=detail, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
