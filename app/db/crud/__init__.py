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

from .exercise_log import (
    create_exercise_log,
    get_exercise_log,
    get_workout_logs,
    update_exercise_log,
    delete_exercise_log,
)

from .utils import (
    get_or_create_workout_id,
)