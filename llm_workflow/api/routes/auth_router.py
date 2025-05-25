# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
import time
from typing import Dict, Any
from pydantic import EmailStr
from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from db import schemas, crud
from api.services import auth_service
from db.session import get_db
from db.models.user import User
from utils.email_service import send_verification_email, send_password_reset_email

# Limita las solicitudes por IP
request_counts: Dict[str, Dict[str, Any]] = {}

auth_router = APIRouter(prefix="/auth", tags=["auth"])

# Middleware para rate limiting
async def check_rate_limit(client_ip: str, limit: int = 5, window: int = 60) -> bool:
    """
    Verifica si una IP ha excedido el límite de solicitudes
    limit: número máximo de solicitudes
    window: periodo de tiempo en segundos
    """
    now = time.time()
    
    # Inicializar contador para esta IP si no existe
    if client_ip not in request_counts:
        request_counts[client_ip] = {"count": 0, "reset_at": now + window}
        
    # Si ya se pasó el tiempo de ventana, reiniciar contador
    if now > request_counts[client_ip]["reset_at"]:
        request_counts[client_ip] = {"count": 0, "reset_at": now + window}
        
    # Incrementar contador
    request_counts[client_ip]["count"] += 1
    
    # Verificar límite
    if request_counts[client_ip]["count"] > limit:
        return False
        
    return True

@auth_router.post("/register", response_model=schemas.user.User)
async def register(
    background_tasks: BackgroundTasks,
    user: schemas.user.UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    await auth_service.check_user_exists(db, user.email, user.username)
    
    # Generar token de verificación
    verification_token = auth_service.generate_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    # Crear usuario con token de verificación
    db_user = await crud.user.create_user(
        db, 
        user, 
        verification_token=verification_token,
        verification_token_expires=verification_expires
    )
    
    # Enviar email de verificación en segundo plano
    background_tasks.add_task(send_verification_email, user.email, verification_token)
    
    return db_user

@auth_router.post("/login", response_model=schemas.token.Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db),
    client_ip: str = "127.0.0.1"  # En producción obtener la IP real del request
):
    # Verificar rate limit
    if not await check_rate_limit(client_ip, limit=5, window=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiadas solicitudes. Inténtalo más tarde."
        )
    
    # Autenticar usuario
    user, is_valid = await auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user or not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Nombre de usuario o contraseña incorrectos"
        )
    
    # Crear tokens
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    refresh_token = auth_service.create_refresh_token(data={"sub": str(user.id)})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@auth_router.post("/refresh", response_model=schemas.token.Token)
async def refresh_token(
    response: Response,
    token: schemas.token.Token, 
    db: AsyncSession = Depends(get_db)
):
    try:
        # Decodificar refresh token
        payload = auth_service.jwt.decode(token.refresh_token, auth_service.SECRET_KEY, algorithms=[auth_service.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid refresh token"
            )
        
        # Verificar si el usuario existe
        user = await crud.user.get_user(db, int(user_id))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User not found"
            )
            
        # Revocar token anterior
        await auth_service.revoke_token(db, token.access_token)
        
        # Generar nuevos tokens
        access_token = auth_service.create_access_token(data={"sub": user_id})
        refresh_token = auth_service.create_refresh_token(data={"sub": user_id})
        
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
        
    except auth_service.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid refresh token"
        )

@auth_router.post("/logout")
async def logout(
    token: str = Depends(auth_service.oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    await auth_service.revoke_token(db, token)
    return {"message": "Logout successful"}

@auth_router.post("/verify-email")
@auth_router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    # Buscar usuario con ese token
    stmt = select(User).where(User.verification_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de verificación inválido"
        )
    
    # Verificar si el token expiró
    if user.verification_token_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificación expirado"
        )
        
    # Actualizar estado de verificación
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
    # Buscar usuario
    user = await crud.user.get_user_by_email(db, email)
    if not user:
        # No revelar si el email existe o no
        return {"message": "Si tu cuenta existe, recibirás un email de verificación"}
        
    # Si ya está verificado
    if user.is_verified:
        return {"message": "Esta cuenta ya está verificada"}
    
    # Generar nuevo token
    verification_token = auth_service.generate_verification_token()
    verification_expires = datetime.now(timezone.utc) + timedelta(hours=24)
    
    # Actualizar token
    user.verification_token = verification_token
    user.verification_token_expires = verification_expires
    await db.commit()
    
    # Enviar email en segundo plano
    background_tasks.add_task(send_verification_email, email, verification_token)
    
    return {"message": "Si tu cuenta existe, recibirás un email de verificación"}

@auth_router.post("/forgot-password")
async def forgot_password(
    background_tasks: BackgroundTasks,
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    # Buscar usuario
    user = await crud.user.get_user_by_email(db, email)
    if not user:
        # No revelar si el email existe o no por seguridad
        return {"message": "Si tu cuenta existe, recibirás un email con instrucciones para restablecer tu contraseña"}
    
    # Generar token de restablecimiento
    reset_token = auth_service.generate_verification_token()
    reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)  # Expira en 1 hora
    
    # Guardar token en usuario
    user.reset_password_token = reset_token
    user.reset_password_expires = reset_expires
    await db.commit()
    
    # Enviar email
    background_tasks.add_task(send_password_reset_email, email, reset_token)
    
    return {"message": "Si tu cuenta existe, recibirás un email con instrucciones para restablecer tu contraseña"}

@auth_router.get("/reset-password/verify")
async def verify_reset_token(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Verifica que el token de restablecimiento sea válido antes de mostrar el formulario
    """
    # Buscar usuario con ese token
    stmt = select(User).where(User.reset_password_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de restablecimiento inválido"
        )
    
    # Verificar si el token expiró
    if user.reset_password_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de restablecimiento expirado"
        )
    
    # Devolver información mínima del usuario (solo correo parcialmente oculto para verificación)
    email_parts = user.email.split('@')
    masked_email = f"{email_parts[0][0:3]}{'*' * (len(email_parts[0])-3)}@{email_parts[1]}"
    
    return {"valid": True, "user_email": masked_email}

@auth_router.post("/reset-password")
async def reset_password(
    reset_data: schemas.user.PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    """
    Restablece la contraseña usando el token de restablecimiento
    """
    # Validar complejidad de contraseña
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
    
    # Buscar usuario con ese token
    stmt = select(User).where(User.reset_password_token == reset_data.token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de restablecimiento inválido"
        )
    
    # Verificar si el token expiró
    if user.reset_password_expires < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de restablecimiento expirado"
        )
    
    # Actualizar contraseña
    hashed_password = crud.user.get_password_hash(reset_data.new_password)
    user.hashed_password = hashed_password
    user.reset_password_token = None
    user.reset_password_expires = None
    
    # Invalidar todas las sesiones existentes
    await auth_service.revoke_all_user_tokens(db, user.id)
    
    await db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}
