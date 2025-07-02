"""
Router para endpoints administrativos y monitoreo.
Incluye métricas del cache de agentes y estadísticas del sistema.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any
from db.schemas.user import User
from api.services import get_current_verified_user
from agent.agent_factory import (
    get_cache_metrics, 
    get_cache_detailed_stats, 
    clear_agent_cache,
    cleanup_expired_agents,
    get_cached_agent_count,
    precompile_popular_agents
)
from agent.lru_cache import global_agent_cache
from db.session import get_db
import logging

logger = logging.getLogger(__name__)

admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/cache/metrics")
async def get_agent_cache_metrics(
    current_user: User = Depends(get_current_verified_user)
):
    """
    Obtiene métricas básicas del cache de agentes.
    
    Returns:
        Dict: Métricas del cache incluyendo hit rate, tamaño, etc.
    """
    try:
        metrics = await get_cache_metrics()
        
        return {
            "status": "success",
            "cache_metrics": metrics.to_dict(),
            "summary": {
                "hit_rate_percentage": round(metrics.hit_rate * 100, 2),
                "miss_rate_percentage": round(metrics.miss_rate * 100, 2),
                "efficiency": "High" if metrics.hit_rate > 0.8 else "Medium" if metrics.hit_rate > 0.5 else "Low"
            }
        }
    except Exception as e:
        logger.error(f"Error obteniendo métricas del cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener métricas del cache"
        )

@admin_router.get("/cache/detailed-stats")
async def get_agent_cache_detailed_stats(
    current_user: User = Depends(get_current_verified_user)
):
    """
    Obtiene estadísticas detalladas del cache de agentes.
    Incluye información sobre cada entrada individual.
    
    Returns:
        Dict: Estadísticas detalladas del cache
    """
    try:
        stats = await get_cache_detailed_stats()
        
        # Agregar análisis adicional
        if stats["entries"]:
            # Encontrar entrada más y menos usada
            most_used = max(stats["entries"], key=lambda x: x["access_count"])
            least_used = min(stats["entries"], key=lambda x: x["access_count"])
            
            # Promedio de edad de entradas
            avg_age = sum(entry["age_seconds"] for entry in stats["entries"]) / len(stats["entries"])
            
            stats["analysis"] = {
                "most_used_agent": {
                    "combination": most_used["tool_combination"],
                    "access_count": most_used["access_count"]
                },
                "least_used_agent": {
                    "combination": least_used["tool_combination"], 
                    "access_count": least_used["access_count"]
                },
                "average_age_minutes": round(avg_age / 60, 2),
                "total_entries": len(stats["entries"])
            }
        
        return {
            "status": "success",
            "detailed_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas detalladas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estadísticas detalladas"
        )

@admin_router.post("/cache/clear")
async def clear_cache(
    current_user: User = Depends(get_current_verified_user)
):
    """
    Limpia completamente el cache de agentes.
    ⚠️ Operación que afectará el rendimiento hasta que se vuelvan a compilar los agentes.
    
    Returns:
        Dict: Confirmación de limpieza
    """
    try:
        # Obtener métricas antes de limpiar para reporte
        metrics_before = await get_cache_metrics()
        entries_before = len(global_agent_cache.cache)
        
        # Limpiar cache
        await clear_agent_cache()
        
        logger.warning(f"Cache de agentes limpiado por usuario {current_user.id} - {entries_before} entradas removidas")
        
        return {
            "status": "success",
            "message": "Cache de agentes limpiado completamente",
            "entries_removed": entries_before,
            "metrics_before_clear": metrics_before.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error limpiando cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al limpiar cache"
        )

@admin_router.post("/cache/cleanup-expired")
async def cleanup_expired(
    current_user: User = Depends(get_current_verified_user)
):
    """
    Limpia solo las entradas expiradas del cache.
    Operación segura que no afecta agentes activos.
    
    Returns:
        Dict: Número de entradas expiradas removidas
    """
    try:
        removed_count = await cleanup_expired_agents()
        
        logger.info(f"Limpieza de expirados ejecutada por usuario {current_user.id} - {removed_count} entradas removidas")
        
        return {
            "status": "success",
            "message": "Limpieza de entradas expiradas completada",
            "expired_entries_removed": removed_count,
            "current_cache_size": get_cached_agent_count()
        }
        
    except Exception as e:
        logger.error(f"Error en limpieza de expirados: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error en limpieza de expirados"
        )

@admin_router.post("/cache/precompile")
async def precompile_agents(
    current_user: User = Depends(get_current_verified_user)
):
    """
    Pre-compila agentes para disciplinas populares.
    Mejora la experiencia del usuario eliminando latencia de primera compilación.
    
    Returns:
        Dict: Resultado de la pre-compilación
    """
    try:
        # Esta operación requiere acceso a LLM y checkpointer del servidor
        # Por ahora retornamos un placeholder - se implementará cuando se integre con FastAPI app state
        
        return {
            "status": "pending",
            "message": "Pre-compilación solicitada - se ejecutará en background",
            "note": "Esta funcionalidad requiere integración con el estado de la aplicación"
        }
        
    except Exception as e:
        logger.error(f"Error en pre-compilación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al iniciar pre-compilación"
        )

@admin_router.get("/cache/status")
async def get_cache_status(
    current_user: User = Depends(get_current_verified_user)
):
    """
    Obtiene el estado actual del cache en formato resumido.
    Endpoint rápido para monitoreo básico.
    
    Returns:
        Dict: Estado resumido del cache
    """
    try:
        metrics = await get_cache_metrics()
        current_size = get_cached_agent_count()
        
        # Determinar estado de salud del cache
        health_status = "healthy"
        if metrics.hit_rate < 0.5:
            health_status = "poor"
        elif metrics.hit_rate < 0.8:
            health_status = "fair"
        
        return {
            "status": "success",
            "cache_status": {
                "health": health_status,
                "size": current_size,
                "max_size": global_agent_cache.max_size,
                "hit_rate": round(metrics.hit_rate * 100, 2),
                "total_requests": metrics.total_requests,
                "avg_compilation_time_seconds": round(metrics.avg_compilation_time, 3),
                "memory_usage_mb": metrics.memory_usage_mb
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estado del cache"
        )

@admin_router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(get_current_verified_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el estado general del sistema incluyendo cache y base de datos.
    
    Returns:
        Dict: Estado de salud del sistema completo
    """
    try:
        # Métricas del cache
        cache_metrics = await get_cache_metrics()
        
        # Test básico de conectividad a DB
        try:
            await db.execute(text("SELECT 1"))
            db_status = "healthy"
        except Exception:
            db_status = "unhealthy"
        
        # Estado general
        overall_health = "healthy"
        if db_status != "healthy" or cache_metrics.hit_rate < 0.3:
            overall_health = "unhealthy"
        elif cache_metrics.hit_rate < 0.7:
            overall_health = "degraded"
        
        return {
            "status": "success",
            "system_health": {
                "overall": overall_health,
                "components": {
                    "database": db_status,
                    "agent_cache": "healthy" if cache_metrics.hit_rate > 0.7 else "degraded",
                    "cache_hit_rate": round(cache_metrics.hit_rate * 100, 2),
                    "active_agents": get_cached_agent_count()
                },
                "timestamp": cache_metrics.total_requests  # Usar como proxy de timestamp
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del sistema: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener estado del sistema"
        ) 