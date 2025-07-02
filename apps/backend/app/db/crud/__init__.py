"""
CRUD (Create, Read, Update, Delete) module for database operations.
Provides access to CRUD functions for all application models.
"""

from .user import (
    create_user,
    get_user,
    get_user_by_email,
    get_user_by_username,
    update_user,
    delete_user,
    get_users,
    get_password_hash,
    verify_password
)

from .workout import (
    create_workout,
    get_workout,
    get_user_workouts,
    update_workout,
    delete_workout,
)

from .discipline_exercise_logs import (
    # Max Strength
    create_max_strength_log, get_max_strength_log, get_user_max_strength_logs,
    get_workout_max_strength_logs, update_max_strength_log, delete_max_strength_log,
    # Hypertrophy
    create_hypertrophy_log, get_hypertrophy_log, get_user_hypertrophy_logs,
    get_workout_hypertrophy_logs, update_hypertrophy_log, delete_hypertrophy_log,
    # Flexibility
    create_flexibility_log, get_flexibility_log, get_user_flexibility_logs,
    get_workout_flexibility_logs, update_flexibility_log, delete_flexibility_log,
    # Cardio
    create_cardio_log, get_cardio_log, get_user_cardio_logs,
    get_workout_cardio_logs, update_cardio_log, delete_cardio_log
)

from .utils import (
    get_or_create_workout_id,
)