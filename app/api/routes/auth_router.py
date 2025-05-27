# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from jose import JWTError

from db import schemas, crud
from api.services import auth_service
from core.services import AuthService, UserService
from db.session import get_db
from db.models.user import User
from utils.email_service import send_verification_email, send_password_reset_email

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=schemas.user.User)
async def register(
    background_tasks: BackgroundTasks,
    user: schemas.user.UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user, generates a verification token, and sends a verification email.

    Args:
        background_tasks: Allows sending the email asynchronously.
        user: The user data for registration.
        db: Database session.

    Returns:
        The created user object.
    """
    await auth_service.check_user_exists(db, user.email, user.username)
    
    verification_token = auth_service.generate_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    db_user = await UserService.create_user(
        db, 
        user, 
        verification_token=verification_token,
        verification_token_expires=verification_expires
    )
    
    background_tasks.add_task(send_verification_email, user.email, verification_token)
    
    return db_user

@auth_router.post("/login", response_model=schemas.token.Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticates a user and returns access and refresh tokens.

    Args:
        response: FastAPI response object.
        form_data: Form data containing username and password.
        db: Database session.

    Returns:
        A dictionary with access token, refresh token, and token type.
    """
    user, is_valid = await auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user or not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Nombre de usuario o contraseña incorrectos"
        )
    
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@auth_router.post("/refresh", response_model=schemas.token.Token)
async def refresh_token(
    response: Response,
    token: schemas.token.Token, 
    db: AsyncSession = Depends(get_db)
):
    """
    Refreshes access and refresh tokens using a valid refresh token.

    Args:
        response: FastAPI response object.
        token: The current token object containing refresh_token.
        db: Database session.

    Returns:
        A new set of access and refresh tokens.
    """
    try:
        payload = AuthService.decode_token(token.refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
        
        user = await crud.user.get_user(db, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found"
            )
            
        await AuthService.revoke_token(db, token.access_token)
        
        access_token = AuthService.create_access_token(data={"sub": user_id})
        refresh_token = AuthService.create_refresh_token(data={"sub": user_id})
        
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid refresh token"
        )

@auth_router.post("/logout")
async def logout(
    token: str = Depends(auth_service.oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Logs the user out by revoking the current token.

    Args:
        token: The token to be revoked.
        db: Database session.

    Returns:
        A message confirming successful logout.
    """
    await AuthService.revoke_token(db, token)
    return {"message": "Logout successful"}

@auth_router.post("/verify-email")
@auth_router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):

    """
    Verifies a user's email using a verification token.

    Args:
        token: The verification token sent by email.
        db: Database session.

    Returns:
        A message indicating the result of the verification.
    """
    stmt = select(User).where(User.verification_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de verificación inválido"
        )
    
    if user.verification_token_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificación expirado"
        )
        
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    await db.commit()
    
    return {"message": "Email verificado correctamente"}

@auth_router.post("/resend-verification")
async def resend_verification(
    background_tasks: BackgroundTasks,
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    """
    Resends a new email verification link to the user.

    Args:
        background_tasks: Allows sending the email asynchronously.
        email: User's email.
        db: Database session.

    Returns:
        A message indicating whether the email was sent.
    """
    user = await crud.user.get_user_by_email(db, email)
    if not user:
        return {"message": "Si tu cuenta existe, recibirás un email de verificación"}
        
    if user.is_verified:
        return {"message": "Esta cuenta ya está verificada"}
    
    verification_token = AuthService.generate_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    user.verification_token = verification_token
    user.verification_token_expires = verification_expires
    await db.commit()
    
    background_tasks.add_task(send_verification_email, email, verification_token)
    
    return {"message": "Si tu cuenta existe, recibirás un email de verificación"}

@auth_router.post("/forgot-password")
async def forgot_password(
    background_tasks: BackgroundTasks,
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    """
    Sends a password reset email to the user.

    Args:
        background_tasks: Allows sending the email asynchronously.
        email: User's email address.
        db: Database session.

    Returns:
        A message indicating whether the email was sent.
    """
    user = await crud.user.get_user_by_email(db, email)
    if not user:
        return {"message": "Si tu cuenta existe, recibirás un email con instrucciones para restablecer tu contraseña"}
    
    reset_token = AuthService.generate_verification_token()
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)  # Expira en 1 hora
    
    user.reset_password_token = reset_token
    user.reset_password_expires = reset_expires
    await db.commit()
    
    background_tasks.add_task(send_password_reset_email, email, reset_token)
    
    return {"message": "Si tu cuenta existe, recibirás un email con instrucciones para restablecer tu contraseña"}

@auth_router.get("/reset-password/verify")
async def verify_reset_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifies that a password reset token is valid and not expired.

    Args:
        token: The reset token provided by the user.
        db: Database session.

    Returns:
        A boolean indicating validity and a masked version of the user's email.
    """
    stmt = select(User).where(User.reset_password_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de restablecimiento inválido"
        )
    
    if user.reset_password_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de restablecimiento expirado"
        )
    
    email_parts = user.email.split('@')
    masked_email = f"{email_parts[0][0:3]}{'*' * (len(email_parts[0])-3)}@{email_parts[1]}"
    
    return {"valid": True, "user_email": masked_email}

@auth_router.post("/reset-password")
async def reset_password(
    reset_data: schemas.user.PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Resets the user's password using a valid reset token.

    Args:
        reset_data: New password and reset token.
        db: Database session.

    Returns:
        A message indicating the password has been updated.
    """
    try:
        schemas.user.UserCreate(
            username="temp",
            email="temp@example.com",
            password=reset_data.new_password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    stmt = select(User).where(User.reset_password_token == reset_data.token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de restablecimiento inválido"
        )
    
    if user.reset_password_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de restablecimiento expirado"
        )
    
    hashed_password = crud.user.get_password_hash(reset_data.new_password)
    user.hashed_password = hashed_password
    user.reset_password_token = None
    user.reset_password_expires = None
    
    await AuthService.revoke_all_user_tokens(db, user.id)
    
    await db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}
