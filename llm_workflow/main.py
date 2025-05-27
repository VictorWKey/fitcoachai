# main.py
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from typing import List, Optional
from api.routes import api_router
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from utils.utils import wait_for_server_and_load_model
from agent.agent import get_agent
from db import init_db
from agent.tools.log_exercise import log_exercise
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic import BaseModel
from middleware import RateLimitMiddleware

# Configuración CSRF
class CsrfSettings(BaseModel):
    secret_key: str = os.getenv("SECRET_KEY", "very_secret_key_for_csrf")
    token_location: Optional[str] = "header"
    cookie_secure: bool = False 
    cookie_samesite: str = "lax"

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# Get the database URL from environment and convert to proper psycopg format if needed
DATABASE_URL = os.getenv("DATABASE_URL")

OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

# Hosts de confianza (para producción)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

CORS_ORIGINS = os.getenv("CORS_ORIGINS").split(",")

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

# Middleware para añadir cabeceras de seguridad
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Cabeceras de seguridad recomendadas
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none'"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    # await wait_for_server_and_load_model() # Activar cuando se use Ollama localmente
    
    await init_db()
    
    async with AsyncConnectionPool(
        conninfo=DATABASE_URL,
        min_size=5,
        max_size=10,
        timeout=30,
        max_lifetime=1800,
        kwargs=connection_kwargs
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        # llm = ChatOllama(
        #     model=MODEL_NAME,
        #     temperature=0.2,
        #     base_url=OLLAMA_API_BASE_URL,
        # ).bind_tools([log_exercise])

        llm = ChatOpenAI(
            model=MODEL_NAME,
            temperature=0,
            max_tokens=1000,
        ).bind_tools([log_exercise])

        agent = get_agent(llm=llm, checkpointer=checkpointer, tools=[log_exercise])
        
        # print(agent.get_graph().draw_mermaid())

        app.state.pool = pool
        app.state.llm = llm
        app.state.checkpointer = checkpointer
        app.state.agent = agent

        yield

app = FastAPI(
    lifespan=lifespan,
    title="FitCoach AI API",
    description="API para la aplicación FitCoach AI",
    version="1.0.0"
)

# Agregar middleware de rate limiting
app.add_middleware(
    RateLimitMiddleware,
    rate_limit=10,  # 10 solicitudes
    time_window=60  # por minuto
)

# Agregar middleware de seguridad
app.add_middleware(SecurityHeadersMiddleware)

# Limitar hosts de confianza
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-CSRF-Token"]
)

# Manejo de excepciones para CSRF
@app.exception_handler(CsrfProtectError)
async def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

app.include_router(api_router)





