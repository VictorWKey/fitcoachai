from typing import List

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv
import time
import requests
load_dotenv()

LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = "fitcoachai"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"

OLLAMA_URL = "http://ollama:11434"

@tool
def validate_user(user_id: int, addresses: List[str]) -> bool:
    """Validate user using historical addresses.

    Args:
        user_id (int): the user ID.
        addresses (List[str]): Previous addresses as a list of strings.
    """
    return True

OLLAMA_URL = "http://ollama:11434"
MODEL_NAME = "llama3.2"

# Esperar a que Ollama esté listo
while True:
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags")
        if r.status_code == 200:
            print("✅ Ollama server está listo!")
            break
    except Exception:
        print("⏳ Esperando a Ollama server...")
    time.sleep(2)

# Verificar si el modelo ya está descargado
r = requests.get(f"{OLLAMA_URL}/api/tags")
models = r.json().get("models", [])

if not any(model["name"] == MODEL_NAME for model in models):
    print(f"⬇️ Modelo {MODEL_NAME} no encontrado, haciendo pull...")
    r = requests.post(f"{OLLAMA_URL}/api/pull", json={"name": MODEL_NAME})
    r.raise_for_status()
    print(f"✅ Modelo {MODEL_NAME} descargado!")


llm = ChatOllama(
    model="llama3.2:latest",
    temperature=0,
    base_url="http://ollama:11434"
).bind_tools([validate_user])

result = llm.invoke(
    "Could you validate user 12345678910? They previously lived at "
    "123 Fake St in Boston MA and 234 Pretend Boulevard in "
    "Houston TX."
)
print(result.content)
print(result.tool_calls)
