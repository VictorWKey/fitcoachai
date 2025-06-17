# FitCoach AI - API Documentation

This document provides detailed information about the FitCoach AI backend API endpoints, including request/response formats and authentication requirements. This documentation is intended for frontend developers implementing the React Native Expo mobile application.

## Table of Contents

1. [Authentication](#authentication)
2. [Chat](#chat)
3. [Workouts](#workouts)
4. [Exercises](#exercises)

## Base URL

All API endpoints are relative to the base URL of your backend server.

## Authentication

Authentication is handled using JWT (JSON Web Tokens). Most endpoints require authentication using a Bearer token in the Authorization header.

### Authentication Flow

1. Register a user account
2. Verify email using the verification link
3. Login to obtain access and refresh tokens
4. Use the access token for authenticated requests
5. Use the refresh token to obtain new tokens when the access token expires

### Endpoints

#### Register

```
POST /auth/register
```

Creates a new user account and sends a verification email.

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "StrongP@ssw0rd"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "string",
  "email": "user@example.com",
  "full_name": null,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00.000000",
  "updated_at": null
}
```

**Notes:**
- Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character.
- If an unverified account with the same email exists, it will be updated.
- If an unverified account with the same username exists, it will be deleted.

#### Login

```
POST /auth/login
```

Authenticates a user and returns access and refresh tokens.

**Request Body (Form Data):**
```
username: "string" (can be username or email)
password: "string"
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

**Notes:**
- Store both tokens securely in the frontend.
- The access token should be sent in the Authorization header for authenticated requests.

#### Refresh Token

```
POST /auth/refresh
```

Refreshes access and refresh tokens using a valid refresh token.

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

#### Logout

```
POST /auth/logout
```

Logs the user out by revoking the current access and refresh tokens.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh_token": "string"
}
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

#### Verify Email

```
GET /auth/verify-email?token=verification_token
POST /auth/verify-email
```

Verifies a user's email using a verification token.

**Query Parameters or Request Body:**
```
token: "string"
```

**Response:**
```json
{
  "message": "Email verificado correctamente"
}
```

#### Resend Verification Email

```
POST /auth/resend-verification
```

Resends a verification email to an unverified user.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Se ha enviado un nuevo correo de verificación. Por favor revisa tu bandeja de entrada."
}
```

#### Forgot Password

```
POST /auth/forgot-password
```

Sends a password reset email to the user.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Si tu cuenta existe, recibirás un email con instrucciones para restablecer tu contraseña"
}
```

#### Verify Reset Token

```
GET /auth/reset-password/verify?token=reset_token
```

Verifies that a password reset token is valid and not expired.

**Query Parameters:**
```
token: "string"
```

**Response:**
```json
{
  "valid": true,
  "user_email": "use***@example.com"
}
```

#### Reset Password

```
POST /auth/reset-password
```

Resets the user's password using a valid reset token.

**Request Body:**
```json
{
  "token": "string",
  "new_password": "NewStrongP@ssw0rd",
  "confirm_password": "NewStrongP@ssw0rd"
}
```

**Response:**
```json
{
  "message": "Contraseña actualizada correctamente"
}
```

## Chat

The chat endpoints allow interaction with the AI fitness coach.

### Endpoints

#### Send Message

```
POST /chat/
```

Sends a message to the AI coach and gets a response.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "input": "string"
}
```

**Response:**
```json
{
  "id": 123,
  "role": "assistant",
  "content": "string",
  "created_at": "2023-01-01T00:00:00.000000"
}
```

**Notes:**
- Both the user's message and the assistant's response are stored in the database.
- The response includes the ID of the assistant's message, which can be used for fetching history.

#### Get Chat History

```
GET /chat/history?after_id=0&limit=50
```

Retrieves the user's chat history with the AI coach.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
after_id: integer (optional, default: 0)
limit: integer (optional, default: 50, max: 100)
```

**Response:**
```json
[
  {
    "id": 123,
    "role": "user",
    "content": "string",
    "created_at": "2023-01-01T00:00:00.000000"
  },
  {
    "id": 124,
    "role": "assistant",
    "content": "string",
    "created_at": "2023-01-01T00:00:00.000000"
  }
]
```

**Notes:**
- If `after_id` is 0, returns the most recent messages up to the limit.
- If `after_id` is > 0, returns messages with ID greater than `after_id` up to the limit.
- Messages are returned in chronological order.

## Workouts

The workout endpoints allow managing user workouts and exercise logs.

### Endpoints

#### List Workouts

```
GET /workouts/?skip=0&limit=50
```

Gets all workouts for the current user.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
skip: integer (optional, default: 0)
limit: integer (optional, default: 50, max: 100)
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "muscle_group": "chest",
    "category": "hypertrophy",
    "is_finished": true,
    "start_time": "2023-01-01T00:00:00.000000",
    "created_at": "2023-01-01T00:00:00.000000",
    "updated_at": null
  }
]
```

#### Get Active Workout

```
GET /workouts/active
```

Gets the user's active (most recent unfinished) workout.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "muscle_group": "chest",
  "category": "hypertrophy",
  "is_finished": false,
  "start_time": "2023-01-01T00:00:00.000000",
  "created_at": "2023-01-01T00:00:00.000000",
  "updated_at": null
}
```

**Notes:**
- Returns `null` if no active workout is found.

#### Get Workout by ID

```
GET /workouts/{workout_id}
```

Gets a specific workout by ID.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "muscle_group": "chest",
  "category": "hypertrophy",
  "is_finished": true,
  "start_time": "2023-01-01T00:00:00.000000",
  "created_at": "2023-01-01T00:00:00.000000",
  "updated_at": null
}
```

#### Create Workout

```
POST /workouts/
```

Creates a new workout.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "muscle_group": "chest",
  "category": "hypertrophy",
  "start_time": "2023-01-01T00:00:00.000000"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "muscle_group": "chest",
  "category": "hypertrophy",
  "is_finished": false,
  "start_time": "2023-01-01T00:00:00.000000",
  "created_at": "2023-01-01T00:00:00.000000",
  "updated_at": null
}
```

**Notes:**
- `start_time` is optional. If not provided, the current time will be used.
- `user_id` is automatically set to the authenticated user's ID.

#### Update Workout

```
PUT /workouts/{workout_id}
```

Updates a workout.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
```

**Request Body:**
```json
{
  "muscle_group": "back",
  "category": "strength",
  "is_finished": true,
  "start_time": "2023-01-01T00:00:00.000000"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "muscle_group": "back",
  "category": "strength",
  "is_finished": true,
  "start_time": "2023-01-01T00:00:00.000000",
  "created_at": "2023-01-01T00:00:00.000000",
  "updated_at": "2023-01-01T01:00:00.000000"
}
```

**Notes:**
- All fields in the request body are optional.

#### Delete Workout

```
DELETE /workouts/{workout_id}
```

Deletes a workout.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
```

**Response:**
- Status: 204 No Content

#### Finish Workout

```
POST /workouts/{workout_id}/finish
```

Finishes a workout and infers its type using the AI.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "muscle_group": "chest",
  "category": "hypertrophy",
  "is_finished": true,
  "start_time": "2023-01-01T00:00:00.000000",
  "created_at": "2023-01-01T00:00:00.000000",
  "updated_at": "2023-01-01T01:00:00.000000"
}
```

**Notes:**
- The AI will analyze the exercises performed and update the `muscle_group` and `category` fields if necessary.

#### List Workout Exercises

```
GET /workouts/{workout_id}/exercises
```

Gets all exercise logs for a specific workout.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
```

**Response:**
```json
[
  {
    "id": 1,
    "workout_id": 1,
    "exercise_name": "Bench Press",
    "set_number": 1,
    "reps": 10,
    "weight": 100,
    "weight_unit": "kg",
    "rir": 2,
    "notes": "Felt strong today",
    "exercise_date": "2023-01-01T00:00:00.000000",
    "updated_at": "2023-01-01T00:00:00.000000"
  }
]
```

#### Create Exercise Log

```
POST /workouts/{workout_id}/exercises
```

Adds a new exercise log to a workout.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
```

**Request Body:**
```json
{
  "exercise_name": "Bench Press",
  "set_number": 1,
  "reps": 10,
  "weight": 100,
  "weight_unit": "kg",
  "rir": 2,
  "notes": "Felt strong today"
}
```

**Response:**
```json
{
  "id": 1,
  "workout_id": 1,
  "exercise_name": "Bench Press",
  "set_number": 1,
  "reps": 10,
  "weight": 100,
  "weight_unit": "kg",
  "rir": 2,
  "notes": "Felt strong today",
  "exercise_date": "2023-01-01T00:00:00.000000",
  "updated_at": "2023-01-01T00:00:00.000000"
}
```

**Notes:**
- All fields except `workout_id` and `user_id` (which are set automatically) are optional.
- `weight_unit` must be one of the values defined in the `WeightUnit` enum (e.g., "kg", "lbs").

#### Get Exercise Log

```
GET /workouts/{workout_id}/exercises/{exercise_id}
```

Gets a specific exercise log by ID.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
exercise_id: integer
```

**Response:**
```json
{
  "id": 1,
  "workout_id": 1,
  "exercise_name": "Bench Press",
  "set_number": 1,
  "reps": 10,
  "weight": 100,
  "weight_unit": "kg",
  "rir": 2,
  "notes": "Felt strong today",
  "exercise_date": "2023-01-01T00:00:00.000000",
  "updated_at": "2023-01-01T00:00:00.000000"
}
```

#### Update Exercise Log

```
PUT /workouts/{workout_id}/exercises/{exercise_id}
```

Updates a specific exercise log.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
exercise_id: integer
```

**Request Body:**
```json
{
  "exercise_name": "Incline Bench Press",
  "set_number": 1,
  "reps": 8,
  "weight": 90,
  "weight_unit": "kg",
  "rir": 1,
  "notes": "Increased difficulty with incline"
}
```

**Response:**
```json
{
  "id": 1,
  "workout_id": 1,
  "exercise_name": "Incline Bench Press",
  "set_number": 1,
  "reps": 8,
  "weight": 90,
  "weight_unit": "kg",
  "rir": 1,
  "notes": "Increased difficulty with incline",
  "exercise_date": "2023-01-01T00:00:00.000000",
  "updated_at": "2023-01-01T01:00:00.000000"
}
```

**Notes:**
- All fields in the request body are optional.

#### Delete Exercise Log

```
DELETE /workouts/{workout_id}/exercises/{exercise_id}
```

Deletes a specific exercise log.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
workout_id: integer
exercise_id: integer
```

**Response:**
- Status: 204 No Content

## Exercises

The exercises endpoints provide additional functionality for analyzing and retrieving exercise data across workouts.

### Endpoints

#### Get Recent Exercises

```
GET /exercises/recent?limit=10
```

Gets the user's most recent exercises across all workouts.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
limit: integer (optional, default: 10, max: 50)
```

**Response:**
```json
[
  {
    "id": 1,
    "workout_id": 1,
    "exercise_name": "Bench Press",
    "set_number": 1,
    "reps": 10,
    "weight": 100,
    "weight_unit": "kg",
    "rir": 2,
    "notes": "Felt strong today",
    "exercise_date": "2023-01-01T00:00:00.000000",
    "updated_at": "2023-01-01T00:00:00.000000"
  }
]
```

#### Get Popular Exercises

```
GET /exercises/popular?limit=10
```

Gets the user's most frequently performed exercises.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
limit: integer (optional, default: 10, max: 50)
```

**Response:**
```json
[
  {
    "name": "Bench Press",
    "count": 15
  },
  {
    "name": "Squat",
    "count": 12
  }
]
```

#### Get Exercise Stats

```
GET /exercises/stats?days=30
```

Gets exercise statistics for the current user.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
days: integer (optional, default: 30, max: 365)
```

**Response:**
```json
{
  "total_exercises": 120,
  "total_workouts": 15,
  "avg_exercises_per_workout": 8.0,
  "top_muscle_groups": [
    {
      "muscle_group": "chest",
      "count": 5
    },
    {
      "muscle_group": "back",
      "count": 4
    }
  ],
  "period_days": 30
}
```

#### Search Exercises

```
GET /exercises/search?query=bench&limit=20
```

Searches for exercises by name.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
```
query: string (required, min length: 2)
limit: integer (optional, default: 20, max: 100)
```

**Response:**
```json
[
  {
    "id": 1,
    "workout_id": 1,
    "exercise_name": "Bench Press",
    "set_number": 1,
    "reps": 10,
    "weight": 100,
    "weight_unit": "kg",
    "rir": 2,
    "notes": "Felt strong today",
    "exercise_date": "2023-01-01T00:00:00.000000",
    "updated_at": "2023-01-01T00:00:00.000000"
  }
]
```

#### Get Exercise Progress

```
GET /exercises/progress/{exercise_name}?days=90
```

Gets progress data for a specific exercise over time.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
```
exercise_name: string
```

**Query Parameters:**
```
days: integer (optional, default: 90, max: 365)
```

**Response:**
```json
[
  {
    "date": "2023-01-01T00:00:00.000000",
    "reps": 10,
    "weight": 100,
    "weight_unit": "kg",
    "rir": 2,
    "set_number": 1
  },
  {
    "date": "2023-01-08T00:00:00.000000",
    "reps": 10,
    "weight": 105,
    "weight_unit": "kg",
    "rir": 2,
    "set_number": 1
  }
]
```

#### Get Exercise Catalog

```
GET /exercises/catalog
```

Gets a catalog of all unique exercises performed by the user, categorized by muscle group.

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "chest": [
    "Bench Press",
    "Incline Bench Press",
    "Chest Fly"
  ],
  "back": [
    "Pull Up",
    "Barbell Row",
    "Lat Pulldown"
  ]
}
```

## Enums

### MuscleGroup

The following values are valid for the `muscle_group` field:

- `chest`: Exercises primarily for chest (bench press, flyes, etc.)
- `back`: Exercises primarily for back (pull-ups, rows, pull-downs, etc.)
- `legs_in_general`: Exercises for legs without specific emphasis
- `legs_cuadriceps_enphasis`: Exercises for legs with emphasis on quadriceps (squats, leg press, etc.)
- `legs_hamstrings_enphasis`: Exercises for legs with emphasis on hamstrings (deadlifts, leg curls, etc.)
- `shoulders`: Exercises for shoulders (military press, lateral raises, etc.)
- `arms`: Exercises for arms in general
- `only_triceps`: Exercises specifically for triceps
- `only_biceps`: Exercises specifically for biceps
- `abs`: Exercises for abdominals
- `core`: Exercises for the core (abs, obliques, lower back)
- `full_body`: Full body workout
- `cardio`: Cardiovascular exercises

### Category

The following values are valid for the `category` field:

- `strength`: Strength training (typically 1-5 reps with high weight)
- `hypertrophy`: Hypertrophy or muscle growth (typically 6-12 reps with moderate weight)
- `endurance`: Muscular endurance (typically more than 12 reps with low weight)
- `balance`: Balance exercises
- `flexibility`: Flexibility or stretching exercises
- `coordination`: Exercises emphasizing coordination
- `power`: Power exercises (explosive movements)

### WeightUnit

The following values are valid for the `weight_unit` field:

- `kg`: Kilograms
- `lbs`: Pounds

## Error Handling

All endpoints may return the following error responses:

- 400 Bad Request: Invalid input data
- 401 Unauthorized: Missing or invalid authentication
- 403 Forbidden: Insufficient permissions (e.g., unverified email)
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server-side error

Error responses have the following format:

```json
{
  "detail": "Error message"
}
```

## Authentication Headers

For all authenticated endpoints, include the following header:

```
Authorization: Bearer <access_token>
```

Where `<access_token>` is the JWT token obtained from the login or refresh token endpoints. 