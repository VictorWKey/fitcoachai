"""
Main entry point for the FitCoach AI application.
"""

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_openai import ChatOpenAI
from db import init_db
from api.routes import api_router
from middleware import RateLimitMiddleware, SecurityHeadersMiddleware, setup_csrf_protection
from config.app_settings import settings
from config.db_settings import db_settings
from utils.model_utils import wait_for_server_and_load_model
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from jobs.cache_maintenance import start_cache_maintenance, start_metrics_logging, stop_cache_maintenance, stop_metrics_logging
from agent.agent_factory import precompile_popular_agents
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan configuration.
    
    Args:
        app: The FastAPI instance
    """
    # Uncomment when using Ollama locally
    # await wait_for_server_and_load_model()
    
    await init_db()
    
    # Connection pool configuration
    async with AsyncConnectionPool(
        conninfo=db_settings.PSYCOPG_DATABASE_URL,
        min_size=db_settings.POOL_SIZE,
        max_size=db_settings.MAX_OVERFLOW,
        timeout=db_settings.POOL_TIMEOUT,
        max_lifetime=db_settings.POOL_RECYCLE,
        kwargs=db_settings.CONNECTION_KWARGS
    ) as pool:
        # Configure langgraph checkpointer
        async with AsyncPostgresSaver.from_conn_string(db_settings.PSYCOPG_DATABASE_URL) as checkpointer:
            await checkpointer.setup()

            # LLM base sin tools (se agregarán dinámicamente por usuario)
            llm_base = ChatOpenAI(
                model=settings.MODEL_NAME,
                temperature=0,
                max_completion_tokens=1000,
            )
            
            app.state.pool = pool
            app.state.llm_base = llm_base  # Cambiar nombre para claridad
            app.state.checkpointer = checkpointer
            # Remover: app.state.agent = agent (ya no hay agente global)

            # 🚀 INICIALIZAR CACHE LRU Y JOBS DE MANTENIMIENTO
            logger.info("🔧 Iniciando sistemas de cache y mantenimiento...")
            
            try:
                # 1. Iniciar jobs de mantenimiento automático
                await start_cache_maintenance()
                await start_metrics_logging()
                logger.info("✅ Jobs de mantenimiento iniciados")
                
                # 2. Pre-compilar agentes populares (opcional, mejora UX)
                logger.info("🔄 Pre-compilando agentes populares...")
                await precompile_popular_agents(llm_base, checkpointer)
                logger.info("✅ Pre-compilación completada")
                
            except Exception as e:
                logger.error(f"❌ Error en inicialización de cache: {e}")
                # No fallar el startup por esto
            
            logger.info("🚀 Sistema de cache LRU listo - rendimiento optimizado!")

            yield
            
            # 🛑 CLEANUP AL CERRAR
            logger.info("🔧 Deteniendo sistemas de mantenimiento...")
            try:
                await stop_cache_maintenance()
                await stop_metrics_logging() 
                logger.info("✅ Mantenimiento detenido correctamente")
            except Exception as e:
                logger.error(f"❌ Error en cleanup: {e}")
        
        if hasattr(app.state, "scheduler"):
            app.state.scheduler.shutdown()

app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

app.add_middleware(
    RateLimitMiddleware,
    rate_limit=10,
    time_window=60
)

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"]
)

setup_csrf_protection(app)

app.include_router(api_router)
