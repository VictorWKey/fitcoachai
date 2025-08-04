# Sessions API Documentation

## Descripción General

La API de Sessions maneja todo lo relacionado con el ciclo de vida de las sesiones de entrenamiento y el registro de ejercicios. Permite a los usuarios iniciar sesiones, registrar ejercicios de fuerza y cardio, y realizar seguimiento del progreso.

**Base URL**: `/sessions`

## Autenticación

Todos los endpoints requieren autenticación mediante JWT token en el header:
```
Authorization: Bearer <token>
```

---

## 🏃 Gestión de Sesiones de Entrenamiento

### POST `/sessions/start/{session_id}`

Inicia una sesión de entrenamiento para el logging de ejercicios.

**Parámetros de Ruta:**
- `session_id` (int, requerido): ID de la sesión a iniciar

**Respuesta Exitosa (200):**
```json
{
  "message": "Training session started successfully",
  "session": {
    "id": 123,
    "name": "Día 1 - Pecho y Tríceps",
    "week_id": 5,
    "day_of_week": 1,
    "is_active": true,
    "start_time": "2025-07-21T14:30:00.000Z"
  }
}
```

**Errores Posibles:**
- `400`: Ya hay una sesión activa
- `404`: Sesión no encontrada
- `500`: Error interno del servidor

---

### POST `/sessions/finish`

Finaliza la sesión de entrenamiento actualmente activa.

**Parámetros de Query (Opcionales):**
- `session_id` (int): ID específico de sesión a finalizar

**Respuesta Exitosa (200):**
```json
{
  "message": "Training session finished successfully",
  "session": {
    "id": 123,
    "name": "Día 1 - Pecho y Tríceps",
    "duration_seconds": 4500,
    "completion_percentage": 85,
    "end_time": "2025-07-21T15:45:00.000Z"
  }
}
```

**Errores Posibles:**
- `404`: No hay sesión activa o sesión no encontrada
- `500`: Error interno del servidor

---

### GET `/sessions/active`

Obtiene la sesión de entrenamiento actualmente activa del usuario.

**Respuesta Exitosa (200):**
```json
{
  "active_session": {
    "id": 123,
    "name": "Día 1 - Pecho y Tríceps",
    "week_id": 5,
    "day_of_week": 1,
    "start_time": "2025-07-21T14:30:00.000Z",
    "completion_percentage": 45,
    "strength_logs_count": 8,
    "cardio_logs_count": 1
  }
}
```

**Respuesta Sin Sesión Activa (200):**
```json
{
  "active_session": null
}
```

---

### GET `/sessions/history`

Obtiene el historial de sesiones de entrenamiento del usuario.

**Parámetros de Query:**
- `limit` (int, opcional): Máximo de registros a retornar (1-50, por defecto: 10)
- `offset` (int, opcional): Número de registros a saltar (por defecto: 0)

**Respuesta Exitosa (200):**
```json
{
  "sessions": [
    {
      "id": 122,
      "name": "Día 3 - Piernas",
      "week_id": 4,
      "day_of_week": 5,
      "start_time": "2025-07-19T09:00:00.000Z",
      "end_time": "2025-07-19T10:30:00.000Z",
      "duration_seconds": 5400,
      "completion_percentage": 100,
      "strength_logs_count": 12,
      "cardio_logs_count": 0
    },
    {
      "id": 121,
      "name": "Día 2 - Espalda y Bíceps",
      "week_id": 4,
      "day_of_week": 3,
      "start_time": "2025-07-17T16:00:00.000Z",
      "end_time": "2025-07-17T17:15:00.000Z",
      "duration_seconds": 4500,
      "completion_percentage": 90,
      "strength_logs_count": 10,
      "cardio_logs_count": 1
    }
  ],
  "total": 2,
  "limit": 10,
  "offset": 0
}
```

---

### GET `/sessions/{session_id}`

Obtiene información detallada de una sesión específica con todos sus ejercicios registrados.

**Parámetros de Ruta:**
- `session_id` (int, requerido): ID de la sesión

**Respuesta Exitosa (200):**
```json
{
  "session": {
    "id": 123,
    "name": "Día 1 - Pecho y Tríceps",
    "week_id": 5,
    "day_of_week": 1,
    "start_time": "2025-07-21T14:30:00.000Z",
    "end_time": "2025-07-21T15:45:00.000Z",
    "duration_seconds": 4500,
    "completion_percentage": 85,
    "is_active": false
  },
  "strength_logs": [
    {
      "id": 1001,
      "set_number": 1,
      "repetitions_done": 12,
      "used_weight": 80.0,
      "used_weight_unit": "kg",
      "perceived_rir": 3,
      "perceived_rpe": 7.5,
      "notes": "Buena técnica, peso adecuado",
      "exercise_date": "2025-07-21T14:35:00.000Z"
    }
  ],
  "cardio_logs": [
    {
      "id": 501,
      "exercise_name": "Cinta de correr",
      "total_duration_seconds": 600,
      "distance": 2.5,
      "distance_unit": "km",
      "calories_burned": 150,
      "notes": "Cardio post-entrenamiento",
      "exercise_date": "2025-07-21T15:40:00.000Z"
    }
  ]
}
```

**Errores Posibles:**
- `403`: Acceso denegado a esta sesión
- `404`: Sesión no encontrada
- `500`: Error interno del servidor

---

## 📊 Progreso de Ejercicios

### GET `/sessions/logs/exercise/{standard_exercise_id}/progress`

Obtiene el progreso de un ejercicio específico en la sesión activa actual.

**Parámetros de Ruta:**
- `standard_exercise_id` (int, requerido): ID del ejercicio estándar

**Respuesta Exitosa (200):**
```json
{
  "exercise_id": 25,
  "programmed_sets": 4,
  "completed_sets": 2,
  "remaining_sets": 2,
  "next_set_number": 3,
  "is_complete": false,
  "existing_logs": [
    {
      "set_number": 1,
      "reps": 12,
      "weight": 80.0,
      "rpe": 7.5,
      "rir": 3
    },
    {
      "set_number": 2,
      "reps": 10,
      "weight": 85.0,
      "rpe": 8.0,
      "rir": 2
    }
  ]
}
```

**Errores Posibles:**
- `400`: No hay sesión activa o ejercicio no programado
- `404`: Sesión no encontrada
- `500`: Error interno del servidor

---

## 💪 Registro de Ejercicios de Fuerza

### POST `/sessions/logs/strength`

Crea un nuevo registro de ejercicio de fuerza en la sesión activa.

**Cuerpo de la Petición (StrengthLogCreate):**
```json
{
  "standard_exercise_id": 25,
  "set_number": 1,
  "repetitions_done": 12,
  "used_weight": 80.0,
  "used_weight_unit": "kg",
  "perceived_rir": 3,
  "perceived_rpe": 7.5,
  "tempo": "3-1-1-0",
  "rest_time_seconds": 120,
  "notes": "Buena técnica, peso adecuado"
}
```

**Campos del StrengthLogCreate:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `standard_exercise_id` | int | ✅ | ID del ejercicio estándar |
| `set_number` | int | ✅ | Número de la serie (>0) |
| `repetitions_done` | int | ✅ | Repeticiones realizadas (1-50) |
| `used_weight` | float | ✅ | Peso utilizado (≥0) |
| `used_weight_unit` | string | ✅ | Unidad: `"kg"` o `"lb"` |
| `perceived_rir` | int | ❌ | Repeticiones en reserva (0-10) |
| `perceived_rpe` | float | ❌ | Escala de esfuerzo percibido (1.0-10.0) |
| `tempo` | string | ❌ | Formato "E-B-C-T" ej: "3-1-1-0" |
| `rest_time_seconds` | int | ❌ | Tiempo de descanso en segundos |
| `notes` | string | ❌ | Notas adicionales |

**Respuesta Exitosa (200):**
```json
{
  "message": "Strength exercise log created successfully",
  "log": {
    "id": 1001,
    "user_id": 1,
    "training_session_id": 123,
    "standard_exercise_id": 25,
    "programmed_exercise_id": 450,
    "set_number": 1,
    "repetitions_done": 12,
    "used_weight": 80.0,
    "used_weight_unit": "kg",
    "perceived_rir": 3,
    "perceived_rpe": 7.5,
    "tempo": "3-1-1-0",
    "rest_time_seconds": 120,
    "notes": "Buena técnica, peso adecuado",
    "exercise_date": "2025-07-21T14:35:00.000Z",
    "updated_at": "2025-07-21T14:35:00.000Z"
  },
  "programmed_sets": 4,
  "completed_sets": 1,
  "remaining_sets": 3
}
```

**Validaciones y Errores:**
- `400`: No hay sesión activa
- `400`: Ejercicio no programado en la sesión
- `400`: Número de serie inválido o duplicado
- `400`: Repeticiones fuera del rango válido
- `400`: RPE/RIR fuera del rango válido
- `400`: Peso negativo
- `500`: Error interno del servidor

---

### GET `/sessions/logs/strength/{log_id}`

Obtiene un registro específico de ejercicio de fuerza.

**Parámetros de Ruta:**
- `log_id` (int, requerido): ID del registro

**Respuesta Exitosa (200):**
```json
{
  "log": {
    "id": 1001,
    "user_id": 1,
    "training_session_id": 123,
    "standard_exercise_id": 25,
    "programmed_exercise_id": 450,
    "set_number": 1,
    "repetitions_done": 12,
    "used_weight": 80.0,
    "used_weight_unit": "kg",
    "perceived_rir": 3,
    "perceived_rpe": 7.5,
    "tempo": "3-1-1-0",
    "rest_time_seconds": 120,
    "notes": "Buena técnica, peso adecuado",
    "exercise_date": "2025-07-21T14:35:00.000Z",
    "updated_at": "2025-07-21T14:35:00.000Z"
  }
}
```

**Errores Posibles:**
- `403`: Acceso denegado al registro
- `404`: Registro no encontrado
- `500`: Error interno del servidor

---

### PUT `/sessions/logs/strength/{log_id}`

Actualiza un registro existente de ejercicio de fuerza.

**Parámetros de Ruta:**
- `log_id` (int, requerido): ID del registro

**Cuerpo de la Petición (StrengthLogUpdate - todos los campos opcionales):**
```json
{
  "repetitions_done": 10,
  "used_weight": 85.0,
  "perceived_rpe": 8.0,
  "notes": "Serie más pesada, buena ejecución"
}
```

**Respuesta Exitosa (200):**
```json
{
  "message": "Strength exercise log updated successfully",
  "log": {
    "id": 1001,
    "user_id": 1,
    "training_session_id": 123,
    "standard_exercise_id": 25,
    "programmed_exercise_id": 450,
    "set_number": 1,
    "repetitions_done": 10,
    "used_weight": 85.0,
    "used_weight_unit": "kg",
    "perceived_rir": 3,
    "perceived_rpe": 8.0,
    "tempo": "3-1-1-0",
    "rest_time_seconds": 120,
    "notes": "Serie más pesada, buena ejecución",
    "exercise_date": "2025-07-21T14:35:00.000Z",
    "updated_at": "2025-07-21T14:40:00.000Z"
  }
}
```

---

### DELETE `/sessions/logs/strength/{log_id}`

Elimina un registro de ejercicio de fuerza.

**Parámetros de Ruta:**
- `log_id` (int, requerido): ID del registro

**Respuesta Exitosa (200):**
```json
{
  "message": "Strength exercise log deleted successfully"
}
```

**Errores Posibles:**
- `403`: Acceso denegado al registro
- `404`: Registro no encontrado
- `500`: Error interno del servidor

---

## 🏃 Registro de Ejercicios de Cardio

### POST `/sessions/logs/cardio`

Crea un nuevo registro de ejercicio cardiovascular en la sesión activa.

**Cuerpo de la Petición (CardioLogCreate):**
```json
{
  "exercise_name": "Cinta de correr",
  "cardio_type": "steady_state",
  "total_duration_seconds": 1200,
  "distance": 3.5,
  "distance_unit": "km",
  "calories_burned": 200,
  "avg_heart_rate": 140,
  "avg_rpe": 6.0,
  "intensity_level": 8,
  "incline_level": 2,
  "notes": "Cardio post-entrenamiento, buen ritmo"
}
```

**Campos del CardioLogCreate:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `exercise_name` | string | ✅ | Nombre del ejercicio cardiovascular |
| `cardio_type` | string | ✅ | Tipo: `"hiit"` o `"steady_state"` |
| `total_duration_seconds` | int | ✅ | Duración total en segundos |
| `distance` | float | ❌ | Distancia recorrida |
| `distance_unit` | string | ❌ | Unidad: `"km"` o `"mi"` (por defecto: "km") |
| `calories_burned` | int | ❌ | Calorías quemadas |
| `avg_heart_rate` | int | ❌ | Frecuencia cardíaca promedio |
| `avg_rpe` | float | ❌ | RPE promedio (1.0-10.0) |
| `intensity_level` | int | ❌ | Nivel de intensidad (1-20) |
| `incline_level` | int | ❌ | Nivel de inclinación (0-15) |
| `notes` | string | ❌ | Notas adicionales |

**Respuesta Exitosa (200):**
```json
{
  "message": "Cardio exercise log created successfully",
  "log": {
    "id": 501,
    "user_id": 1,
    "training_session_id": 123,
    "exercise_name": "Cinta de correr",
    "cardio_type": "steady_state",
    "total_duration_seconds": 1200,
    "distance": 3.5,
    "distance_unit": "km",
    "calories_burned": 200,
    "avg_heart_rate": 140,
    "avg_rpe": 6.0,
    "intensity_level": 8,
    "incline_level": 2,
    "notes": "Cardio post-entrenamiento, buen ritmo",
    "exercise_date": "2025-07-21T15:40:00.000Z",
    "updated_at": "2025-07-21T15:40:00.000Z"
  }
}
```

**Errores Posibles:**
- `400`: No hay sesión activa
- `500`: Error interno del servidor

---

## 📋 Enumeraciones y Tipos de Datos

### WeightUnit (Unidades de Peso)
```typescript
type WeightUnit = "kg" | "lb"
```

### DistanceUnit (Unidades de Distancia)
```typescript
type DistanceUnit = "km" | "mi"
```

### CardioType (Tipos de Cardio)
```typescript
type CardioType = "hiit" | "steady_state"
```

### SetType (Tipos de Series)
```typescript
type SetType = "strength" | "hypertrophy" | "technique"
```

---

## 🔍 Ejemplos de Uso Completo

### Flujo Típico de Entrenamiento

1. **Iniciar sesión:**
```bash
POST /sessions/start/123
```

2. **Verificar sesión activa:**
```bash
GET /sessions/active
```

3. **Consultar progreso de ejercicio:**
```bash
GET /sessions/logs/exercise/25/progress
```

4. **Registrar serie de fuerza:**
```bash
POST /sessions/logs/strength
{
  "standard_exercise_id": 25,
  "set_number": 1,
  "repetitions_done": 12,
  "used_weight": 80.0,
  "used_weight_unit": "kg",
  "perceived_rpe": 7.5
}
```

5. **Registrar cardio:**
```bash
POST /sessions/logs/cardio
{
  "exercise_name": "Elíptica",
  "cardio_type": "steady_state",
  "total_duration_seconds": 900,
  "calories_burned": 150
}
```

6. **Finalizar sesión:**
```bash
POST /sessions/finish
```

---

## ⚠️ Notas Importantes

### Validaciones de Ejercicios de Fuerza:
- Solo se pueden registrar ejercicios programados en la sesión activa
- No se permiten series duplicadas para el mismo ejercicio
- El número de serie debe seguir la secuencia programada
- RPE debe estar entre 1-10, RIR entre 0-10
- Repeticiones entre 1-50 para evitar errores de entrada

### Gestión de Sesiones:
- Solo puede haber una sesión activa por usuario
- Los registros de ejercicios solo se pueden crear en sesiones activas
- El progreso se calcula automáticamente basado en ejercicios programados

### Seguridad:
- Todos los endpoints requieren autenticación
- Los usuarios solo pueden acceder a sus propios registros
- Las validaciones de permisos se aplican en cada operación
