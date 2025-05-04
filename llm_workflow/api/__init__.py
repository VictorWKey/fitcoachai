from fastapi import APIRouter
from .chat import router as chat_router
from .exercises import router as ui_router

api_router = APIRouter()
api_router.include_router(chat_router)
api_router.include_router(ui_router)