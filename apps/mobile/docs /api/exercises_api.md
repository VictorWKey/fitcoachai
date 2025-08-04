# API de Ejercicios - Documentación para Frontend

Esta documentación describe todos los endpoints disponibles en el router de ejercicios (`/exercises`) para que los desarrolladores frontend puedan consumir la API correctamente.

## Base URL
```
/exercises
```

## Autenticación
Todos los endpoints requieren autenticación JWT válida en el header `Authorization: Bearer <token>`, excepto donde se indique lo contrario.

---

## 1. Obtener Ejercicios Recientes

### `GET /exercises/recent`

Obtiene los ejercicios más recientes realizados por el usuario.

#### Parámetros de consulta
- `limit` (opcional): Número máximo de ejercicios a retornar (1-50, por defecto: 10)

#### Respuesta exitosa (200)
```json
[
  {
    "exercise_name": "Press de banca",
    "type": "strength",
    "exercise_date": "2025-01-20T10:30:00",
    "set_number": 3,
    "reps": 10,
    "weight": 80.0,
    "weight_unit": "kg",
    "rir": 2,
    "rpe": 8.0,
    "notes": "Buena sesión"
  },
  {
    "exercise_name": "Caminata en cinta",
    "type": "cardio",
    "exercise_date": "2025-01-19T18:00:00",
    "duration": 1800,
    "distance": 5.0,
    "distance_unit": "km",
    "avg_heart_rate": 140,
    "max_heart_rate": 160,
    "calories_burned": 300
  }
]
```

#### Estructura de respuesta por tipo:

**Ejercicios de fuerza:**
- `exercise_name`: string - Nombre del ejercicio
- `type`: "strength"
- `exercise_date`: string (ISO) - Fecha y hora del ejercicio
- `set_number`: number - Número de serie
- `reps`: number - Repeticiones realizadas
- `weight`: number - Peso utilizado
- `weight_unit`: string - Unidad de peso ("kg", "lbs")
- `rir`: number - Repeticiones en reserva
- `rpe`: number - Percepción del esfuerzo
- `notes`: string - Notas adicionales

**Ejercicios de cardio:**
- `exercise_name`: string - Nombre del ejercicio
- `type`: "cardio"
- `exercise_date`: string (ISO) - Fecha y hora del ejercicio
- `duration`: number - Duración en segundos
- `distance`: number - Distancia recorrida
- `distance_unit`: string - Unidad de distancia
- `avg_heart_rate`: number - Frecuencia cardíaca promedio
- `max_heart_rate`: number - Frecuencia cardíaca máxima
- `calories_burned`: number - Calorías quemadas

---

## 2. Obtener Ejercicios Populares

### `GET /exercises/popular`

Obtiene los ejercicios más frecuentemente realizados por el usuario.

#### Parámetros de consulta
- `limit` (opcional): Número máximo de ejercicios a retornar (1-50, por defecto: 10)

#### Respuesta exitosa (200)
```json
[
  {
    "exercise_name": "Press de banca",
    "frequency": 45,
    "type": "strength"
  },
  {
    "exercise_name": "Sentadillas",
    "frequency": 38,
    "type": "strength"
  },
  {
    "exercise_name": "Caminata en cinta",
    "frequency": 25,
    "type": "cardio"
  }
]
```

#### Estructura de respuesta:
- `exercise_name`: string - Nombre del ejercicio
- `frequency`: number - Número de veces que se ha realizado
- `type`: string - Tipo de ejercicio ("strength" | "cardio")

---

## 3. Obtener Estadísticas de Ejercicios

### `GET /exercises/stats`

Obtiene estadísticas agregadas sobre los ejercicios del usuario.

#### Parámetros de consulta
- `days` (opcional): Número de días hacia atrás para calcular estadísticas (1-365, por defecto: 30)

#### Respuesta exitosa (200)
```json
{
  "date_range": {
    "start_date": "2024-12-21T00:00:00",
    "end_date": "2025-01-20T23:59:59",
    "days": 30
  },
  "strength": {
    "total_sets": 120,
    "unique_exercises": 15,
    "avg_weight": 65.5,
    "total_reps": 1800
  },
  "cardio": {
    "total_sessions": 12,
    "unique_exercises": 4,
    "avg_duration": 1650.0,
    "total_duration": 19800.0
  }
}
```

#### Estructura de respuesta:
- `date_range`: Objeto con el rango de fechas analizado
  - `start_date`: string (ISO) - Fecha de inicio
  - `end_date`: string (ISO) - Fecha de fin
  - `days`: number - Días analizados
- `strength`: Estadísticas de ejercicios de fuerza
  - `total_sets`: number - Total de series realizadas
  - `unique_exercises`: number - Ejercicios únicos realizados
  - `avg_weight`: number - Peso promedio utilizado
  - `total_reps`: number - Total de repeticiones
- `cardio`: Estadísticas de ejercicios cardiovasculares
  - `total_sessions`: number - Total de sesiones
  - `unique_exercises`: number - Ejercicios únicos realizados
  - `avg_duration`: number - Duración promedio en segundos
  - `total_duration`: number - Duración total en segundos

---

## 4. Buscar Ejercicios

### `GET /exercises/search`

Busca ejercicios por nombre que el usuario haya realizado previamente.

#### Parámetros de consulta
- `query` (requerido): Término de búsqueda (1-100 caracteres)

#### Respuesta exitosa (200)
```json
[
  {
    "exercise_name": "Press de banca",
    "type": "strength",
    "usage_count": 45
  },
  {
    "exercise_name": "Press inclinado",
    "type": "strength", 
    "usage_count": 23
  }
]
```

#### Estructura de respuesta:
- `exercise_name`: string - Nombre del ejercicio
- `type`: string - Tipo de ejercicio ("strength" | "cardio")
- `usage_count`: number - Número de veces que el usuario ha realizado este ejercicio

---

## 5. Obtener Progreso de un Ejercicio

### `GET /exercises/progress/{exercise_name}`

Obtiene el historial de progreso para un ejercicio específico.

#### Parámetros de ruta
- `exercise_name`: string - Nombre del ejercicio

#### Parámetros de consulta
- `days` (opcional): Número de días hacia atrás (1-365, por defecto: 90)

#### Respuesta exitosa (200)
```json
[
  {
    "date": "2025-01-15T10:30:00",
    "type": "strength",
    "exercise_name": "Press de banca",
    "reps": 10,
    "weight": 80.0,
    "weight_unit": "kg",
    "rir": 2,
    "rpe": 8.0,
    "set_number": 1
  },
  {
    "date": "2025-01-12T18:00:00",
    "type": "cardio",
    "exercise_name": "Caminata en cinta",
    "duration": 1800,
    "distance": 5.0,
    "distance_unit": "km",
    "avg_heart_rate": 140,
    "max_heart_rate": 160,
    "calories_burned": 300
  }
]
```

La estructura varía según el tipo de ejercicio (similar a `/recent`).

---

## 6. Obtener Catálogo de Ejercicios

### `GET /exercises/catalog`

Obtiene un catálogo de todos los ejercicios únicos realizados por el usuario, organizados por grupo muscular.

#### Respuesta exitosa (200)
```json
{
  "pectoral": [
    "Press de banca",
    "Press inclinado",
    "Aperturas con mancuernas"
  ],
  "espalda": [
    "Dominadas",
    "Remo con barra",
    "Jalones"
  ],
  "Cardio": [
    "Caminata en cinta",
    "Bicicleta estática",
    "Elíptica"
  ],
  "Unknown": [
    "Ejercicio personalizado"
  ]
}
```

#### Estructura de respuesta:
- Objeto con claves siendo los nombres de grupos musculares y valores siendo arrays de nombres de ejercicios
- Los ejercicios de cardio se agrupan bajo la clave "Cardio"
- Los ejercicios sin grupo muscular conocido se agrupan bajo "Unknown"

---

## 7. Obtener Récords Personales

### `GET /exercises/personal-records`

Obtiene los récords personales de peso máximo para ejercicios de fuerza.

#### Respuesta exitosa (200)
```json
[
  {
    "exercise_name": "Press de banca",
    "max_weight": 100.0,
    "weight_unit": "kg",
    "record_date": "2025-01-15T10:30:00"
  },
  {
    "exercise_name": "Sentadillas",
    "max_weight": 120.0,
    "weight_unit": "kg", 
    "record_date": "2025-01-10T16:45:00"
  }
]
```

#### Estructura de respuesta:
- `exercise_name`: string - Nombre del ejercicio
- `max_weight`: number - Peso máximo levantado
- `weight_unit`: string - Unidad de peso
- `record_date`: string (ISO) - Fecha del récord

---

## 8. Obtener Ejercicios Estándar

### `GET /exercises/standard`

Obtiene ejercicios estandarizados de la base de datos con sus IDs reales.

#### Parámetros de consulta
- `equipment` (opcional): Filtrar por tipo de equipo
- `muscle_group` (opcional): Filtrar por grupo muscular  
- `exercise_type` (opcional): Filtrar por tipo de ejercicio
- `limit` (opcional): Número máximo a retornar (1-500, por defecto: 100)

#### Valores válidos para filtros:

**Equipment:**
- `barra`
- `mancuernas`
- `maquina`
- `poleas`
- `peso_corporal`
- `discos`

**Muscle Groups:**
- `pectoral`
- `espalda`
- `biceps`
- `triceps`
- `abdomen`
- `gluteo`
- `cuadriceps`
- `aductor`
- `isquiotibiales`
- `pantorrilla`
- `trapecio`
- `hombro_posterior`
- `hombro_lateral`
- `hombro_frontal`
- `antebrazo`
- `core`
- `oblicuos`
- `zona_lumbar`
- `cuello`

**Exercise Types:**
- `compuesto`
- `aislado`

#### Respuesta exitosa (200)
```json
[
  {
    "id": 1,
    "standard_name": "Press de banca",
    "main_muscle_group": "pectoral",
    "equipment": "barra",
    "type": "compuesto"
  },
  {
    "id": 2,
    "standard_name": "Curl de bíceps",
    "main_muscle_group": "biceps",
    "equipment": "mancuernas",
    "type": "aislado"
  }
]
```

#### Estructura de respuesta:
- `id`: number - ID único del ejercicio
- `standard_name`: string - Nombre estándar del ejercicio
- `main_muscle_group`: string - Grupo muscular principal
- `equipment`: string - Equipo utilizado
- `type`: string - Tipo de ejercicio

---

## 9. Autocompletar Ejercicios

### `GET /exercises/autocomplete`

Proporciona sugerencias de autocompletado para nombres de ejercicios.

#### Parámetros de consulta
- `query` (requerido): Término de búsqueda (2-50 caracteres)
- `limit` (opcional): Número máximo de sugerencias (1-50, por defecto: 10)

#### Respuesta exitosa (200)
```json
[
  "Press de banca",
  "Press inclinado",
  "Press declinado",
  "Press militar"
]
```

#### Estructura de respuesta:
Array de strings con nombres de ejercicios que coinciden con la búsqueda.

---

## 10. Obtener Tipos de Equipo

### `GET /exercises/equipment-types`

Obtiene todos los tipos de equipo válidos para ejercicios.

#### Respuesta exitosa (200)
```json
[
  {
    "value": "barra",
    "label": "Barra"
  },
  {
    "value": "mancuernas",
    "label": "Mancuernas"
  },
  {
    "value": "peso_corporal",
    "label": "Peso Corporal"
  }
]
```

#### Estructura de respuesta:
- `value`: string - Valor del enum para usar en la API
- `label`: string - Etiqueta legible para mostrar al usuario

---

## 11. Obtener Grupos Musculares

### `GET /exercises/muscle-groups`

Obtiene todos los grupos musculares válidos para ejercicios.

#### Respuesta exitosa (200)
```json
[
  {
    "value": "pectoral",
    "label": "Pectoral"
  },
  {
    "value": "espalda", 
    "label": "Espalda"
  },
  {
    "value": "hombro_posterior",
    "label": "Hombro Posterior"
  }
]
```

#### Estructura de respuesta:
- `value`: string - Valor del enum para usar en la API
- `label`: string - Etiqueta legible para mostrar al usuario

---

## 12. Obtener Tipos de Ejercicio

### `GET /exercises/exercise-types`

Obtiene todos los tipos de ejercicio válidos.

#### Respuesta exitosa (200)
```json
[
  {
    "value": "compuesto",
    "label": "Compuesto"
  },
  {
    "value": "aislado",
    "label": "Aislado"
  }
]
```

#### Estructura de respuesta:
- `value`: string - Valor del enum para usar en la API
- `label`: string - Etiqueta legible para mostrar al usuario

---

## 13. Health Check

### `GET /exercises/health`

Endpoint de verificación de estado del router.

#### Respuesta exitosa (200)
```json
{
  "status": "ok",
  "message": "Exercises router is working"
}
```

---

## Códigos de Error Comunes

### 400 Bad Request
```json
{
  "detail": "Invalid equipment type: invalid_equipment"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is greater than or equal to 1",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

---

## Notas para Implementación Frontend

1. **Autenticación**: Todos los endpoints (excepto `/health`) requieren token JWT válido.

2. **Fechas**: Todas las fechas están en formato ISO 8601 (UTC).

3. **Paginación**: Los endpoints que retornan listas tienen parámetros `limit` para controlar el tamaño de respuesta.

4. **Filtros**: Los endpoints de búsqueda son case-insensitive y usan coincidencia parcial.

5. **Tipos de datos**: 
   - Los números decimales se retornan como `float`
   - Las fechas como strings ISO
   - Los enums como strings con sus valores

6. **Manejo de errores**: Siempre verificar el código de estado HTTP y manejar los errores de validación apropiadamente.

7. **Performance**: Los endpoints están optimizados pero considera implementar caching en el frontend para datos que no cambian frecuentemente (como tipos de equipo, grupos musculares).
