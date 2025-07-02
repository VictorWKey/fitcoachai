"""
Fitness discipline CRUD operations package.
"""

from .max_strength import (
    create_max_strength_log,
    get_max_strength_log,
    get_user_max_strength_logs,
    get_workout_max_strength_logs,
    update_max_strength_log,
    delete_max_strength_log
)

from .hypertrophy import (
    create_hypertrophy_log,
    get_hypertrophy_log,
    get_user_hypertrophy_logs,
    get_workout_hypertrophy_logs,
    update_hypertrophy_log,
    delete_hypertrophy_log
)







from .flexibility import (
    create_flexibility_log,
    get_flexibility_log,
    get_user_flexibility_logs,
    get_workout_flexibility_logs,
    update_flexibility_log,
    delete_flexibility_log
)



from .cardio import (
    create_cardio_log,
    get_cardio_log,
    get_user_cardio_logs,
    get_workout_cardio_logs,
    update_cardio_log,
    delete_cardio_log
)



__all__ = [
    # Max Strength
    "create_max_strength_log",
    "get_max_strength_log",
    "get_user_max_strength_logs",
    "get_workout_max_strength_logs",
    "update_max_strength_log",
    "delete_max_strength_log",
    
    # Hypertrophy
    "create_hypertrophy_log",
    "get_hypertrophy_log",
    "get_user_hypertrophy_logs",
    "get_workout_hypertrophy_logs",
    "update_hypertrophy_log",
    "delete_hypertrophy_log",
    
    
    

    
    # Balance
    "create_balance_log",
    "get_balance_log",
    "get_user_balance_logs",
    "get_workout_balance_logs",
    "update_balance_log",
    "delete_balance_log",
    
    # Flexibility
    "create_flexibility_log",
    "get_flexibility_log",
    "get_user_flexibility_logs",
    "get_workout_flexibility_logs",
    "update_flexibility_log",
    "delete_flexibility_log",
    
    
    
    # Cardio
    "create_cardio_log",
    "get_cardio_log",
    "get_user_cardio_logs",
    "get_workout_cardio_logs",
    "update_cardio_log",
    "delete_cardio_log",
    
    
] 