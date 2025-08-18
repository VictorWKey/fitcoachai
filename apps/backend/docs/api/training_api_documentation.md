# Training API Documentation

## Overview

The Training API provides a comprehensive system for managing fitness training programs, sessions, exercises, and workout logs. This API follows a hierarchical structure where programs contain weeks, weeks contain sessions, and sessions contain exercises.

## API Hierarchy

```
TrainingProgram (Program)
├── TrainingWeek (Week)
│   └── TrainingSession (Session)
│       └── ProgrammedExercise (Exercise)
│           ├── StrengthLog (Sets/Reps logs)
│           └── CardioLog (Cardio logs)
```

## Core Concepts

### 1. Training Programs
- Container for complete training plans
- Belongs to a specific user
- Has a type (Hipertrophy, Strength, Peaking) and duration
- Contains multiple training weeks

### 2. Training Weeks
- Represent weeks within a program
- Have a sequential `week_number` (1, 2, 3...)
- Contain multiple training sessions

### 3. Training Sessions  
- Individual workouts within a week
- Have a `day_of_week` (0=Monday, 6=Sunday)
- Have a `session_order` for chronological ordering
- Can be started/finished for logging
- Contain programmed exercises

### 4. Programmed Exercises
- Specific exercises planned for a session
- Reference a StandardExercise (exercise database)
- Have ordering within session (`exercise_order`)
- Grouped by block type (MAIN/ACCESSORY)
- Contain exercise parameters (sets, reps, RPE, etc.)

### 5. Exercise Logs
- **StrengthLog**: Records for strength exercises (weight, reps, RPE)
- **CardioLog**: Records for cardio exercises (duration, distance, heart rate)

## 🔥 Critical PUT Operation Behavior

The `PUT /programs/{program_id}` endpoint implements a **holistic replacement** strategy that is crucial for frontend integration:

### ID-Based Operation Logic

#### 1. **Updates (Has ID)**
When an object in the request has an `id` field:
- The system will **UPDATE** the existing object with that ID
- All fields are replaced with new values
- The object maintains its position/order based on array position

#### 2. **Creations (No ID)**  
When an object in the request has no `id` field (or `id: null`):
- The system will **CREATE** a new object
- A new ID is generated and assigned
- Position is determined by array index

#### 3. **Deletions (Missing from Array)**
When an existing object is **not present** in the request array:
- The system will **DELETE** that object from the database
- This includes all related child objects (cascade delete)

### ⚠️ Array Position = Order Priority

**CRITICAL**: The position of items in arrays determines their final order, regardless of existing order values:

```json
{
  "training_weeks": [
    {"id": 2, "week_number": 1},  // Will become week 1 (position 0)
    {"id": 1, "week_number": 3},  // Will become week 2 (position 1) 
    {"week_number": 5}            // Will become week 3 (position 2, new week)
  ]
}
```

### Ordering Fields Auto-Calculation

The system automatically calculates ordering fields based on array positions:

- **`week_number`**: Based on position in `training_weeks` array (1, 2, 3...)
- **`session_order`**: Based on chronological position (sorted by `day_of_week`, then array position)
- **`exercise_order`**: Based on position in `programmed_exercises` array (0, 1, 2...)

### Session Ordering Logic

Sessions are ordered chronologically by `day_of_week`, then by array position for same-day sessions:

```json
{
  "training_sessions": [
    {"day_of_week": 1, "name": "Session A"},  // Monday, session_order: 0
    {"day_of_week": 1, "name": "Session B"},  // Monday, session_order: 1  
    {"day_of_week": 3, "name": "Session C"},  // Wednesday, session_order: 2
    {"day_of_week": 5, "name": "Session D"}   // Friday, session_order: 3
  ]
}
```

### Example PUT Request

```json
{
  "name": "Updated Program",
  "description": "Modified program",
  "program_type": "STRENGTH",
  "duration_weeks": 8,
  "is_ai_generated": false,
  "training_weeks": [
    {
      "id": 1,                    // UPDATE existing week
      "week_number": 1,           // Will be recalculated to 1 (position 0)
      "description": "Updated week 1",
      "training_sessions": [
        {
          "id": 2,                // UPDATE existing session
          "name": "Upper Body",
          "day_of_week": 1,
          "description": "Chest and back",
          "programmed_exercises": [
            {
              "id": 5,            // UPDATE existing exercise
              "standard_exercise_id": 1,
              "block": "MAIN",
              "sets": 4,
              "reps": 8,
              "rpe_target": 8.0
            },
            {
              // NEW exercise (no id)
              "standard_exercise_id": 15,
              "block": "ACCESSORY", 
              "sets": 3,
              "reps": 12
            }
            // Note: Any existing exercises not in this array will be DELETED
          ]
        }
        // Note: Any existing sessions not in this array will be DELETED
      ]
    },
    {
      // NEW week (no id)
      "week_number": 2,           // Will be recalculated to 2 (position 1)
      "description": "New week",
      "training_sessions": [...]
    }
    // Note: Any existing weeks not in this array will be DELETED
  ]
}
```

## Endpoints

### Programs

#### GET /programs
Returns list of user's training programs (simplified view).

**Response:**
```json
[
  {
    "id": 1,
    "name": "Beginner Strength",
    "description": "4-week beginner program",
    "program_type": "STRENGTH",
    "duration_weeks": 4,
    "is_ai_generated": false,
    "user_id": 123,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /programs/{program_id}
Returns complete program structure with all nested data.

**Response:**
```json
{
  "id": 1,
  "name": "Beginner Strength",
  "description": "4-week beginner program",
  "program_type": "STRENGTH", 
  "duration_weeks": 4,
  "is_ai_generated": false,
  "user_id": 123,
  "training_weeks": [
    {
      "id": 1,
      "program_id": 1,
      "week_number": 1,
      "description": "Week 1 - Foundation",
      "training_sessions": [
        {
          "id": 1,
          "week_id": 1,
          "name": "Upper Body",
          "day_of_week": 1,
          "session_order": 0,
          "session_status": "NOT_STARTED",
          "description": "Chest and back focus",
          "programmed_exercises": [
            {
              "id": 1,
              "session_id": 1,
              "standard_exercise_id": 1,
              "exercise_name": "Bench Press",
              "block": "MAIN",
              "exercise_order": 0,
              "sets": 3,
              "reps": 10,
              "load_type": "PERCENTAGE_1RM",
              "percentage_1rm": 75.0,
              "rpe_target": 7.5,
              "rest_seconds": 180,
              "tempo": "2010",
              "sets_type": "WORKING",
              "notes": "Focus on form",
              "created_at": "2024-01-01T00:00:00Z",
              "updated_at": "2024-01-01T00:00:00Z"
            }
          ],
          "created_at": "2024-01-01T00:00:00Z",
          "updated_at": "2024-01-01T00:00:00Z"
        }
      ],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### GET /programs/{program_id}/summary
Returns program summary with statistics.

**Response:**
```json
{
  "id": 1,
  "name": "Beginner Strength",
  "description": "4-week beginner program",
  "program_type": "STRENGTH",
  "duration_weeks": 4,
  "is_ai_generated": false,
  "user_id": 123,
  "total_weeks": 4,
  "total_sessions": 12,
  "total_exercises": 48,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### POST /programs
Creates a new training program with complete structure.

**Request Body:**
```json
{
  "name": "New Program",
  "description": "Program description",
  "program_type": "STRENGTH",
  "duration_weeks": 4,
  "is_ai_generated": false,
  "training_weeks": [
    {
      "week_number": 1,
      "description": "Week 1",
      "training_sessions": [
        {
          "name": "Upper Body",
          "day_of_week": 1,
          "description": "Chest and back",
          "programmed_exercises": [
            {
              "standard_exercise_id": 1,
              "block": "MAIN",
              "sets": 3,
              "reps": 10,
              "load_type": "PERCENTAGE_1RM",
              "percentage_1rm": 75.0,
              "rpe_target": 7.5,
              "rest_seconds": 180
            }
          ]
        }
      ]
    }
  ]
}
```

#### PATCH /programs/{program_id}
Updates basic program information only (not structure).

#### PUT /programs/{program_id} 🔥
**THE MOST IMPORTANT ENDPOINT** - Replaces entire program structure.

**Key Behaviors:**
- Objects with IDs are updated
- Objects without IDs are created  
- Objects missing from arrays are deleted
- Array position determines final ordering
- Maintains referential integrity

**Request:** Same structure as GET response, but with optional IDs for update/create logic.

#### DELETE /programs/{program_id}
Deletes program and all related data (cascade delete).

### Weeks

#### GET /programs/{program_id}/weeks
Returns list of weeks for a program (simplified view).

#### GET /programs/{program_id}/weeks/{week_id}
Returns week details with optional sessions (`?include_sessions=true`).

#### POST /programs/{program_id}/weeks
Creates a new week in a program.

### Sessions

#### GET /programs/{program_id}/weeks/{week_id}/sessions
Returns list of sessions for a week.

#### GET /programs/{program_id}/weeks/{week_id}/sessions/{session_id}
Returns session details with optional exercises (`?include_exercises=true`).

#### POST /programs/{program_id}/weeks/{week_id}/sessions
Creates a new session in a week.

#### POST /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/start
Starts a session for exercise logging.

**Response:**
```json
{
  "message": "Training session started successfully",
  "session": {
    "id": 1,
    "name": "Upper Body",
    "week_id": 1,
    "day_of_week": 1,
    "session_status": "ACTIVE",
    "start_time": "2024-01-01T10:00:00Z"
  }
}
```

#### POST /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/finish
Finishes an active session.

**Request Body (Optional):**
```json
{
  "duration_seconds": 3600  // Optional: frontend-calculated duration
}
```

**Response:**
```json
{
  "message": "Training session finished successfully", 
  "session": {
    "id": 1,
    "name": "Upper Body",
    "duration_seconds": 3600,
    "completion_percentage": 85.5,
    "end_time": "2024-01-01T11:00:00Z"
  }
}
```

#### GET /active-session
Returns the user's currently active session, if any.

### Exercises

#### GET /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises
Returns exercises grouped by block type.

**Response:**
```json
{
  "main": [
    {
      "id": 1,
      "exercise_name": "Bench Press",
      "block": "MAIN",
      "exercise_order": 0,
      "sets": 3,
      "reps": 10,
      // ... other exercise fields
    }
  ],
  "accessory": [
    {
      "id": 2, 
      "exercise_name": "Tricep Pushdowns",
      "block": "ACCESSORY",
      "exercise_order": 1,
      "sets": 3,
      "reps": 15,
      // ... other exercise fields
    }
  ]
}
```

### Exercise Logs

#### GET /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/logs
Returns all logs for a session, grouped by exercise.

**Response:**
```json
[
  {
    "exercise_name": "Bench Press",
    "exercise_type": "STRENGTH",
    "programmed_exercise_id": 1,
    "logs": [
      {
        "id": 1,
        "set_number": 1,
        "repetitions_done": 10,
        "used_weight": 80.0,
        "used_weight_unit": "KG",
        "perceived_rpe": 7.0,
        "exercise_date": "2024-01-01T10:15:00Z"
      }
    ]
  }
]
```

#### GET /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs
Returns logs for a specific exercise in a session.

#### POST /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/strength
Creates a strength exercise log.

**Request Body:**
```json
{
  "set_number": 1,
  "set_type": "WORKING",
  "repetitions_done": 10,
  "used_weight": 80.0,
  "used_weight_unit": "KG", 
  "perceived_rpe": 7.0,
  "tempo": "2010",
  "rest_time_seconds": 180,
  "notes": "Felt strong today"
}
```

#### POST /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/cardio
Creates a cardio exercise log.

**Request Body:**
```json
{
  "exercise_name": "Treadmill Run",
  "cardio_type": "RUNNING",
  "total_duration_seconds": 1800,
  "distance": 5.0,
  "distance_unit": "KM",
  "calories_burned": 400,
  "avg_heart_rate": 150,
  "avg_rpe": 6.5,
  "intensity_level": "MODERATE",
  "notes": "Good pace today"
}
```

#### PUT /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/strength/{log_id}
Updates an existing strength log.

#### PUT /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/cardio/{log_id}
Updates an existing cardio log.

#### DELETE /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/strength/{log_id}
Deletes a strength log.

#### DELETE /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises/{exercise_id}/logs/cardio/{log_id}
Deletes a cardio log.

## Data Types & Enums

### ProgramType
- `STRENGTH`: Strength training focus
- `CARDIO`: Cardiovascular training focus  
- `HYBRID`: Mixed strength and cardio

### BlockType
- `MAIN`: Primary/compound exercises
- `ACCESSORY`: Secondary/isolation exercises

### LoadType
- `PERCENTAGE_1RM`: Load based on % of 1-rep max
- `RPE`: Load based on Rate of Perceived Exertion
- `WEIGHT_RANGE`: Load within a weight range
- `BODYWEIGHT`: Bodyweight exercises

### SetType
- `WORKING`: Main working sets
- `WARMUP`: Warm-up sets
- `DROPSET`: Drop sets
- `CLUSTER`: Cluster sets
- `REST_PAUSE`: Rest-pause sets

### SessionStatus
- `NOT_STARTED`: Session not yet started
- `ACTIVE`: Session currently in progress
- `COMPLETED`: Session finished successfully
- `ABANDONED`: Session started but not completed

## Frontend Integration Guidelines

### 1. Program Management
- Use `GET /programs` for program listing
- Use `GET /programs/{id}` for editing (gets complete structure)
- Use `PUT /programs/{id}` for saving changes (sends complete structure)
- Remember: Array position = final order

### 2. Session Flow
1. `GET /programs/{id}/weeks/{week_id}/sessions/{session_id}?include_exercises=true`
2. `POST .../sessions/{session_id}/start` 
3. Create logs during workout
4. `POST .../sessions/{session_id}/finish`

### 3. Exercise Ordering
- Send exercises in desired order within the array
- `exercise_order` will be auto-calculated (0, 1, 2...)
- Group by `block` type for display (MAIN, ACCESSORY)

### 4. Week/Session Ordering
- Send weeks in desired order (positions become week_number)
- Sessions are auto-ordered by `day_of_week`, then array position
- `session_order` is auto-calculated for chronological flow

### 5. Error Handling
- Check response status codes
- Handle validation errors (400) for missing required fields
- Handle not found errors (404) for invalid IDs
- Handle access denied errors (403) for unauthorized operations

### 6. Active Session Monitoring
- Check `GET /active-session` on app startup
- Only one session can be active per user
- Must finish/abandon before starting new session

## Common Patterns

### Creating a Complete Program
```javascript
// 1. Create with complete nested structure
const program = await fetch('/api/training/programs', {
  method: 'POST',
  body: JSON.stringify({
    name: "My Program",
    program_type: "STRENGTH",
    duration_weeks: 4,
    training_weeks: [
      {
        week_number: 1,
        training_sessions: [
          {
            name: "Day 1",
            day_of_week: 1,
            programmed_exercises: [...]
          }
        ]
      }
    ]
  })
});
```

### Updating Program Structure
```javascript
// 1. Get current program
const program = await fetch(`/api/training/programs/${programId}`);

// 2. Modify structure (add/remove/reorder)
program.training_weeks[0].training_sessions.push(newSession);

// 3. Save complete structure
await fetch(`/api/training/programs/${programId}`, {
  method: 'PUT', 
  body: JSON.stringify(program)
});
```

### Starting a Workout
```javascript
// 1. Start session
await fetch(`/api/training/programs/${programId}/weeks/${weekId}/sessions/${sessionId}/start`, {
  method: 'POST'
});

// 2. Log exercises during workout
await fetch(`/api/training/programs/${programId}/weeks/${weekId}/sessions/${sessionId}/exercises/${exerciseId}/logs/strength`, {
  method: 'POST',
  body: JSON.stringify({
    set_number: 1,
    repetitions_done: 10,
    used_weight: 80,
    used_weight_unit: "KG",
    perceived_rpe: 7
  })
});

// 3. Finish session
await fetch(`/api/training/programs/${programId}/weeks/${weekId}/sessions/${sessionId}/finish`, {
  method: 'POST',
  body: JSON.stringify({
    duration_seconds: 3600
  })
});
```

## Important Notes

1. **Session Access Control**: Only active sessions can accept new logs
2. **Cascade Deletes**: Deleting a program/week/session deletes all children
3. **Auto-Ordering**: Order fields are auto-calculated from array positions
4. **ID Preservation**: Existing IDs are preserved during updates
5. **Referential Integrity**: All foreign key relationships are maintained
6. **User Isolation**: Users can only access their own data
7. **Validation**: Required fields enforced, data types validated
8. **Timestamps**: `created_at`/`updated_at` automatically managed

This documentation provides the complete picture of how the Training API works, with special emphasis on the critical PUT operation behavior that frontend developers need to understand for proper integration.
