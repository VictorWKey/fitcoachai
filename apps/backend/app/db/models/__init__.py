"""
ORM models for the FitCoach AI application.
Defines the data structure and relationships between entities in the database.
"""

from .user import User
from .chat_history import ChatHistory
from .workout import Workout, MuscleGroup, Category
from .exercise_log import ExerciseLog, WeightUnit
from .token import TokenBlacklist