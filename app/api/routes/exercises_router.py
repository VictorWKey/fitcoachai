"""
Routes for exercise management.
"""

from fastapi import APIRouter

exercises_router = APIRouter(prefix="/ui", tags=["ui"])

@exercises_router.get("/")
async def get_ui():
    """
    Test endpoint for the user interface.

    Returns:
        dict: Test message
    """
    return {"message": "Hello, World!"}
