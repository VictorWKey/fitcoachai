"""
Tests unitarios para el cache LRU de agentes con métricas.
Verifica funcionalidad, rendimiento y correctitud del sistema de cache.
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
from agent.lru_cache import LRUAgentCache, create_tool_combination_key, CacheMetrics
from agent.agent_factory import get_agent_for_user, get_cache_metrics
from db.models.workout import TrainingDiscipline

class TestLRUAgentCache:
    """Tests para la clase LRUAgentCache"""
    
    @pytest.fixture
    def cache(self):
        """Fixture que crea un cache limpio para cada test"""
        return LRUAgentCache(max_size=3, ttl_seconds=2)  # Tamaños pequeños para testing
    
    @pytest.fixture
    def mock_agent(self):
        """Mock de un agente compilado"""
        agent = MagicMock()
        agent.name = "test_agent"
        return agent
    
    @pytest.mark.asyncio
    async def test_cache_basic_functionality(self, cache, mock_agent):
        """Test básico de get/set del cache"""
        
        # Función mock para crear agente
        async def create_agent():
            await asyncio.sleep(0.1)  # Simular compilación
            return mock_agent
        
        # Primera llamada - cache miss
        key = "test_key_1"
        agent1 = await cache.get_or_create_agent(key, create_agent)
        
        assert agent1 == mock_agent
        assert len(cache.cache) == 1
        
        # Segunda llamada - cache hit
        agent2 = await cache.get_or_create_agent(key, create_agent)
        
        assert agent2 == mock_agent
        assert agent1 is agent2  # Mismo objeto
        assert len(cache.cache) == 1
        
    @pytest.mark.asyncio
    async def test_cache_metrics(self, cache, mock_agent):
        """Test de métricas del cache"""
        
        async def create_agent():
            return mock_agent
        
        # Verificar métricas iniciales
        metrics = await cache.get_metrics()
        assert metrics.hits == 0
        assert metrics.misses == 0
        assert metrics.total_requests == 0
        assert metrics.hit_rate == 0.0
        
        # Primera llamada (miss)
        await cache.get_or_create_agent("key1", create_agent)
        metrics = await cache.get_metrics()
        assert metrics.hits == 0
        assert metrics.misses == 1
        assert metrics.total_requests == 1
        assert metrics.hit_rate == 0.0
        
        # Segunda llamada mismo key (hit)
        await cache.get_or_create_agent("key1", create_agent)
        metrics = await cache.get_metrics()
        assert metrics.hits == 1
        assert metrics.misses == 1
        assert metrics.total_requests == 2
        assert metrics.hit_rate == 0.5
        
    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache, mock_agent):
        """Test de eviction LRU cuando se supera max_size"""
        
        async def create_agent():
            return mock_agent
        
        # Llenar cache hasta el límite (max_size=3)
        await cache.get_or_create_agent("key1", create_agent)
        await cache.get_or_create_agent("key2", create_agent)
        await cache.get_or_create_agent("key3", create_agent)
        
        assert len(cache.cache) == 3
        assert "key1" in cache.cache
        
        # Agregar uno más - debería evict key1 (least recently used)
        await cache.get_or_create_agent("key4", create_agent)
        
        assert len(cache.cache) == 3
        assert "key1" not in cache.cache  # Evicted
        assert "key4" in cache.cache  # Nuevo
        
        # Verificar métricas de eviction
        metrics = await cache.get_metrics()
        assert metrics.evictions == 1
        
    @pytest.mark.asyncio
    async def test_ttl_expiration(self, cache, mock_agent):
        """Test de expiración por TTL"""
        
        async def create_agent():
            return mock_agent
        
        # Agregar entrada
        await cache.get_or_create_agent("key1", create_agent)
        assert "key1" in cache.cache
        
        # Esperar que expire (ttl_seconds=2)
        await asyncio.sleep(2.1)
        
        # Nueva llamada debería limpiar expired y crear nuevo
        await cache.get_or_create_agent("key2", create_agent)
        
        # key1 debería haber sido removido en cleanup
        assert "key1" not in cache.cache
        assert "key2" in cache.cache
        
    @pytest.mark.asyncio
    async def test_concurrent_access(self, cache, mock_agent):
        """Test de acceso concurrente al cache"""
        
        call_count = 0
        async def create_agent():
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simular compilación
            return mock_agent
        
        # Múltiples llamadas concurrentes con la misma clave
        tasks = [
            cache.get_or_create_agent("same_key", create_agent)
            for _ in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Solo debería haber compilado una vez
        assert call_count == 1
        
        # Todos deberían haber obtenido el mismo agente
        assert all(agent is mock_agent for agent in results)
        
        # Solo una entrada en cache
        assert len(cache.cache) == 1

class TestToolCombinationKey:
    """Tests para la generación de claves de combinación de herramientas"""
    
    def test_key_generation_consistency(self):
        """Test que las claves se generen de forma consistente"""
        tools1 = ["tool_a", "tool_b", "tool_c"]
        tools2 = ["tool_c", "tool_a", "tool_b"]  # Orden diferente
        
        key1 = create_tool_combination_key(tools1)
        key2 = create_tool_combination_key(tools2)
        
        # Deberían ser iguales independientemente del orden
        assert key1 == key2
        
    def test_key_generation_with_preferences(self):
        """Test de generación de claves con preferencias"""
        tools = ["tool_a", "tool_b"]
        prefs1 = {"param1": "value1", "param2": "value2"}
        prefs2 = {"param2": "value2", "param1": "value1"}  # Orden diferente
        
        key1 = create_tool_combination_key(tools, prefs1)
        key2 = create_tool_combination_key(tools, prefs2)
        
        # Deberían ser iguales
        assert key1 == key2
        
    def test_key_uniqueness(self):
        """Test que combinaciones diferentes generen claves diferentes"""
        key1 = create_tool_combination_key(["tool_a", "tool_b"])
        key2 = create_tool_combination_key(["tool_a", "tool_c"])
        key3 = create_tool_combination_key(["tool_a", "tool_b"], {"param": "value"})
        
        # Todas deberían ser diferentes
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3

class TestAgentFactoryIntegration:
    """Tests de integración para el agent factory con cache LRU"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock de sesión de base de datos"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_llm(self):
        """Mock del LLM"""
        llm = MagicMock()
        llm.bind_tools = MagicMock(return_value=llm)
        return llm
    
    @pytest.fixture
    def mock_checkpointer(self):
        """Mock del checkpointer"""
        return MagicMock()
    
    @pytest.mark.asyncio
    async def test_cache_integration_same_discipline(self, mock_llm, mock_checkpointer, monkeypatch):
        """Test que usuarios con la misma disciplina compartan agente cacheado"""
        
        # Mock de get_user_training_discipline
        async def mock_get_discipline(db, user_id):
            return TrainingDiscipline.HYPERTROPHY
        
        # Mock de get_tools_for_discipline
        def mock_get_tools(discipline):
            return [MagicMock()]
        
        # Mock de get_agent
        def mock_get_agent(llm, checkpointer, tools):
            agent = MagicMock()
            agent.discipline = llm.discipline if hasattr(llm, 'discipline') else 'test'
            return agent
        
        # Aplicar mocks
        monkeypatch.setattr("agent.agent_factory.get_user_training_discipline", mock_get_discipline)
        monkeypatch.setattr("agent.agent_factory.get_tools_for_discipline", mock_get_tools)
        monkeypatch.setattr("agent.agent_factory.get_agent", mock_get_agent)
        
        # Limpiar cache antes del test
        from agent.lru_cache import global_agent_cache
        await global_agent_cache.clear_cache()
        
        # Obtener agentes para dos usuarios diferentes con misma disciplina
        agent1 = await get_agent_for_user(1, mock_llm, mock_checkpointer)
        agent2 = await get_agent_for_user(2, mock_llm, mock_checkpointer)
        
        # Deberían ser el mismo objeto (cacheado)
        assert agent1 is agent2
        
        # Verificar métricas
        metrics = await get_cache_metrics()
        assert metrics.hits >= 1  # Al menos un hit
        assert metrics.compilations >= 1  # Al menos una compilación

# Tests de rendimiento
class TestCachePerformance:
    """Tests de rendimiento del cache"""
    
    @pytest.mark.asyncio
    async def test_cache_performance_vs_no_cache(self):
        """Test que demuestra la mejora de rendimiento del cache"""
        
        compilation_time = 0.1  # 100ms simulado de compilación
        
        async def slow_create_agent():
            await asyncio.sleep(compilation_time)
            return MagicMock()
        
        cache = LRUAgentCache(max_size=10)
        
        # Tiempo sin cache (múltiples compilaciones)
        start_time = time.time()
        for i in range(5):
            await slow_create_agent()
        no_cache_time = time.time() - start_time
        
        # Tiempo con cache (una compilación + hits)
        start_time = time.time()
        for i in range(5):
            await cache.get_or_create_agent("same_key", slow_create_agent)
        cache_time = time.time() - start_time
        
        # Cache debería ser significativamente más rápido
        assert cache_time < no_cache_time * 0.5  # Al menos 50% más rápido
        
        # Verificar métricas
        metrics = await cache.get_metrics()
        assert metrics.hits == 4  # 4 hits después de la primera compilación
        assert metrics.misses == 1  # Solo una miss (primera vez)

if __name__ == "__main__":
    # Ejecutar tests básicos
    pytest.main([__file__, "-v"]) 