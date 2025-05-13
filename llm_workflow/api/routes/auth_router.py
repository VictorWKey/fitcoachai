# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from db import schemas, crud
from api.services import auth_service
from db.session import get_db

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=schemas.user.User)
async def register(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    await auth_service.check_user_exists(db, user.email, user.username)
    return await crud.user.create_user(db, user)

@auth_router.post("/login", response_model=schemas.token.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = auth_service.create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
