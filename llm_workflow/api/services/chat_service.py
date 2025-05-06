from langchain.schema.messages import HumanMessage
from langchain.schema.runnable import RunnableConfig
from agent.agent import agents

async def process_agent(user_input: str, config: dict) -> str:
    if agents["agent"] is None:
        raise Exception("Agent aún no ha sido cargado")
    
    # TODO: Add thread_id to the config
    
    response = await agents["agent"].ainvoke({"messages": [{"role": "user", "content": user_input}]}, config)
    return response