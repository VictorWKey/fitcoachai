import requests
import time
import os
from langchain_core import runnables
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
import asyncio
import httpx

OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

async def wait_for_server_and_load_model():
    # Wait for Ollama to be ready
    async with httpx.AsyncClient() as client:
        while True:
            try:
                r = await client.get(f"{OLLAMA_API_BASE_URL}/api/version")
                if r.status_code == 200:
                    print("✅ Ollama server is ready!")
                    break
            except Exception:
                print("⏳ Waiting for Ollama server...")
            await asyncio.sleep(2)

        # Check if the model is already downloaded
        r = await client.get(f"{OLLAMA_API_BASE_URL}/api/tags")
        models = r.json().get("models", [])

        if not any(model["name"] == MODEL_NAME for model in models):
            print(f"⬇️ Model {MODEL_NAME} not found, pulling...")
            r = await client.post(f"{OLLAMA_API_BASE_URL}/api/pull", json={"name": MODEL_NAME})
            r.raise_for_status()
            print(f"✅ Model {MODEL_NAME} downloaded!")
        
def stream_graph_updates(graph, user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value)

def coerce_null_string(v):
    if v == "null" or v == "":
        return None
    return v