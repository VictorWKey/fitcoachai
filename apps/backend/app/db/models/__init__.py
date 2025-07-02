"""
ORM models for the FitCoach AI application.
Defines the data structure and relationships between entities in the database.
"""

from .user import User
from .chat_history import ChatHistory
from .workout import Workout, MuscleGroup, TrainingDiscipline
from .token import TokenBlacklist
from .discipline_exercise_logs.hypertrophy import HypertrophyLog
from .discipline_exercise_logs.flexibility import FlexibilityLog
from .discipline_exercise_logs.cardio import CardioLog
from .discipline_exercise_logs.common import WeightUnit, RangeOfMotion