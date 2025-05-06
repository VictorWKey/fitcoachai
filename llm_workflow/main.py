from db import init_db
from fastapi import FastAPI
import fastapi
from api.routes import api_router
from utils import wait_for_server_and_load_model
from contextlib import asynccontextmanager
from agent.agent import get_agent
from agent.agent import agents

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Cargando modelo LLM...")
    agents["agent"] = await get_agent()
    print("✅ Modelo cargado.")
    yield
    print("🧹 Limpiando recursos del LLM...")
    # Aquí podrías liberar GPU o cerrar sesiones si fuera necesario
    # Por ejemplo: llm.unload() o similar
    
app = FastAPI(title="FitCoach AI", lifespan=lifespan)
    
app.include_router(api_router)





