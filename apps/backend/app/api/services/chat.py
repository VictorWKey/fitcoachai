from langchain_core.messages import SystemMessage
from agent.prompts import get_system_message, USER_MESSAGE
from agent.context import get_history_context
from agent.agent_factory import get_agent_for_user
from db.crud.user import get_user_training_discipline
from db.session import db_session
from db.models.workout import TrainingDiscipline

async def process_agent(
    user_input: str, 
    config: dict, 
    llm_base,
    checkpointer,
    user_chat_history_exists: bool,
    system_message_needs_update: bool = False
) -> dict:
    """
    Processes the user's input and gets a response from the agent.
    
    Args:
        user_input: The user's input text.
        config: Configuration for the agent.
        llm_base: Base LLM without tools.
        checkpointer: Checkpointer for agent state.
        user_chat_history_exists: Indicates whether there is existing chat history.
        system_message_needs_update: Flag indicating if system message needs to be updated.
        
    Returns:
        dict: The agent's response.
    """
    # Get user-specific agent based on their discipline
    # OPTIMIZACIÓN: El agente se cachea por disciplina para evitar recompilaciones
    user_id = config["configurable"]["user_id"]
    agent = await get_agent_for_user(user_id, llm_base, checkpointer)
    
    user_history_context = await get_history_context(
        user_id, 
        n_logs=3
    )

    user_messages = USER_MESSAGE.format_messages(
        input=user_input, 
        history=user_history_context
    )
    
    # Prepare initial messages
    if user_chat_history_exists:
        messages = [user_messages[0]]
    else:
        # For new users, get their current discipline and create system message
        async with db_session() as db:
            user_discipline = await get_user_training_discipline(db, user_id)
            if not user_discipline:
                user_discipline = TrainingDiscipline.HYPERTROPHY
        
        system_message = get_system_message(user_discipline)
        messages = [system_message, user_messages[0]]

    # Add system_message_needs_update flag to config
    config["configurable"]["system_message_needs_update"] = system_message_needs_update

    # Prepare state (simplified, without user-specific flags)
    initial_state = {
        "messages": messages
    }

    response = await agent.ainvoke(
        initial_state,
        config=config
    )

    return response
