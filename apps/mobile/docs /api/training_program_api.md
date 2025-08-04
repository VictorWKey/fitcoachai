# Training Program API Documentation

Esta documentación describe los endpoints de la API para gestionar programas de entrenamiento en FitCoach AI.

**Base URL:** `/api/training-programs`

## Autenticación

Todos los endpoints requieren autenticación mediante Bearer Token en el header:
```
Authorization: Bearer <your_jwt_token>
```

## Modelos de Datos

### Enums

#### ProgramType
```typescript
enum ProgramType {
  HYPERTROPHY = "hypertrophy",  // Programas enfocados en crecimiento muscular
  STRENGTH = "strength",        // Programas enfocados en desarrollo de fuerza
  PEAKING = "peaking"          // Programas enfocados en pico para competencia
}
```

#### BlockType
```typescript
enum BlockType {
  MAIN = "main",           // Ejercicios principales (ej: sentadilla, press banca)
  ACCESSORY = "accessory"  // Ejercicios accesorios (ej: leg press, flies)
}
```

#### LoadType
```typescript
enum LoadType {
  RPE = "rpe",           // Tasa de Esfuerzo Percibido
  PERCENTAGE = "percentage", // Porcentaje de 1RM
  WEIGHT = "weight"      // Peso absoluto
}
```

#### SetType
```typescript
enum SetType {
  STRENGTH = "strength",
  HIPERTROPHY = "hypertrophy",
  TECHNIQUE = "technique"
}
```

### Esquemas de Respuesta

#### TrainingProgramSimpleResponse
```typescript
interface TrainingProgramSimpleResponse {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  program_type: ProgramType;
  duration_weeks: number;
  is_ai_generated: boolean;
  created_at: string; // ISO 8601 datetime
  updated_at: string; // ISO 8601 datetime
}
```

#### ProgrammedExerciseResponse
```typescript
interface ProgrammedExerciseResponse {
  id: number;
  block_id: number;
  tempo?: string;
  sets?: number;
  reps?: number;
  load_type?: LoadType;
  load_value?: string;
  rpe_target?: number;
  percentage_1rm?: number;
  weight_range?: string;
  rest_seconds?: number;
  sets_type?: SetType;
  custom_parameters?: Record<string, any>;
  created_at: string;
  updated_at: string;
}
```

#### ExerciseBlockResponse
```typescript
interface ExerciseBlockResponse {
  id: number;
  session_id: number;
  name: string;
  block_type: BlockType;
  order: number;
  description?: string;
  programmed_exercises: ProgrammedExerciseResponse[];
  created_at: string;
  updated_at: string;
}
```

#### TrainingSessionResponse
```typescript
interface TrainingSessionResponse {
  id: number;
  week_id: number;
  name: string;
  day_of_week?: number; // 0 = Monday, 6 = Sunday
  session_order: number; // Orden secuencial dentro del programa (0,1,2,3...)
  description?: string;
  exercise_blocks: ExerciseBlockResponse[];
  created_at: string;
  updated_at: string;
}
```

#### TrainingWeekResponse
```typescript
interface TrainingWeekResponse {
  id: number;
  program_id: number;
  week_number: number;
  description?: string;
  training_sessions: TrainingSessionResponse[];
  created_at: string;
  updated_at: string;
}
```

#### TrainingProgramResponse
```typescript
interface TrainingProgramResponse {
  id: number;
  user_id: number;
  name: string;
  description?: string;
  program_type: ProgramType;
  duration_weeks: number;
  is_ai_generated: boolean;
  training_weeks: TrainingWeekResponse[];
  created_at: string;
  updated_at: string;
}
```

### Esquemas de Creación

#### ProgrammedExerciseCreate
```typescript
interface ProgrammedExerciseCreate {
  standard_exercise_id: number;
  tempo?: string;
  sets?: number;
  reps?: number;
  load_type?: LoadType;
  load_value?: string;
  rpe_target?: number;
  percentage_1rm?: number;
  weight_range?: string;
  rest_seconds?: number;
  sets_type?: SetType;
  custom_parameters?: Record<string, any>;
}
```

#### ExerciseBlockCreate
```typescript
interface ExerciseBlockCreate {
  name: string;
  block_type: BlockType;
  order: number;
  description?: string;
  programmed_exercises: ProgrammedExerciseCreate[];
}
```

#### TrainingSessionCreate
```typescript
interface TrainingSessionCreate {
  name: string;
  day_of_week?: number;
  session_order: number;
  description?: string;
  exercise_blocks: ExerciseBlockCreate[];
}
```

#### TrainingWeekCreate
```typescript
interface TrainingWeekCreate {
  week_number: number;
  description?: string;
  training_sessions: TrainingSessionCreate[];
}
```

#### TrainingProgramCreate
```typescript
interface TrainingProgramCreate {
  name: string;
  description?: string;
  program_type: ProgramType;
  duration_weeks: number;
  is_ai_generated?: boolean; // default: false
  training_weeks: TrainingWeekCreate[];
}
```

### Esquemas de Actualización

#### TrainingProgramUpdate
```typescript
interface TrainingProgramUpdate {
  name?: string;
  description?: string;
  program_type?: ProgramType;
  duration_weeks?: number;
}
```

### Esquemas Específicos

#### ProgramProgressResponse
```typescript
interface ProgramProgressResponse {
  program_id: number;
  program_name: string;
  completion_percentage: number;
  total_programmed_exercises: number;
  completed_exercises: number;
  total_weeks: number;
  program_type: string;
}
```

#### ProgramWeekResponse
```typescript
interface ProgramWeekResponse {
  week_id: number;
  week_number: number;
  description?: string;
  total_sessions: number;
  total_exercises: number;
  sessions: {
    session_id: number;
    name: string;
    day_of_week?: number;
    description?: string;
    exercise_blocks: {
      block_id: number;
      name: string;
      block_type: string;
      order: number;
      exercises_count: number;
    }[];
  }[];
}
```

#### ProgramSessionsResponse
```typescript
interface ProgramSessionsResponse {
  program_id: number;
  program_name: string;
  total_sessions: number;
  filtered_by_week?: number;
  sessions: {
    id: number;
    name: string;
    description?: string;
    session_order: number;
    day_of_week?: number;
    week: {
      week_number: number;
      description?: string;
    };
    exercise_blocks_count: number;
    programmed_exercises_count: number;
    active_session?: {
      id: number;
      start_time?: string;
      completion_percentage: number;
    };
    can_start: boolean;
  }[];
}
```

#### ProgramTemplate
```typescript
interface ProgramTemplate {
  id: string;
  name: string;
  description: string;
  program_type: string;
  duration_weeks: number;
  difficulty: "beginner" | "intermediate" | "advanced";
}
```

## Endpoints

### 1. Crear Programa de Entrenamiento

**POST** `/`

Crea un programa de entrenamiento completo con todas sus semanas, sesiones, bloques de ejercicios y ejercicios programados.

#### Request Body
```typescript
TrainingProgramCreate
```

#### Response
- **Status:** 201 Created
- **Body:** `TrainingProgramResponse`

#### Ejemplo de Request
```json
{
  "name": "Mi Programa de Fuerza",
  "description": "Programa 5/3/1 modificado",
  "program_type": "strength",
  "duration_weeks": 12,
  "is_ai_generated": false,
  "training_weeks": [
    {
      "week_number": 1,
      "description": "Semana de introducción",
      "training_sessions": [
        {
          "name": "Sesión A - Tren Superior",
          "day_of_week": 0,
          "session_order": 0,
          "description": "Enfoque en press banca y dominadas",
          "exercise_blocks": [
            {
              "name": "Bloque Principal",
              "block_type": "main",
              "order": 1,
              "description": "Ejercicios principales",
              "programmed_exercises": [
                {
                  "standard_exercise_id": 1,
                  "sets": 5,
                  "reps": 5,
                  "load_type": "percentage",
                  "percentage_1rm": 85.0,
                  "rest_seconds": 180,
                  "sets_type": "strength"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### 2. Obtener Programas de Entrenamiento

**GET** `/`

Obtiene todos los programas de entrenamiento del usuario actual (sin componentes anidados).

#### Query Parameters
- `skip` (int, optional): Número de registros a omitir (default: 0, min: 0)
- `limit` (int, optional): Número máximo de registros a devolver (default: 100, min: 1, max: 100)

#### Response
- **Status:** 200 OK
- **Body:** `TrainingProgramSimpleResponse[]`

### 3. Obtener Programa Específico

**GET** `/{program_id}`

Obtiene un programa de entrenamiento específico con toda su estructura completa.

#### Path Parameters
- `program_id` (int): ID del programa (min: 1)

#### Response
- **Status:** 200 OK
- **Body:** `TrainingProgramResponse`

#### Errores
- **404:** Programa no encontrado
- **403:** No autorizado para acceder a este programa

### 4. Actualizar Programa

**PATCH** `/{program_id}`

Actualiza la información básica de un programa de entrenamiento (no sus componentes).

#### Path Parameters
- `program_id` (int): ID del programa (min: 1)

#### Request Body
```typescript
TrainingProgramUpdate
```

#### Response
- **Status:** 200 OK
- **Body:** `TrainingProgramResponse`

#### Errores
- **404:** Programa no encontrado
- **403:** No autorizado para actualizar este programa

### 5. Eliminar Programa

**DELETE** `/{program_id}`

Elimina un programa de entrenamiento y todos sus componentes.

#### Path Parameters
- `program_id` (int): ID del programa (min: 1)

#### Response
- **Status:** 204 No Content

#### Errores
- **404:** Programa no encontrado
- **403:** No autorizado para eliminar este programa
- **500:** Error interno al eliminar el programa

### 6. Activar Programa

**POST** `/{program_id}/activate`

Activa un programa de entrenamiento (desactiva otros programas del usuario).

#### Path Parameters
- `program_id` (int): ID del programa (min: 1)

#### Response
- **Status:** 200 OK
- **Body:** `TrainingProgramResponse`

#### Errores
- **404:** Programa no encontrado
- **403:** No autorizado para activar este programa

### 7. Obtener Progreso del Programa

**GET** `/{program_id}/progress`

Obtiene estadísticas de progreso de un programa de entrenamiento.

#### Path Parameters
- `program_id` (int): ID del programa (min: 1)

#### Response
- **Status:** 200 OK
- **Body:** `ProgramProgressResponse`

#### Ejemplo de Response
```json
{
  "program_id": 123,
  "program_name": "Mi Programa de Fuerza",
  "completion_percentage": 65.5,
  "total_programmed_exercises": 120,
  "completed_exercises": 78,
  "total_weeks": 12,
  "program_type": "strength"
}
```

### 8. Obtener Semana Específica

**GET** `/{program_id}/weeks/{week_number}`

Obtiene información detallada de una semana específica del programa.

#### Path Parameters
- `program_id` (int): ID del programa (min: 1)
- `week_number` (int): Número de la semana (min: 1)

#### Response
- **Status:** 200 OK
- **Body:** `ProgramWeekResponse`

#### Errores
- **404:** Programa o semana no encontrada
- **403:** No autorizado para acceder a este programa

### 9. Obtener Programa Activo

**GET** `/active`

Obtiene el programa de entrenamiento actualmente activo del usuario.

#### Response
- **Status:** 200 OK
- **Body:** `TrainingProgramResponse | null`

### 10. Obtener Plantillas de Programas

**GET** `/templates`

Obtiene plantillas de programas predefinidas que se pueden usar para crear nuevos programas.

#### Query Parameters
- `program_type` (string, optional): Filtrar por tipo de programa ("strength", "hypertrophy", "peaking")

#### Response
- **Status:** 200 OK
- **Body:** `ProgramTemplate[]`

#### Ejemplo de Response
```json
[
  {
    "id": "beginner_strength",
    "name": "Beginner Strength Program",
    "description": "5/3/1 based program for beginners",
    "program_type": "strength",
    "duration_weeks": 12,
    "difficulty": "beginner"
  },
  {
    "id": "intermediate_hypertrophy",
    "name": "Intermediate Hypertrophy Program",
    "description": "Push/Pull/Legs split for muscle growth",
    "program_type": "hypertrophy",
    "duration_weeks": 16,
    "difficulty": "intermediate"
  }
]
```

### 11. Crear Programa desde Plantilla

**POST** `/from-template/{template_id}`

Crea un programa de entrenamiento basado en una plantilla predefinida.

#### Path Parameters
- `template_id` (string): ID de la plantilla

#### Query Parameters
- `program_name` (string): Nombre para el nuevo programa (min: 1, max: 100 caracteres)
- `customize_weights` (boolean, optional): Si personalizar los pesos (default: false)

#### Response
- **Status:** 201 Created
- **Body:** `TrainingProgramResponse`

#### Errores
- **501:** Funcionalidad no implementada aún

### 12. Obtener Sesiones del Programa

**GET** `/{program_id}/sessions`

Obtiene todas las sesiones de un programa específico con información detallada sobre su estado.

#### Path Parameters
- `program_id` (int): ID del programa

#### Query Parameters
- `week_number` (int, optional): Filtrar por número de semana específico

#### Response
- **Status:** 200 OK
- **Body:** `ProgramSessionsResponse`

#### Ejemplo de Response
```json
{
  "program_id": 123,
  "program_name": "Mi Programa de Fuerza",
  "total_sessions": 36,
  "filtered_by_week": null,
  "sessions": [
    {
      "id": 1,
      "name": "Sesión A - Tren Superior",
      "description": "Enfoque en press banca y dominadas",
      "session_order": 0,
      "day_of_week": 0,
      "week": {
        "week_number": 1,
        "description": "Semana de introducción"
      },
      "exercise_blocks_count": 2,
      "programmed_exercises_count": 8,
      "active_session": {
        "id": 1,
        "start_time": "2025-07-21T10:30:00Z",
        "completion_percentage": 45
      },
      "can_start": false
    }
  ]
}
```

## Códigos de Error

### Códigos HTTP Comunes
- **200:** OK - Solicitud exitosa
- **201:** Created - Recurso creado exitosamente
- **204:** No Content - Eliminación exitosa
- **400:** Bad Request - Datos de entrada inválidos
- **401:** Unauthorized - Token de autenticación faltante o inválido
- **403:** Forbidden - No autorizado para realizar esta acción
- **404:** Not Found - Recurso no encontrado
- **500:** Internal Server Error - Error interno del servidor
- **501:** Not Implemented - Funcionalidad no implementada

### Formato de Errores
```typescript
interface ErrorResponse {
  detail: string;
}
```

## Notas Importantes

1. **Autenticación**: Todos los endpoints requieren un usuario autenticado y verificado.

2. **Permisos**: Los usuarios solo pueden acceder a sus propios programas de entrenamiento.

3. **Estructura Jerárquica**: Los programas tienen una estructura anidada:
   - Programa → Semanas → Sesiones → Bloques de Ejercicios → Ejercicios Programados

4. **Validaciones**:
   - Los IDs de path deben ser >= 1
   - Los parámetros de paginación tienen límites específicos
   - Los nombres de programas tienen límites de longitud

5. **Fechas**: Todas las fechas están en formato ISO 8601 UTC.

6. **Tipos de Datos Opcionales**: Muchos campos son opcionales para permitir flexibilidad en la creación de programas.

7. **Sesiones Activas**: Solo puede haber una sesión activa por usuario a la vez.
