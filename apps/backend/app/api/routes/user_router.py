"""
Routes for user profile management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Annotated, Dict
from db.schemas.user import User
from db.models.workout import TrainingDiscipline
from api.services import get_current_verified_user
from db.session import get_db
from db.crud.user import update_user_discipline, get_user_training_discipline
from agent.tool_factory import get_available_disciplines

user_router = APIRouter(prefix="/user", tags=["user"])

class DisciplineUpdate(BaseModel):
    """Model for updating user's preferred discipline."""
    preferred_discipline: TrainingDiscipline

class DisciplineResponse(BaseModel):
    """Response model for discipline operations."""
    message: str
    current_discipline: TrainingDiscipline

@user_router.put("/discipline")
async def update_user_preferred_discipline(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    discipline_update: DisciplineUpdate
):
    """
    Updates the user's preferred training discipline.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        discipline_update: New discipline preference
        
    Returns:
        DisciplineResponse: Confirmation message and current discipline
    """
    try:
        updated_user = await update_user_discipline(
            db, 
            current_user.id, 
            discipline_update.preferred_discipline
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )
        
        return DisciplineResponse(
            message="Disciplina actualizada correctamente",
            current_discipline=updated_user.preferred_discipline
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar disciplina: {str(e)}"
        )

@user_router.get("/discipline")
async def get_user_preferred_discipline(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Gets the user's current preferred training discipline.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Dict: Current discipline information
    """
    try:
        discipline = await get_user_training_discipline(db, current_user.id)
        
        if not discipline:
            discipline = TrainingDiscipline.HYPERTROPHY  # Default
        
        return {
            "current_discipline": discipline,
            "available_disciplines": get_available_disciplines()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener disciplina: {str(e)}"
        )

@user_router.get("/profile")
async def get_user_profile(
    current_user: Annotated[User, Depends(get_current_verified_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Gets the user's complete profile information.
    
    Args:
        current_user: Authenticated and verified user
        db: Database session
        
    Returns:
        Dict: User profile information including discipline
    """
    try:
        discipline = await get_user_training_discipline(db, current_user.id)
        
        if not discipline:
            discipline = TrainingDiscipline.HYPERTROPHY
        
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "preferred_discipline": discipline,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener perfil: {str(e)}"
        ) 