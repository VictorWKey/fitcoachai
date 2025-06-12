"""
Middleware to add security headers to responses.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all HTTP responses.
    These headers help protect against various common web attacks.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Adds security headers to the response.
        
        Args:
            request: The incoming HTTP request
            call_next: The next function in the middleware pipeline
            
        Returns:
            The HTTP response with the security headers added
        """
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
