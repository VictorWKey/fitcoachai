# api/services/chat_service.py
from langchain_core.messages import HumanMessage, SystemMessage


SYSTEM_MESSAGE = SystemMessage(
    content="""
    Eres un asistente de IA profesional en entrenamiento y nutrición.       
    """
)

async def process_agent(user_input: str, config: dict, agent, user_chat_history_exists: bool) -> dict:
    
    if user_chat_history_exists:
        response = await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(content=user_input)
                ],
            },
            config=config
        )
    else:
        response = await agent.ainvoke(
            {
                "messages": [
                    SYSTEM_MESSAGE, 
                    HumanMessage(content=user_input)
                ],
            },
            config=config
        )
    return response
