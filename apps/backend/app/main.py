"""
Main entry point for the FitCoach AI application.
"""

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_openai import ChatOpenAI
from agent.agent import get_agent
from agent import TRAINING_TOOLS
from db import init_db
from api.routes import api_router
from middleware import RateLimitMiddleware, SecurityHeadersMiddleware, setup_csrf_protection
from config.app_settings import settings
from config.db_settings import db_settings
from core.services.session_monitor import start_session_monitor, stop_session_monitor
from utils.model_utils import wait_for_server_and_load_model
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan configuration.
    
    Args:
        app: The FastAPI instance
    """
    # Uncomment when using Ollama locally
    # await wait_for_server_and_load_model
    
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

        async with pool.connection() as conn:
            checkpointer = AsyncPostgresSaver(conn)  # Aquí pasas la conexión, no el pool
            await checkpointer.setup()

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                max_completion_tokens=10000
            ).bind_tools(TRAINING_TOOLS)

            agent = get_agent(llm=llm, checkpointer=checkpointer, tools=TRAINING_TOOLS)
            
            app.state.pool = pool
            app.state.llm = llm
            app.state.checkpointer = checkpointer
            app.state.agent = agent

            yield
            
            if hasattr(app.state, "scheduler"):
                app.state.scheduler.shutdown()
                
            await stop_session_monitor()
    
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
