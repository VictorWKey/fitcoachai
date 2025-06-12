"""
Main entry point for the FitCoach AI application.
"""

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_openai import ChatOpenAI
from agent.agent import get_agent
from agent.tools.log_exercise import log_exercise
from agent.tools.finish_workout import finish_workout
from db import init_db
from api.routes import api_router
from middleware import RateLimitMiddleware, SecurityHeadersMiddleware, setup_csrf_protection
from config.app_settings import settings
from config.db_settings import db_settings
from utils.model_utils import wait_for_server_and_load_model
from jobs.auto_finish_workouts import setup_auto_finish_job
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
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        llm = ChatOpenAI(
            model=settings.MODEL_NAME,
            temperature=0,
            max_tokens=1000,
        ).bind_tools([log_exercise, finish_workout])

        agent = get_agent(llm=llm, checkpointer=checkpointer, tools=[log_exercise, finish_workout])
        
        app.state.pool = pool
        app.state.llm = llm
        app.state.checkpointer = checkpointer
        app.state.agent = agent
        
        await setup_auto_finish_job(
            app,
            enable_job=settings.ENABLE_AUTO_FINISH_JOB,
            interval_minutes=settings.AUTO_FINISH_JOB_INTERVAL
        )

        yield
        
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
