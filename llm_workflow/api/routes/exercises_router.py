from fastapi import APIRouter

exercises_router = APIRouter(prefix="/ui", tags=["ui"])

@exercises_router.get("/")
async def get_ui():
    return {"message": "Hello, World!"}