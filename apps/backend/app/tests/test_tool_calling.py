import os
import asyncio
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_core.tools import tool
from typing import Annotated
from pydantic import Field

load_dotenv()

def test_tool_calling():
    # Configurar el modelo de OpenAI
    llm = ChatOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        model="gpt-4.1-nano-2025-04-14"
    )

    class Clima(BaseModel):
        ciudad: str
        pais: Annotated[str, Field(description="El pais debe ser un diccionario de python con el nombre del pais y el color de la bandera")]

    @tool("Clima", args_schema=Clima)
    def clima(ciudad: str, pais: str) -> str:
        """
        Devuelve el clima de una ciudad y un pais
        """
        return f"El clima en {ciudad}, {pais} es soleado"
    
    # Vincular las herramientas al modelo
    llm_with_tools = llm.bind_tools([clima])
    
    # Ejemplo de consulta para probar tool calling
    query = "Que clima hace en Madrid, España (pais con bandera roja)?"
    
    # Invocar el modelo con la consulta
    response = llm_with_tools.invoke(query)
    
    # Imprimir la respuesta y las llamadas a herramientas
    print("Respuesta:", response)
  

if __name__ == "__main__":
    test_tool_calling()
