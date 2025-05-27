"""
CSRF protection configuration and middleware.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from config.security_settings import security_settings

def setup_csrf_protection(app: FastAPI):
    """
    Sets up CSRF protection for the application.
    
    Args:
        app: The FastAPI instance
    """
    
    @CsrfProtect.load_config
    def get_csrf_config():
        """Loads the CSRF configuration from security settings."""
        return security_settings.CSRF_SETTINGS
    
    @app.exception_handler(CsrfProtectError)
    async def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
        """
        Exception handler for CSRF errors.
        
        Args:
            request: The HTTP request
            exc: The CSRF exception
            
        Returns:
            A JSON response with the error message
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message}
        )
