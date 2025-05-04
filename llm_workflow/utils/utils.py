import requests
import time
import os

OLLAMA_API_BASE_URL = os.getenv("OLLAMA_API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

def wait_for_server_and_load_model():
  # Wait for Ollama to be ready
  while True:
      try:
          r = requests.get(f"{OLLAMA_API_BASE_URL}/api/version")
          if r.status_code == 200:
              print("✅ Ollama server is ready!")
              break
      except Exception:
          print("⏳ Waiting for Ollama server...")
      time.sleep(2)

  # Check if the model is already downloaded
  r = requests.get(f"{OLLAMA_API_BASE_URL}/api/tags")
  models = r.json().get("models", [])

  if not any(model["name"] == MODEL_NAME for model in models):
      print(f"⬇️ Model {MODEL_NAME} not found, pulling...")
      r = requests.post(f"{OLLAMA_API_BASE_URL}/api/pull", json={"name": MODEL_NAME})
      r.raise_for_status()
      print(f"✅ Model {MODEL_NAME} downloaded!")
      
def save_graph_image(graph, filename):
    image_data = graph.get_graph().draw_mermaid_png()

    with open(filename, "wb") as f:
        f.write(image_data)
        
def stream_graph_updates(graph, user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value)


