"""
Authentication and authorization routes for FitCoach AI.

This module provides all authentication-related endpoints including:
- User registration with email verification
- User login and logout
- Token refresh and revocation
- Email verification and resend
- Password reset functionality

The module follows the layered architecture pattern:
- Routes handle HTTP requests and responses
- Services contain business logic
- CRUD operations interact with the database

Security features:
- JWT-based authentication with access and refresh tokens
- Email verification for new accounts
- Password reset with secure tokens
- Token blacklisting for logout
- Rate limiting and account lockout protection
- CSRF protection middleware

Dependencies:
- FastAPI for HTTP handling
- SQLAlchemy for database operations
- JWT for token management
- Email service for notifications
- Background tasks for async email sending
"""

# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, Optional, cast
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from jose import JWTError
import logging

from db.crud.user import get_password_hash
from db import schemas, crud
from api.services import auth
from core.services import CoreAuthService, CoreUserService
from db.session import get_db
from db.models.user import User
from utils.email_service import send_verification_email, send_password_reset_email


auth_router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger(__name__)

@auth_router.post("/register", response_model=schemas.user.User)
async def register(
    background_tasks: BackgroundTasks,
    user: schemas.user.UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new user, generates a verification token, and sends a verification email.
    
    This endpoint handles several scenarios:
    1. New user registration
    2. Resending verification to unverified email
    3. Reusing usernames from unverified accounts

    Args:
        background_tasks: Allows sending the email asynchronously.
        user: The user data for registration.
        db: Database session.

    Returns:
        The created or updated user object.
        
    Raises:
        HTTPException: If there's an error during registration.
    """
    try:
        # Check if user exists and get additional info
        check_result = await auth.check_user_exists(db, user.email, user.username)
        
        # Generate new verification token and expiration
        verification_token = CoreAuthService.generate_verification_token()
        verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Handle existing unverified user with the same email
        if check_result.get('email_exists') and not check_result.get('is_verified'):
            existing_user = check_result['user']
            
            # If the username is different, check if we need to delete an unverified user with the new username
            if existing_user.username != user.username:
                # Check if the new username is already taken by another unverified user
                if check_result.get('username_exists') and not check_result.get('is_username_verified'):
                    # Delete the unverified user with the same username
                    await db.delete(check_result['username_user'])
                    await db.commit()
                    logger.info(f"Deleted unverified user with username: {user.username}")
            
            # Update existing user with new data and token
            existing_user.username = user.username  # Update username if changed
            existing_user.hashed_password = get_password_hash(user.password)  # Update password
            existing_user.verification_token = verification_token
            existing_user.verification_token_expires = verification_expires
            existing_user.updated_at = datetime.now(timezone.utc)
            
            await db.commit()
            await db.refresh(existing_user)
            db_user = existing_user
        else:
            # No existing unverified user with this email, but check username
            if check_result.get('username_exists') and not check_result.get('is_username_verified'):
                # Delete the unverified user with the same username
                await db.delete(check_result['username_user'])
                await db.commit()
                logger.info(f"Deleted unverified user with username: {user.username}")
            
            # Create new user
            db_user = await CoreUserService.create_user(
                db, 
                user, 
                verification_token=verification_token,
                verification_token_expires=verification_expires
            )
        
        # Send verification email
        background_tasks.add_task(send_verification_email, user.email, verification_token)
        logger.info(f"Verification email sent to: {user.email}")
        
        return db_user
        
    except HTTPException as e:
        # Re-raise HTTP exceptions (e.g., for duplicate verified username/email)
        logger.warning(f"Registration failed: {str(e.detail)}")
        raise e
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration. Please try again."
        )

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
    user, is_valid = await auth.authenticate_user(db, form_data.username, form_data.password)
    if not user or not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Nombre de usuario o contraseña incorrectos"
        )
    
    access_token = CoreAuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = CoreAuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@auth_router.post("/refresh", response_model=schemas.token.Token)
async def refresh_token(
    response: Response,
    token: schemas.token.RefreshRequest, 
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
        payload = CoreAuthService.decode_token(token.refresh_token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
        
        # Verificar que el refresh token no esté en la blacklist
        jti = payload.get("jti")
        
        if jti is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
        await CoreAuthService.verify_token_not_blacklisted(db, jti)
        
        user = await crud.user.get_user(db, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found"
            )
            
        await CoreAuthService.revoke_token(db, token.refresh_token)
        
        access_token = CoreAuthService.create_access_token(data={"sub": user_id})
        refresh_token = CoreAuthService.create_refresh_token(data={"sub": user_id})
        
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid refresh token"
        )

@auth_router.post("/logout")
async def logout(
    logout_payload: schemas.token.LogoutRequest,
    token: str = Depends(auth.oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """
    Logs the user out by revoking the current access **and refresh** tokens.
    
    Args:
        logout_payload: Body containing refresh_token.
        token: The access token (via Bearer header).
        db: Database session.

    Returns:
        A message confirming successful logout.
    """
    # Revocar access token
    await CoreAuthService.revoke_token(db, token)
    # Revocar refresh token si se proporciona
    if logout_payload.refresh_token:
        await CoreAuthService.revoke_token(db, logout_payload.refresh_token)
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
    user: Optional[User] = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de verificación inválido"
        )
    
    if cast(datetime, user.verification_token_expires) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificación expirado"
        )
        
    setattr(user, 'is_verified', True)
    setattr(user, 'verification_token', None)
    setattr(user, 'verification_token_expires', None)
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
    
    This endpoint can be used in two scenarios:
    1. When a user tries to register with an email that already exists but is not verified.
    2. When a user requests to resend the verification email.

    Args:
        background_tasks: Allows sending the email asynchronously.
        email: User's email.
        db: Database session.

    Returns:
        A message indicating the result of the operation.
        
    Raises:
        HTTPException: If there's an error processing the request.
    """
    try:
        user: Optional[User] = await crud.user.get_user_by_email(db, email)
        if not user:
            # For security reasons, we don't reveal if the email exists or not
            logger.info(f"Resend verification requested for non-existent email: {email}")
            return {"message": "Si tu cuenta existe, recibirás un email de verificación"}
            
        if cast(bool, user.is_verified):
            logger.info(f"Resend verification requested for already verified email: {email}")
            return {
                "message": "Esta cuenta ya está verificada. Puedes iniciar sesión con tus credenciales."
            }
        
        # Generate new verification token and expiration
        verification_token = CoreAuthService.generate_verification_token()
        verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
        
        # Update user with new token
        setattr(user, 'verification_token', verification_token)
        setattr(user, 'verification_token_expires', verification_expires)
        setattr(user, 'updated_at', datetime.now(timezone.utc))
        await db.commit()
        
        # Send verification email
        background_tasks.add_task(send_verification_email, email, verification_token)
        logger.info(f"Verification email resent to: {email}")
        
        return {"message": "Se ha enviado un nuevo correo de verificación. Por favor revisa tu bandeja de entrada."}
        
    except Exception as e:
        logger.error(f"Error resending verification email to {email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al procesar tu solicitud. Por favor, inténtalo de nuevo más tarde."
        )

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
    
    reset_token = CoreAuthService.generate_verification_token()
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)  # Expira en 1 hora
    
    setattr(user, 'reset_password_token', reset_token)
    setattr(user, 'reset_password_expires', reset_expires)
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
    
    if cast(datetime, user.reset_password_expires) < datetime.now(timezone.utc):
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
    
    if cast(datetime, user.reset_password_expires) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de restablecimiento expirado"
        )
    
    hashed_password = crud.user.get_password_hash(reset_data.new_password)
    setattr(user, 'hashed_password', hashed_password)
    setattr(user, 'reset_password_token', None)
    setattr(user, 'reset_password_expires', None)
    
    await CoreAuthService.revoke_all_user_tokens(db, cast(int, user.id))
    
    await db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}


@auth_router.post("/verify-user-direct")
async def verify_user_direct(
    verification_data: schemas.user.DirectVerification,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica directamente un usuario por email sin necesidad de token SMTP.
    Este endpoint es para desarrollo/testing cuando no hay servicio SMTP disponible.

    Args:
        verification_data: Datos de verificación que incluyen el email.
        db: Database session.

    Returns:
        Mensaje indicando el resultado de la verificación.
    """
    try:
        # Buscar usuario por email
        user = await crud.user.get_user_by_email(db, verification_data.email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        if getattr(user, 'is_verified'):
            return {"message": f"El usuario {verification_data.email} ya está verificado"}
        
        # Verificar directamente
        setattr(user, 'is_verified', True)
        setattr(user, 'verification_token', None)
        setattr(user, 'verification_token_expires', None)
        setattr(user, 'updated_at', datetime.now(timezone.utc))
        
        await db.commit()
        
        logger.info(f"Usuario verificado directamente: {verification_data.email}")
        
        return {"message": f"Usuario {verification_data.email} verificado exitosamente"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error verificando usuario {verification_data.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@auth_router.get("/unverified-users", response_model=schemas.user.UnverifiedUsersListResponse)
async def list_unverified_users(
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos los usuarios no verificados.
    Este endpoint es útil para desarrollo/testing.

    Args:
        db: Database session.

    Returns:
        Lista de usuarios no verificados con su información básica.
    """
    try:
        stmt = select(User).where(User.is_verified == False)
        result = await db.execute(stmt)
        unverified_users = result.scalars().all()
        
        users_data = []
        for user in unverified_users:
            users_data.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at,
                "verification_token_expires": user.verification_token_expires
            })
        
        return {
            "count": len(users_data),
            "users": users_data
        }
        
    except Exception as e:
        logger.error(f"Error listando usuarios no verificados: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )
