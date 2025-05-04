from agent import Agent
from db import init_db
from fastapi import FastAPI
from api import api_router
from utils import wait_for_server_and_load_model

wait_for_server_and_load_model()

init_db()

app = FastAPI(title="FitCoach AI")

app.include_router(api_router)



