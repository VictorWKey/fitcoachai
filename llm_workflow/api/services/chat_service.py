# api/services/chat_service.py
from langchain_core.messages import SystemMessage
from agent.prompts import SYSTEM_MESSAGE, USER_MESSAGE
from agent.context import get_history_context

async def process_agent(user_input: str, config: dict, agent, user_chat_history_exists: bool) -> dict:
    user_history_context = await get_history_context(config["configurable"]["user_id"], n_logs=3)

    # Crear los mensajes del usuario desde el template
    user_messages = USER_MESSAGE.format_messages(input=user_input, history=user_history_context)
    
    # print(user_messages)

    # Armar la lista de mensajes según haya historial o no
    if user_chat_history_exists:
        messages = [user_messages[0]]
    else:
        messages = [SYSTEM_MESSAGE, user_messages[0]]
        
    # for msg in messages:
    #     print(f"{type(msg)=} | {msg.content=}")


    # # Ejecutar el agente
    response = await agent.ainvoke(
        {"messages": messages},
        config=config
    )

    return response
