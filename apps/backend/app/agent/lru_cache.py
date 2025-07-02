"""
LRU Cache avanzado para agentes con métricas de uso y TTL.
Optimizado para combinaciones personalizadas de herramientas.
"""

import asyncio
import hashlib
import json
import time
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class CacheMetrics:
    """Métricas detalladas del cache"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    compilations: int = 0
    total_requests: int = 0
    avg_compilation_time: float = 0.0
    cache_size: int = 0
    memory_usage_mb: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Tasa de aciertos del cache"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    @property
    def miss_rate(self) -> float:
        """Tasa de fallos del cache"""
        return 1.0 - self.hit_rate
    
    def to_dict(self) -> Dict:
        """Convierte métricas a diccionario para logging/API"""
        return asdict(self)

@dataclass
class CacheEntry:
    """Entrada del cache con metadatos"""
    agent: Any
    created_at: float
    last_accessed: float
    access_count: int
    tool_combination: str
    compilation_time: float

class LRUAgentCache:
    """
    Cache LRU avanzado para agentes con métricas, TTL y gestión inteligente.
    
    Características:
    - LRU (Least Recently Used) eviction
    - TTL (Time To Live) para expiración automática
    - Métricas detalladas de uso
    - Thread-safe con asyncio
    - Gestión de memoria inteligente
    """
    
    def __init__(self, max_size: int = 50, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = asyncio.Lock()
        self.metrics = CacheMetrics()
        self._compilation_times: List[float] = []
        
    async def get_or_create_agent(
        self, 
        tool_combination_key: str, 
        create_func: Callable[[], Any],
        tool_combination_data: Optional[Dict] = None
    ) -> Any:
        """
        Obtiene un agente del cache o lo crea si no existe.
        
        Args:
            tool_combination_key: Clave única para la combinación de tools
            create_func: Función async para crear el agente si no existe
            tool_combination_data: Datos adicionales sobre la combinación
            
        Returns:
            Agent: El agente solicitado
        """
        async with self.lock:
            self.metrics.total_requests += 1
            
            # Limpieza de entradas expiradas
            await self._cleanup_expired_entries()
            
            # Verificar si existe en cache
            if tool_combination_key in self.cache:
                # Cache HIT
                entry = self.cache[tool_combination_key]
                
                # Actualizar estadísticas de acceso
                entry.last_accessed = time.time()
                entry.access_count += 1
                
                # Mover al final (most recently used)
                self.cache.move_to_end(tool_combination_key)
                
                self.metrics.hits += 1
                self.metrics.cache_size = len(self.cache)
                
                logger.info(f"Cache HIT para {tool_combination_key[:8]}... (accesos: {entry.access_count})")
                return entry.agent
            
            # Cache MISS - necesitamos crear el agente
            self.metrics.misses += 1
            logger.info(f"Cache MISS para {tool_combination_key[:8]}... - compilando agente")
            
            # Verificar si necesitamos hacer espacio
            if len(self.cache) >= self.max_size:
                await self._evict_lru_entry()
            
            # Crear nuevo agente (operación costosa)
            start_time = time.time()
            agent = await create_func()
            compilation_time = time.time() - start_time
            
            # Actualizar métricas de compilación
            self.metrics.compilations += 1
            self._compilation_times.append(compilation_time)
            self.metrics.avg_compilation_time = sum(self._compilation_times) / len(self._compilation_times)
            
            # Crear entrada del cache
            entry = CacheEntry(
                agent=agent,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                tool_combination=tool_combination_data.get("description", "unknown") if tool_combination_data else "unknown",
                compilation_time=compilation_time
            )
            
            # Guardar en cache
            self.cache[tool_combination_key] = entry
            self.metrics.cache_size = len(self.cache)
            
            logger.info(f"Agente compilado y cacheado en {compilation_time:.2f}s para {tool_combination_key[:8]}...")
            return agent
    
    async def _cleanup_expired_entries(self):
        """Limpia entradas expiradas del cache"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry.created_at > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            logger.info(f"Entrada expirada removida: {key[:8]}...")
        
        if expired_keys:
            self.metrics.cache_size = len(self.cache)
    
    async def _evict_lru_entry(self):
        """Remueve la entrada menos recientemente usada"""
        if not self.cache:
            return
        
        # OrderedDict mantiene orden de inserción, el primero es el LRU
        lru_key, lru_entry = self.cache.popitem(last=False)
        self.metrics.evictions += 1
        
        logger.info(f"Entrada LRU evicted: {lru_key[:8]}... (accesos: {lru_entry.access_count}, "
                   f"edad: {time.time() - lru_entry.created_at:.0f}s)")
    
    async def get_metrics(self) -> CacheMetrics:
        """Obtiene métricas actuales del cache"""
        async with self.lock:
            self.metrics.cache_size = len(self.cache)
            # Estimar uso de memoria (aproximado)
            self.metrics.memory_usage_mb = len(self.cache) * 5.0  # ~5MB por agente
            return self.metrics
    
    async def get_cache_stats(self) -> Dict:
        """Obtiene estadísticas detalladas del cache"""
        async with self.lock:
            stats = {
                "metrics": self.metrics.to_dict(),
                "entries": []
            }
            
            current_time = time.time()
            for key, entry in self.cache.items():
                stats["entries"].append({
                    "key": key[:16] + "..." if len(key) > 16 else key,
                    "tool_combination": entry.tool_combination,
                    "access_count": entry.access_count,
                    "age_seconds": int(current_time - entry.created_at),
                    "last_accessed_seconds_ago": int(current_time - entry.last_accessed),
                    "compilation_time": entry.compilation_time
                })
            
            # Ordenar por acceso más reciente
            stats["entries"].sort(key=lambda x: x["last_accessed_seconds_ago"])
            
            return stats
    
    async def clear_cache(self):
        """Limpia completamente el cache"""
        async with self.lock:
            cleared_count = len(self.cache)
            self.cache.clear()
            self.metrics = CacheMetrics()
            self._compilation_times.clear()
            
            logger.info(f"Cache limpiado completamente ({cleared_count} entradas removidas)")
    
    async def remove_expired(self) -> int:
        """Remueve todas las entradas expiradas y retorna el número removido"""
        async with self.lock:
            initial_count = len(self.cache)
            await self._cleanup_expired_entries()
            removed_count = initial_count - len(self.cache)
            
            logger.info(f"Limpieza de expirados completada: {removed_count} entradas removidas")
            return removed_count

def create_tool_combination_key(tool_names: List[str], user_preferences: Optional[Dict] = None) -> str:
    """
    Crea una clave única para una combinación de herramientas.
    
    Args:
        tool_names: Lista de nombres de herramientas
        user_preferences: Preferencias adicionales del usuario
        
    Returns:
        str: Clave única para la combinación
    """
    # Normalizar y ordenar herramientas para consistencia
    normalized_tools = sorted([tool.lower().strip() for tool in tool_names])
    
    combination_data = {
        "tools": normalized_tools,
        "preferences": user_preferences or {}
    }
    
    # Crear hash determinístico
    combination_str = json.dumps(combination_data, sort_keys=True)
    return hashlib.sha256(combination_str.encode()).hexdigest()[:32]

# Instancia global del cache
global_agent_cache = LRUAgentCache(max_size=50, ttl_seconds=3600) 