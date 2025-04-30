from typing import List

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
import os
import time
import requests
from LLMTools.TrainingLog import TrainingLog

LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = "fitcoachai"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"

OLLAMA_URL = "http://ollama:11434"

OLLAMA_URL = "http://ollama:11434"
MODEL_NAME = "llama3.2:latest"

# Wait for Ollama to be ready
while True:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/version")
        if r.status_code == 200:
            print("✅ Ollama server is ready!")
            break
    except Exception:
        print("⏳ Waiting for Ollama server...")
    time.sleep(2)

# Check if the model is already downloaded
r = requests.get(f"{OLLAMA_URL}/api/tags")
models = r.json().get("models", [])

if not any(model["name"] == MODEL_NAME for model in models):
    print(f"⬇️ Model {MODEL_NAME} not found, pulling...")
    r = requests.post(f"{OLLAMA_URL}/api/pull", json={"name": MODEL_NAME})
    r.raise_for_status()
    print(f"✅ Model {MODEL_NAME} downloaded!")

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
    base_url="http://ollama:11434"
).bind_tools([TrainingLog])

result = llm.invoke(
    "hice 9 repeticiones de press de banca con 100kg en la segunda serie y senti que fue un RIR 2"
)
print(result.content)
print(result.tool_calls)
