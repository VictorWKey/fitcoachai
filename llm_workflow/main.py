# main.py
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import os
from api.routes import api_router
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_ollama import ChatOllama
from utils.utils import wait_for_server_and_load_model
from agent.agent import get_agent
from db import init_db
from agent.tools.log_exercise import log_exercise

DB_URI = os.getenv("DATABASE_URL")
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    await wait_for_server_and_load_model()
    
    await init_db()
    
    async with AsyncConnectionPool(
        conninfo=DB_URI,
        min_size=5,
        max_size=10,
        timeout=30,
        max_lifetime=1800,
        kwargs=connection_kwargs
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()

        llm = ChatOllama(
            model=MODEL_NAME,
            temperature=0.2,
            base_url=OLLAMA_API_BASE_URL,
        ).bind_tools([log_exercise])

        agent = get_agent(llm=llm, checkpointer=checkpointer, tools=[log_exercise])
        
        print(agent.get_graph().draw_mermaid())

        app.state.pool = pool
        app.state.llm = llm
        app.state.checkpointer = checkpointer
        app.state.agent = agent

        yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)





