"""
Punto de entrada principal para la aplicación FitCoach AI.
"""

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_openai import ChatOpenAI
from agent.agent import get_agent
from agent.tools.log_exercise import log_exercise
from db import init_db
from api.routes import api_router
from middleware import RateLimitMiddleware, SecurityHeadersMiddleware, setup_csrf_protection
from config.app_settings import settings
from config.db_settings import db_settings
from utils.model_utils import wait_for_server_and_load_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Configuración del ciclo de vida de la aplicación.
    
    Args:
        app: La instancia de FastAPI
    """
    # Comentado porque solo se necesita cuando se usa Ollama localmente
    # await wait_for_server_and_load_model()
    
    # Inicializar la base de datos
    await init_db()
    
    # Configurar el pool de conexiones para PostgreSQL
    async with AsyncConnectionPool(
        conninfo=db_settings.PSYCOPG_DATABASE_URL,
        min_size=db_settings.POOL_SIZE,
        max_size=db_settings.MAX_OVERFLOW,
        timeout=db_settings.POOL_TIMEOUT,
        max_lifetime=db_settings.POOL_RECYCLE,
        kwargs=db_settings.CONNECTION_KWARGS
    ) as pool:
        # Configurar el checkpointer para LangGraph
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        # Configurar el modelo de lenguaje
        llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0,
            max_tokens=1000,
        ).bind_tools([log_exercise])

        # Crear el agente
        agent = get_agent(llm=llm, checkpointer=checkpointer, tools=[log_exercise])
        
        # Guardar referencias en el estado de la aplicación
        app.state.pool = pool
        app.state.llm = llm
        app.state.checkpointer = checkpointer
        app.state.agent = agent

        yield

# Crear la aplicación FastAPI
app = FastAPI(
    lifespan=lifespan,
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Configurar middlewares
app.add_middleware(
    RateLimitMiddleware,
    rate_limit=10,
    time_window=60
)

app.add_middleware(SecurityHeadersMiddleware)

# Configurar CORS y TrustedHost
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

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

# Configurar protección CSRF
setup_csrf_protection(app)

# Incluir rutas de la API
app.include_router(api_router)





