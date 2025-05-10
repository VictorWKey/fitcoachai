# api/services/chat_service.py
from langchain_core.messages import HumanMessage

async def process_agent(user_input: str, config: dict, agent) -> dict:
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config
    )
    return response
