from fastapi import APIRouter

router = APIRouter(prefix="/ui", tags=["ui"])

@router.get("/")
async def get_ui():
    return {"message": "Hello, World!"}