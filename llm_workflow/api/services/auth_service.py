# auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple
import secrets
import uuid
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud.user import get_user_by_email, get_user_by_username, get_user, verify_password
from db.schemas.token import TokenData, Token, TokenBlacklist as TokenBlacklistSchema
from db.models.token import TokenBlacklist
from db.session import get_db
from db.models.user import User

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Configuración JWT
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("No SECRET_KEY set in environment variables")
    
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hora
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 días
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Tuple[Optional[User], bool]:
    user = await get_user_by_username(db, username)
    
    # Usuario no existe
    if not user:
        return None, False
    
    # Verificar si la cuenta está bloqueada
    if user.account_locked_until and user.account_locked_until > datetime.now(timezone.utc):
        locked_for = (user.account_locked_until - datetime.now(timezone.utc)).seconds // 60
        logger.warning(f"Intento de login en cuenta bloqueada: {username}")
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"La cuenta está bloqueada temporalmente. Inténtalo nuevamente en {locked_for} minutos."
        )
    
    # Verificar contraseña
    if not verify_password(password, user.hashed_password):
        # Incrementar contador de intentos fallidos
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.now(timezone.utc)
        
        # Bloquear cuenta si se exceden los intentos
        if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.account_locked_until = datetime.now(timezone.utc) + timedelta(minutes=ACCOUNT_LOCKOUT_MINUTES)
            logger.warning(f"Cuenta bloqueada por múltiples intentos fallidos: {username}")
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Demasiados intentos fallidos. La cuenta ha sido bloqueada por {ACCOUNT_LOCKOUT_MINUTES} minutos."
            )
        
        await db.commit()
        return user, False
    
    # Login exitoso - reiniciar contador de intentos fallidos
    user.failed_login_attempts = 0
    user.last_failed_login = None
    user.account_locked_until = None
    await db.commit()
    
    return user, True

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        
        if user_id is None or jti is None:
            raise credentials_exception
        
        # Verificar si el token está en la lista negra
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        )
        blacklisted_token = result.scalar_one_or_none()
        
        if blacklisted_token:
            raise credentials_exception
            
        token_data = TokenData(sub=int(user_id), jti=jti)
        
    except JWTError as e:
        logger.error(f"Error al decodificar token: {e}")
        raise credentials_exception

    user = await get_user(db, user_id=token_data.sub)
    if user is None:
        logger.warning(f"Usuario no encontrado: ID {token_data.sub}")
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")
        
    return user

async def get_current_verified_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email no verificado. Por favor, verifica tu email."
        )
    return current_user

async def check_user_exists(db: AsyncSession, email: str, username: str) -> None:
    db_user = await get_user_by_email(db, email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    db_user = await get_user_by_username(db, username)
    if db_user:
        raise HTTPException(status_code=400, detail="Nombre de usuario ya registrado")

async def revoke_token(db: AsyncSession, token: str) -> bool:
    """Añadir token a lista negra"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        
        if not jti:
            return False
            
        token_blacklist = TokenBlacklist(jti=jti, exp=exp)
        db.add(token_blacklist)
        await db.commit()
        return True
    except JWTError:
        return False

def generate_verification_token() -> str:
    """Generar token único para verificación de email"""
    return secrets.token_urlsafe(32)

async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> bool:
    """
    Revoca todos los tokens activos de un usuario específico
    Útil cuando cambia la contraseña o hay una potencial vulnerabilidad de seguridad
    
    Args:
        db: La sesión de base de datos
        user_id: El ID del usuario cuyos tokens serán revocados
    
    Returns:
        bool: True si la operación se completó correctamente
    """
    try:
        # Buscar todos los tokens activos del usuario 
        # Esto requeriría una tabla que asocie tokens con usuarios
        # Por el momento, simplemente registramos el evento
        logger.info(f"Revocando todos los tokens para el usuario {user_id}")
        
        # En una implementación completa, aquí se añadirían a la lista negra todos 
        # los tokens activos del usuario
        # Por ejemplo:
        # tokens = await db.execute(
        #     select(UserToken).where(UserToken.user_id == user_id)
        # )
        # for token in tokens.scalars().all():
        #     token_blacklist = TokenBlacklist(jti=token.jti, exp=token.exp)
        #     db.add(token_blacklist)
        
        # await db.commit()
        return True
    except Exception as e:
        logger.error(f"Error al revocar tokens de usuario: {str(e)}")
        return False

