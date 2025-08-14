# Guía de Ejercicios con Orden

## 🔄 Cambios en las Peticiones API

### 1. **POST - Crear Ejercicio** (NUEVO CAMPO OPCIONAL)

```bash
curl -X POST "http://localhost:8000/training/programs/1/weeks/1/sessions/2/exercises" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "standard_exercise_id": 1,
    "block": "main",
    "exercise_order": 0,          # ⬅️ NUEVO: posición deseada (opcional)
    "tempo": "2-0-2-0",
    "sets": 3,
    "reps": 10,
    "load_type": "rpe",
    "rpe_target": 7.5,
    "rest_seconds": 90,
    "sets_type": "hypertrophy"
  }'
```

**Comportamiento:**
- Si `exercise_order` NO se especifica → Se agrega al final
- Si `exercise_order` se especifica → Se inserta en esa posición y reordena automáticamente

### 2. **GET - Listar Ejercicios** (MISMO ENDPOINT, NUEVO ORDEN)

```bash
curl -X GET "http://localhost:8000/training/programs/1/weeks/1/sessions/2/exercises" \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta ahora incluye `exercise_order`:**
```json
{
  "main": [
    {
      "id": 5,
      "exercise_order": 0,        # ⬅️ NUEVO CAMPO
      "exercise_name": "Squat",
      "block": "main",
      "sets": 3,
      "reps": 10
    },
    {
      "id": 4,
      "exercise_order": 1,        # ⬅️ NUEVO CAMPO  
      "exercise_name": "Deadlift",
      "block": "main",
      "sets": 4,
      "reps": 8
    }
  ],
  "accessory": [...]
}
```

### 3. **PATCH - Reordenar Ejercicios** (NUEVO ENDPOINT)

```bash
curl -X PATCH "http://localhost:8000/training/programs/1/weeks/1/sessions/2/exercises/reorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exercises": [
      {"id": 4, "exercise_order": 0},    # Deadlift primero
      {"id": 5, "exercise_order": 1}     # Squat segundo
    ]
  }'
```

**Uso:** Cuando el usuario arrastra ejercicios en el frontend para reordenarlos.

### 4. **PUT - Actualizar Ejercicio** (NUEVO CAMPO OPCIONAL)

```bash
curl -X PUT "http://localhost:8000/training/programs/1/weeks/1/sessions/2/exercises/4" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exercise_order": 2,          # ⬅️ NUEVO: cambiar posición
    "sets": 4,
    "reps": 12
  }'
```

## 🔧 Comportamientos Automáticos

### ✅ **Al Crear Programa Completo:**
- Los ejercicios reciben orden secuencial **por sesión**: 
  - Sesión 1: ejercicios [0, 1, 2]
  - Sesión 2: ejercicios [0, 1, 2] 
  - Sesión 3: ejercicios [0, 1, 2]

### ✅ **Al Crear Ejercicio Individual:**
- Sin `exercise_order` → Se agrega al final (order = max + 1 dentro de la sesión)
- Con `exercise_order` → Se inserta y empuja ejercicios hacia abajo

### ✅ **Al Eliminar:**
- Se recompacta automáticamente (0, 1, 2, 3...)
- No quedan huecos en la numeración dentro de cada sesión

### ✅ **Al Obtener:**
- Ejercicios siempre ordenados por `exercise_order`
- Mantiene separación por `block` (main/accessory)
- Orden reinicia en cada sesión

## 🎯 Casos de Uso Frontend

### **Escenario 1: Agregar al Final**
```javascript
// No especificar exercise_order
const newExercise = {
  standard_exercise_id: 3,
  block: "main",
  sets: 3,
  reps: 10
  // exercise_order omitido → se agrega al final
}
```

### **Escenario 2: Insertar en Posición Específica**
```javascript
// Insertar como segundo ejercicio
const newExercise = {
  standard_exercise_id: 3,
  block: "main",
  exercise_order: 1,  // Insertar en posición 1
  sets: 3,
  reps: 10
}
```

### **Escenario 3: Reordenar por Drag & Drop**
```javascript
// Después del drag & drop, enviar nuevo orden
const reorderRequest = {
  exercises: draggedOrder.map((exercise, index) => ({
    id: exercise.id,
    exercise_order: index
  }))
}
```

## 📊 Base de Datos

### **Nueva Columna:**
```sql
ALTER TABLE programmed_exercises 
ADD COLUMN exercise_order INTEGER NOT NULL DEFAULT 0;
```

### **Datos Existentes:**
Los ejercicios existentes recibirán `exercise_order = 0` por defecto.
Recomendado ejecutar un script para asignar orden secuencial basado en `created_at`.
