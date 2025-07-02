# Exercise Log Factory Implementation

## Overview

This document describes the implementation of a Factory Pattern solution for handling exercise logs across multiple fitness disciplines in the FitCoach AI application.

## Problem Solved

Previously, the application had discipline-specific CRUD operations for exercise logs (hypertrophy, max_strength, endurance, etc.) but lacked a unified way to handle them in generic endpoints like `workouts_router.py`. This caused issues when trying to retrieve exercise logs without knowing the specific discipline beforehand.

## Solution Architecture

### 1. Factory Pattern (`db/crud/exercise_log_factory.py`)

The `ExerciseLogCRUDFactory` class provides a centralized registry of CRUD operations for all fitness disciplines:

```python
class ExerciseLogCRUDFactory:
    _discipline_crud_registry = {
        TrainingDiscipline.HYPERTROPHY: {
            'get_log': get_hypertrophy_log,
            'get_workout_logs': get_workout_hypertrophy_logs,
            'update_log': update_hypertrophy_log,
            'delete_log': delete_hypertrophy_log,
        },
        # ... other disciplines
    }
```

**Key Methods:**
- `get_exercise_log(db, exercise_id, discipline)` - Get single exercise log
- `get_workout_logs(db, workout_id, discipline)` - Get all logs for a workout
- `update_exercise_log(db, exercise_id, discipline, update_data)` - Update log
- `delete_exercise_log(db, exercise_id, discipline)` - Delete log

### 2. Core Service Layer (`core/services/exercise_log.py`)

The `CoreExerciseLogService` provides high-level business logic that automatically determines the discipline from the workout:

```python
class CoreExerciseLogService:
    @staticmethod
    async def get_exercise_log_by_workout(db, exercise_id, workout_id, user_id=None):
        # Automatically determines discipline from workout
        # Handles authorization
        # Delegates to factory
```

**Key Features:**
- Automatic discipline detection from workout
- Built-in authorization checks
- Consistent error handling
- Type safety

### 3. Base Mixin (`db/models/discipline_exercise_logs/base.py`)

Common functionality for all exercise log models:

```python
class BaseExerciseLogMixin:
    def get_common_fields(self) -> dict:
        # Returns common fields across all disciplines
    
    def get_discipline_name(self) -> str:
        # Returns discipline name from table name
    
    def to_dict(self) -> dict:
        # Converts to dictionary with discipline info
```

### 4. Schema Abstractions (`db/schemas/discipline_exercise_logs/base.py`)

Union types and base schemas for API responses:

```python
ExerciseLogResponse = Union[
    HypertrophyLog, MaxStrengthLog, EnduranceLog, PowerLog,
    BalanceLog, FlexibilityLog, CoordinationLog, CardioLog, CoreStabilityLog
]

class BaseExerciseLogResponse(BaseModel):
    # Common response format for all disciplines
```

### 5. Updated Router (`api/routes/workouts_router.py`)

Simplified endpoints using the new architecture:

```python
@workouts_router.get("/{workout_id}/exercises")
async def list_workout_exercises(...):
    logs_dicts = await CoreExerciseLogService.get_exercise_logs_as_dicts(
        db, workout_id, current_user.id
    )
    return [BaseExerciseLogResponse(**log_dict) for log_dict in logs_dicts]
```

## Benefits

### 1. **Maintainability**
- Single point of configuration for all disciplines
- Easy to add new disciplines
- Consistent patterns across the codebase

### 2. **Type Safety**
- Strong typing with Union types
- Protocol-based interfaces
- Compile-time error detection

### 3. **Performance**
- No unnecessary JOINs or queries
- Discipline-specific optimizations preserved
- Efficient database access patterns

### 4. **Scalability**
- Easy to add new fitness disciplines
- Modular architecture
- Clear separation of concerns

### 5. **Developer Experience**
- Simplified router code
- Consistent error handling
- Clear abstractions

## Usage Examples

### Getting Exercise Logs for a Workout

```python
# Old way (discipline-specific)
if workout.discipline == TrainingDiscipline.HYPERTROPHY:
    logs = await get_workout_hypertrophy_logs(db, workout_id)
elif workout.discipline == TrainingDiscipline.MAX_STRENGTH:
    logs = await get_workout_max_strength_logs(db, workout_id)
# ... etc

# New way (automatic)
logs = await CoreExerciseLogService.get_workout_exercise_logs(
    db, workout_id, user_id
)
```

### Getting a Single Exercise Log

```python
# Old way (manual discipline detection)
workout = await get_workout(db, workout_id)
if workout.discipline == TrainingDiscipline.HYPERTROPHY:
    log = await get_hypertrophy_log(db, exercise_id)
# ... etc

# New way (automatic)
log = await CoreExerciseLogService.get_exercise_log_by_workout(
    db, exercise_id, workout_id, user_id
)
```

## Files Modified/Created

### Created Files:
- `app/db/models/discipline_exercise_logs/base.py`
- `app/db/crud/exercise_log_factory.py`
- `app/core/services/exercise_log.py`
- `app/db/schemas/discipline_exercise_logs/base.py`

### Modified Files:
- `app/api/routes/workouts_router.py` - Updated to use new architecture
- `app/db/crud/utils.py` - Added helper functions
- `app/exceptions/api.py` - Added NotFoundError and ForbiddenError
- `app/db/models/discipline_exercise_logs/__init__.py` - Added exports
- `app/db/models/discipline_exercise_logs/hypertrophy.py` - Added mixin

## Migration Notes

### Endpoints Status:
- ✅ `GET /{workout_id}/exercises` - Fully implemented
- ✅ `GET /{workout_id}/exercises/{exercise_id}` - Fully implemented  
- ✅ `DELETE /{workout_id}/exercises/{exercise_id}` - Fully implemented
- ⏸️ `POST /{workout_id}/exercises` - Disabled (use discipline-specific endpoints)
- ⏸️ `PUT /{workout_id}/exercises/{exercise_id}` - Disabled (use discipline-specific endpoints)

### Why Some Endpoints are Disabled:
Creation and update operations require discipline-specific schemas and validation. These operations should be handled by the individual discipline endpoints in `/api/routes/exercises/` rather than generic workout endpoints.

## Future Enhancements

1. **Automatic Schema Detection**: Implement automatic schema detection for POST/PUT operations
2. **Caching Layer**: Add caching for frequently accessed exercise logs
3. **Batch Operations**: Support for bulk operations across disciplines
4. **Analytics Integration**: Enhanced analytics across all disciplines
5. **Validation Framework**: Unified validation across all disciplines

## Testing

The implementation includes comprehensive error handling and has been verified for:
- ✅ Factory pattern structure
- ✅ Service layer functionality  
- ✅ Import dependencies
- ✅ Code compilation
- ✅ Router integration

## Conclusion

This implementation successfully solves the original problem while maintaining the benefits of discipline-specific models and adding significant architectural improvements. The factory pattern provides a clean, scalable solution that will serve the application well as it grows. 