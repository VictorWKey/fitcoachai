"""
Factory for creating custom agents per user based on their training discipline.
Implements advanced LRU cache with metrics to optimize performance.
"""

from typing import Optional, Dict, List
from db.crud.user import get_user_training_discipline
from db.session import db_session
from db.models.workout import TrainingDiscipline
from .tool_factory import get_tools_for_discipline
from .agent import get_agent
from .lru_cache import global_agent_cache, create_tool_combination_key, CacheMetrics
import asyncio
import logging

logger = logging.getLogger(__name__)

async def get_agent_for_user(user_id: int, llm, checkpointer):
    """
    Creates a custom agent for the user based on their preferred discipline.
    Uses advanced LRU cache with metrics for maximum performance and scalability.
    
    Args:
        user_id: User ID
        llm: Base language model (without tools)
        checkpointer: Checkpointer for agent state
        
    Returns:
        Agent: Agent configured with appropriate tools for the user
    """
    
    # Get the user's preferred discipline
    async with db_session() as db:
        user_discipline = await get_user_training_discipline(db, user_id)
    
    if not user_discipline:
        user_discipline = TrainingDiscipline.HYPERTROPHY
    
    # For simple disciplines, use the discipline as key
    tool_names = [user_discipline.value]
    tool_combination_key = create_tool_combination_key(tool_names)
    
    # Function to create agent if not in cache
    async def create_agent_func():
        logger.info(f"Compiling new agent for discipline: {user_discipline.value}")
        
        # Get appropriate tools for the discipline
        tools = get_tools_for_discipline(user_discipline)
        
        # Create LLM with specific tools
        llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=True)
        
        # Create and compile agent (expensive operation)
        agent = get_agent(llm=llm_with_tools, checkpointer=checkpointer, tools=tools)
        
        return agent
    
    # Additional data for metrics
    tool_combination_data = {
        "description": f"Discipline: {user_discipline.value}",
        "discipline": user_discipline.value
    }
    
    # Get or create agent using LRU cache
    agent = await global_agent_cache.get_or_create_agent(
        tool_combination_key=tool_combination_key,
        create_func=create_agent_func,
        tool_combination_data=tool_combination_data
    )
    
    logger.info(f"Agent obtained for user {user_id} (discipline: {user_discipline.value})")
    return agent

async def get_agent_for_custom_tools(
    user_id: int, 
    selected_tools: List[str], 
    llm, 
    checkpointer,
    user_preferences: Optional[Dict] = None
):
    """
    Creates an agent for custom tool combinations.
    Prepared for the future when users can choose specific tools.
    
    Args:
        user_id: User ID
        selected_tools: List of selected tool names
        llm: Base language model
        checkpointer: Checkpointer for agent state
        user_preferences: Additional user preferences
        
    Returns:
        Agent: Agent with custom tools
    """
    
    # Create unique key for this combination
    tool_combination_key = create_tool_combination_key(selected_tools, user_preferences)
    
    # Function to create custom agent
    async def create_custom_agent_func():
        logger.info(f"Compiling custom agent for user {user_id} with tools: {selected_tools}")
        
        # Here would go the logic to get tools by name
        # For now, use get_tools_for_discipline as fallback
        from db.models.workout import TrainingDiscipline
        
        # Determine primary discipline based on selected tools
        primary_discipline = _infer_primary_discipline(selected_tools)
        tools = get_tools_for_discipline(primary_discipline)
        
        # Create LLM with tools
        llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=True)
        
        # Compile agent
        agent = get_agent(llm=llm_with_tools, checkpointer=checkpointer, tools=tools)
        
        return agent
    
    # Data for metrics
    tool_combination_data = {
        "description": f"Custom: {', '.join(selected_tools)}",
        "tools": selected_tools,
        "user_preferences": user_preferences
    }
    
    # Get or create agent
    agent = await global_agent_cache.get_or_create_agent(
        tool_combination_key=tool_combination_key,
        create_func=create_custom_agent_func,
        tool_combination_data=tool_combination_data
    )
    
    logger.info(f"Custom agent obtained for user {user_id}")
    return agent

def _infer_primary_discipline(tool_names: List[str]) -> TrainingDiscipline:
    """
    Infers the primary discipline based on tool names.
    Helper function for custom combinations.
    """
    # Mapping of tools to disciplines
    tool_discipline_map = {
        "exercise_log_hypertrophy": TrainingDiscipline.HYPERTROPHY,
        "exercise_log_max_strength": TrainingDiscipline.MAX_STRENGTH,
        "exercise_log_cardio": TrainingDiscipline.CARDIO,
        "exercise_log_flexibility": TrainingDiscipline.FLEXIBILITY
    }
    
    # Search for first discipline found
    for tool_name in tool_names:
        if tool_name in tool_discipline_map:
            return tool_discipline_map[tool_name]
    
    # Fallback to hypertrophy
    return TrainingDiscipline.HYPERTROPHY

async def get_cache_metrics() -> CacheMetrics:
    """
    Gets the current metrics from the agent cache.
    
    Returns:
        CacheMetrics: Detailed cache metrics
    """
    return await global_agent_cache.get_metrics()

async def get_cache_detailed_stats() -> Dict:
    """
    Gets detailed cache statistics for monitoring.
    
    Returns:
        Dict: Detailed statistics including individual entries
    """
    return await global_agent_cache.get_cache_stats()

async def clear_agent_cache():
    """
    Completely clears the agent cache.
    Useful for development, testing or when tools are updated.
    """
    await global_agent_cache.clear_cache()
    logger.info("Agent cache completely cleared")

async def cleanup_expired_agents() -> int:
    """
    Cleans up expired agents from cache.
    
    Returns:
        int: Number of agents removed
    """
    removed_count = await global_agent_cache.remove_expired()
    logger.info(f"Expired agent cleanup completed: {removed_count} removed")
    return removed_count

def get_cached_agent_count() -> int:
    """
    Gets the current number of agents in cache.
    Synchronous function for quick access.
    
    Returns:
        int: Number of cached agents
    """
    return len(global_agent_cache.cache)

async def precompile_popular_agents(llm, checkpointer, popular_disciplines: Optional[List[TrainingDiscipline]] = None):
    """
    Pre-compiles agents for popular disciplines at server startup.
    Improves user experience by eliminating first compilation latency.
    
    Args:
        llm: Base language model
        checkpointer: Checkpointer for state
        popular_disciplines: List of disciplines to pre-compile (optional)
    """
    if not popular_disciplines:
        # Most popular disciplines by default
        popular_disciplines = [
            TrainingDiscipline.HYPERTROPHY,      # 40% of users typically
            TrainingDiscipline.MAX_STRENGTH,    # 25% of users
            TrainingDiscipline.CARDIO,          # 20% of users
        ]
    
    logger.info(f"Starting pre-compilation of {len(popular_disciplines)} popular agents...")
    
    compilation_tasks = []
    for discipline in popular_disciplines:
        # Create task for concurrent compilation
        task = asyncio.create_task(
            _precompile_single_agent(discipline, llm, checkpointer)
        )
        compilation_tasks.append(task)
    
    # Wait for all compilations to finish
    results = await asyncio.gather(*compilation_tasks, return_exceptions=True)
    
    successful_compilations = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error pre-compiling {popular_disciplines[i].value}: {result}")
        else:
            successful_compilations += 1
    
    logger.info(f"Pre-compilation completed: {successful_compilations}/{len(popular_disciplines)} agents ready")

async def _precompile_single_agent(discipline: TrainingDiscipline, llm, checkpointer):
    """Pre-compiles a single agent for a specific discipline"""
    try:
        # Simulate fictional user_id for pre-compilation
        tool_names = [discipline.value]
        tool_combination_key = create_tool_combination_key(tool_names)
        
        async def create_precompiled_agent():
            tools = get_tools_for_discipline(discipline)
            llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=True)
            return get_agent(llm=llm_with_tools, checkpointer=checkpointer, tools=tools)
        
        tool_combination_data = {
            "description": f"Pre-compiled: {discipline.value}",
            "discipline": discipline.value
        }
        
        await global_agent_cache.get_or_create_agent(
            tool_combination_key=tool_combination_key,
            create_func=create_precompiled_agent,
            tool_combination_data=tool_combination_data
        )
        
        logger.info(f"✅ Agent pre-compiled: {discipline.value}")
        
    except Exception as e:
        logger.error(f"❌ Error pre-compiling {discipline.value}: {e}")
        raise
