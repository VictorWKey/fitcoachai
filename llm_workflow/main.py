# main.py
from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import os
from api.routes import api_router
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langchain_ollama import ChatOllama

from agent.agent import get_agent

DB_URI = os.getenv("DATABASE_URL")
OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

@asynccontextmanager
async def lifespan(app: FastAPI):
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
        )

        agent = get_agent(llm=llm, checkpointer=checkpointer)

        app.state.pool = pool
        app.state.llm = llm
        app.state.checkpointer = checkpointer
        app.state.agent = agent

        yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)





