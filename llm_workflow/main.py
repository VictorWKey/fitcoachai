from db import init_db
from fastapi import FastAPI
from api.routes import api_router
from utils import wait_for_server_and_load_model

app = FastAPI(title="FitCoach AI")

@app.on_event("startup")
async def on_startup():
    wait_for_server_and_load_model()
    init_db()

app.include_router(api_router)





