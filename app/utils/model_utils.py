"""
Utilities for managing and configuring LLM models.
"""

import httpx
import asyncio
import os
from langchain_core import runnables
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles
from config.app_settings import settings

async def wait_for_server_and_load_model():
    """
    Waits for the Ollama server to be available and loads the specified model.

    This function continuously checks the availability of the Ollama server. Once it's up,
    it verifies whether the specified model is downloaded. If not, it triggers the download.
    """
    async with httpx.AsyncClient() as client:
        while True:
            try:
                r = await client.get(f"{settings.OLLAMA_API_BASE_URL}/api/version")
                if r.status_code == 200:
                    print("✅ Ollama server is ready!")
                    break
            except Exception:
                print("⏳ Waiting for Ollama server...")
            await asyncio.sleep(2)

        # Check if the model is already downloaded
        r = await client.get(f"{settings.OLLAMA_API_BASE_URL}/api/tags")
        models = r.json().get("models", [])

        if not any(model["name"] == settings.MODEL_NAME for model in models):
            print(f"⬇️ Model {settings.MODEL_NAME} not found, pulling...")
            r = await client.post(f"{settings.OLLAMA_API_BASE_URL}/api/pull", json={"name": settings.MODEL_NAME})
            r.raise_for_status()
            print(f"✅ Model {settings.MODEL_NAME} downloaded!")

def stream_graph_updates(graph, user_input: str):
    """
    Streams updates from a LangGraph in real time based on user input.

    Args:
        graph: The LangGraph instance.
        user_input (str): Input message from the user.
    """
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value)

def coerce_null_string(v):
    """
    Converts a 'null' string or empty string to None.

    Args:
        v: The value to convert.

    Returns:
        None if v is 'null' or an empty string, otherwise returns v unchanged.
    """
    if v == "null" or v == "":
        return None
    return v
