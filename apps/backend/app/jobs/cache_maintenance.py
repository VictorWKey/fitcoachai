"""
Jobs de mantenimiento automático para el cache de agentes.
Incluye limpieza de entradas expiradas y métricas de monitoreo.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from agent.agent_factory import cleanup_expired_agents, get_cache_metrics
from agent.lru_cache import global_agent_cache

logger = logging.getLogger(__name__)

class CacheMaintenanceJob:
    """
    Job automático para mantener el cache de agentes en buen estado.
    
    Funcionalidades:
    - Limpieza automática de entradas expiradas
    - Logging de métricas de rendimiento
    - Alertas cuando el rendimiento es bajo
    """
    
    def __init__(self, cleanup_interval_seconds: int = 1800):  # 30 minutos por defecto
        self.cleanup_interval = cleanup_interval_seconds
        self.is_running = False
        self.task = None
        
    async def start(self):
        """Inicia el job de mantenimiento en background"""
        if self.is_running:
            logger.warning("Cache maintenance job ya está ejecutándose")
            return
            
        self.is_running = True
        self.task = asyncio.create_task(self._maintenance_loop())
        logger.info(f"Cache maintenance job iniciado (intervalo: {self.cleanup_interval}s)")
        
    async def stop(self):
        """Detiene el job de mantenimiento"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Cache maintenance job detenido")
        
    async def _maintenance_loop(self):
        """Loop principal de mantenimiento"""
        while self.is_running:
            try:
                await self._run_maintenance_cycle()
                await asyncio.sleep(self.cleanup_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en ciclo de mantenimiento: {e}")
                await asyncio.sleep(60)  # Esperar 1 minuto antes de reintentar
                
    async def _run_maintenance_cycle(self):
        """Ejecuta un ciclo completo de mantenimiento"""
        logger.debug("Iniciando ciclo de mantenimiento del cache")
        
        # 1. Obtener métricas antes de la limpieza
        metrics_before = await get_cache_metrics()
        
        # 2. Limpiar entradas expiradas
        removed_count = await cleanup_expired_agents()
        
        # 3. Obtener métricas después de la limpieza
        metrics_after = await get_cache_metrics()
        
        # 4. Log de estadísticas
        await self._log_maintenance_stats(metrics_before, metrics_after, removed_count)
        
        # 5. Verificar alertas de rendimiento
        await self._check_performance_alerts(metrics_after)
        
    async def _log_maintenance_stats(self, before: Any, after: Any, removed_count: int):
        """Registra estadísticas del mantenimiento"""
        if removed_count > 0:
            logger.info(f"Mantenimiento completado: {removed_count} entradas expiradas removidas")
        
        # Log métricas importantes
        logger.info(f"Cache stats - Size: {after.cache_size}, Hit rate: {after.hit_rate:.2%}, "
                   f"Total requests: {after.total_requests}")
        
        # Log cambios significativos
        if after.cache_size != before.cache_size:
            logger.info(f"Cache size cambió de {before.cache_size} a {after.cache_size}")
            
    async def _check_performance_alerts(self, metrics: Any):
        """Verifica y registra alertas de rendimiento"""
        # Alerta por baja tasa de aciertos
        if metrics.hit_rate < 0.5 and metrics.total_requests > 100:
            logger.warning(f"⚠️ Baja tasa de aciertos del cache: {metrics.hit_rate:.2%} "
                          f"({metrics.total_requests} requests totales)")
        
        # Alerta por tiempo de compilación alto
        if metrics.avg_compilation_time > 10.0:
            logger.warning(f"⚠️ Tiempo de compilación promedio alto: {metrics.avg_compilation_time:.2f}s")
        
        # Alerta por muchas evictions
        if metrics.evictions > metrics.compilations * 0.5:
            logger.warning(f"⚠️ Muchas evictions de cache: {metrics.evictions} vs {metrics.compilations} compilaciones")

# Instancia global del job de mantenimiento
cache_maintenance_job = CacheMaintenanceJob()

async def start_cache_maintenance():
    """Función helper para iniciar el mantenimiento del cache"""
    await cache_maintenance_job.start()

async def stop_cache_maintenance():
    """Función helper para detener el mantenimiento del cache"""
    await cache_maintenance_job.stop()

async def force_maintenance_cycle():
    """Ejecuta un ciclo de mantenimiento inmediato"""
    maintenance_job = CacheMaintenanceJob()
    await maintenance_job._run_maintenance_cycle()
    logger.info("Ciclo de mantenimiento forzado completado")

class CacheMetricsLogger:
    """
    Logger especializado para métricas del cache.
    Registra métricas detalladas en intervalos regulares.
    """
    
    def __init__(self, log_interval_seconds: int = 3600):  # 1 hora por defecto
        self.log_interval = log_interval_seconds
        self.is_running = False
        self.task = None
        
    async def start(self):
        """Inicia el logging de métricas"""
        if self.is_running:
            return
            
        self.is_running = True
        self.task = asyncio.create_task(self._metrics_loop())
        logger.info(f"Cache metrics logger iniciado (intervalo: {self.log_interval}s)")
        
    async def stop(self):
        """Detiene el logging de métricas"""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Cache metrics logger detenido")
        
    async def _metrics_loop(self):
        """Loop de logging de métricas"""
        while self.is_running:
            try:
                await self._log_detailed_metrics()
                await asyncio.sleep(self.log_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en logging de métricas: {e}")
                await asyncio.sleep(300)  # 5 minutos antes de reintentar
                
    async def _log_detailed_metrics(self):
        """Registra métricas detalladas del cache"""
        try:
            metrics = await get_cache_metrics()
            
            # Crear reporte detallado
            report = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cache_size": metrics.cache_size,
                "hit_rate": round(metrics.hit_rate * 100, 2),
                "miss_rate": round(metrics.miss_rate * 100, 2),
                "total_requests": metrics.total_requests,
                "cache_hits": metrics.hits,
                "cache_misses": metrics.misses,
                "compilations": metrics.compilations,
                "evictions": metrics.evictions,
                "avg_compilation_time": round(metrics.avg_compilation_time, 3),
                "memory_usage_mb": metrics.memory_usage_mb
            }
            
            logger.info(f"📊 Cache metrics report: {report}")
            
            # Métricas derivadas útiles
            if metrics.total_requests > 0:
                efficiency = metrics.hits / metrics.total_requests
                if efficiency > 0.9:
                    logger.info("🟢 Cache performance: EXCELLENT")
                elif efficiency > 0.7:
                    logger.info("🟡 Cache performance: GOOD")
                else:
                    logger.info("🔴 Cache performance: NEEDS ATTENTION")
                    
        except Exception as e:
            logger.error(f"Error generando reporte de métricas: {e}")

# Instancia global del logger de métricas
cache_metrics_logger = CacheMetricsLogger()

async def start_metrics_logging():
    """Inicia el logging automático de métricas"""
    await cache_metrics_logger.start()

async def stop_metrics_logging():
    """Detiene el logging automático de métricas"""
    await cache_metrics_logger.stop() 