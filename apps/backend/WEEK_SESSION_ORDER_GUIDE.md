# Guía de Semanas y Sesiones con Orden Automático

## 🔄 Cambios en las Peticiones API

### 1. **POST - Crear Semana** (NUEVO CAMPO OPCIONAL)

```bash
curl -X POST "http://localhost:8000/training/programs/1/weeks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "week_number": 3,          # ⬅️ OPCIONAL: semana deseada (opcional)
    "description": "Semana de carga",
    "training_sessions": [
      {
        "name": "Sesión A",
        "session_order": 0,    # ⬅️ OPCIONAL: posición deseada (opcional)
        "day_of_week": 1,
        "description": "Empuje",
        "programmed_exercises": [
          {
            "standard_exercise_id": 1,
            "block": "main",
            "exercise_order": 0,  # ⬅️ OPCIONAL: ya implementado
            "sets": 3,
            "reps": 8
          }
        ]
      }
    ]
  }'
```

**Comportamiento:**
- Si `week_number` NO se especifica → Se asigna automáticamente (último + 1)
- Si `week_number` se especifica → Se usa el valor proporcionado
- Si `session_order` NO se especifica → Se calcula automáticamente basado en `day_of_week` (orden cronológico)
- Si `session_order` se especifica → Se usa el valor proporcionado

**Lógica automática de session_order:**
```
day_of_week = 1 (lunes)    → session_order = 0
day_of_week = 3 (miércoles) → session_order = 1  
day_of_week = 5 (viernes)   → session_order = 2
```

### 2. **POST - Crear Sesión** (NUEVO CAMPO OPCIONAL)

```bash
curl -X POST "http://localhost:8000/training/programs/1/weeks/2/sessions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sesión C",
    "day_of_week": 5,         # ⬅️ DETERMINA session_order automáticamente
    "description": "Piernas",
    "programmed_exercises": [
      {
        "standard_exercise_id": 5,
        "block": "main",
        "exercise_order": 0,   # ⬅️ OPCIONAL: ya implementado
        "sets": 4,
        "reps": 6
      }
    ]
  }'
```

**Resultado:** Si ya existen sesiones en lunes (1) y miércoles (3), esta sesión de viernes (5) recibirá automáticamente `session_order = 2`.

### 3. **PUT - Actualizar Programa Completo** (COMPORTAMIENTO MEJORADO)

```bash
curl -X PUT "http://localhost:8000/training/programs/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Programa Actualizado",
    "program_type": "strength",
    "duration_weeks": 4,
    "training_weeks": [
      {
        "id": 1,
        "week_number": 1,      # ⬅️ RESPETADO: si se proporciona
        "training_sessions": [
          {
            "id": 1,
            "name": "Sesión A",
            "session_order": 0   # ⬅️ RESPETADO: si se proporciona
          },
          {
            "name": "Sesión B Nueva"
            # session_order se calcula automáticamente como 1
          }
        ]
      },
      {
        "description": "Semana nueva"
        # week_number se calcula automáticamente como 2
      }
    ]
  }'
```

## 🔧 Comportamientos Automáticos

### ✅ **Al Crear Programa Completo:**
- Las semanas reciben numeración secuencial **por programa**: 
  - Programa: semanas [1, 2, 3, 4]
- Las sesiones reciben orden secuencial **por día de semana dentro de cada semana**:
  - Semana 1: Lunes=0, Miércoles=1, Viernes=2
  - Semana 2: Lunes=0, Miércoles=1, Viernes=2 
  - Semana 3: Martes=0, Jueves=1, Sábado=2
- Los ejercicios reciben orden secuencial **por sesión**:
  - Sesión 1: ejercicios [0, 1, 2]
  - Sesión 2: ejercicios [0, 1, 2]

### ✅ **Al Crear Semana Individual:**
- Sin `week_number` → Se agrega al final (number = max + 1 dentro del programa)
- Con `week_number` → Se usa el valor proporcionado
- Las sesiones dentro de la semana reciben `session_order` basado en orden cronológico de `day_of_week`

### ✅ **Al Crear Sesión Individual:**
- Sin `session_order` → Se calcula automáticamente basado en `day_of_week` (posición cronológica)
- Con `session_order` → Se usa el valor proporcionado
- Los ejercicios dentro de la sesión reciben `exercise_order` basado en su posición en el array

### ✅ **Al Obtener:**
- Semanas siempre ordenadas por `week_number`
- Sesiones siempre ordenadas por `session_order` (que refleja orden cronológico)
- Ejercicios siempre ordenados por `exercise_order`
- Mantiene separación por contexto (programa → semana → sesión)

## 🎯 Casos de Uso Frontend

### **Escenario 1: Agregar Semana al Final**
```javascript
// No especificar week_number, sessions se ordenan por day_of_week
const newWeek = {
  description: "Semana de descarga",
  training_sessions: [
    {
      name: "Sesión A",
      day_of_week: 5  // Viernes → session_order = 0 (primera sesión cronológicamente)
    },
    {
      name: "Sesión B", 
      day_of_week: 1  // Lunes → session_order = 1 (segunda sesión cronológicamente)
    },
    {
      name: "Sesión C",
      day_of_week: 3  // Miércoles → session_order = 2 (tercera sesión cronológicamente)
    }
  ]
  // week_number omitido → se agrega al final
  // sessions se reordenarán: Lunes=0, Miércoles=1, Viernes=2
}
```

### **Escenario 2: Insertar Semana en Posición Específica**
```javascript
// Insertar como segunda semana
const newWeek = {
  week_number: 2,  // Insertar en posición 2
  description: "Semana intensiva",
  training_sessions: [...]
}
```

### **Escenario 3: Agregar Sesión en Orden Cronológico**
```javascript
// day_of_week determina automáticamente session_order
const newSession = {
  name: "Sesión Extra",
  day_of_week: 2,  // Martes
  programmed_exercises: [...]
  // Si ya existen: Lunes(0), Miércoles(1), Viernes(2)
  // Esta sesión de Martes recibirá session_order = 1
  // Y las demás se reordenarán: Lunes(0), Martes(1), Miércoles(2), Viernes(3)
}
```

### **Escenario 4: Programa Completo con Orden Cronológico Automático**
```javascript
// Las sessions se ordenarán automáticamente por day_of_week
const programData = {
  training_weeks: [
    {
      // Será week_number: 1
      training_sessions: [
        { name: "Viernes", day_of_week: 5 },    // session_order: 2 (último cronológicamente)
        { name: "Lunes", day_of_week: 1 },      // session_order: 0 (primero cronológicamente)  
        { name: "Miércoles", day_of_week: 3 }   // session_order: 1 (segundo cronológicamente)
      ]
      // Backend reordenará automáticamente por day_of_week
    },
    {
      // Será week_number: 2
      training_sessions: [
        { name: "Jueves", day_of_week: 4 },     // session_order: 1
        { name: "Martes", day_of_week: 2 }      // session_order: 0
      ]
    }
  ]
}
```

## 📊 Base de Datos

### **Campos Existentes:**
```sql
-- training_weeks table
ALTER TABLE training_weeks 
ADD COLUMN week_number INTEGER NOT NULL;

-- training_sessions table  
ALTER TABLE training_sessions 
ADD COLUMN session_order INTEGER NOT NULL;

-- programmed_exercises table (ya existente)
ALTER TABLE programmed_exercises 
ADD COLUMN exercise_order INTEGER NOT NULL DEFAULT 0;
```

### **Datos Existentes:**
Los registros existentes mantendrán sus valores actuales.
Recomendado ejecutar un script para verificar secuencias correctas.

## 🚀 Beneficios

### **Para el Frontend:**
1. **Simplificación**: No necesita calcular manualmente week_number o session_order
2. **Orden Cronológico**: session_order se basa en day_of_week para orden lógico de la semana
3. **Flexibilidad**: Puede especificar orden explícito cuando necesite
4. **Consistencia**: Mismo comportamiento que exercise_order
5. **Predictibilidad**: day_of_week determina automáticamente la posición en la semana

### **Para el Backend:**
1. **Automatización**: Lógica centralizada de ordenamiento
2. **Mantenimiento**: Menos errores de inconsistencia
3. **Escalabilidad**: Fácil agregar funcionalidades similares

## 🔍 Ejemplos de Respuesta

### **POST /training/programs/1/weeks**
```json
{
  "id": 15,
  "program_id": 1,
  "week_number": 5,           // ⬅️ Calculado automáticamente
  "description": "Semana de carga",
  "training_sessions": [
    {
      "id": 45,
      "week_id": 15,
      "name": "Sesión A",
      "session_order": 0,     // ⬅️ Calculado automáticamente (día más temprano)
      "day_of_week": 1,
      "programmed_exercises": [
        {
          "id": 120,
          "session_id": 45,
          "exercise_order": 0 // ⬅️ Calculado automáticamente
        }
      ]
    }
  ]
}
```

### **POST /training/programs/1/weeks/2/sessions**
```json
{
  "id": 46,
  "week_id": 2,
  "name": "Sesión Extra",
  "session_order": 3,         // ⬅️ Calculado automáticamente (era la 4ta sesión cronológicamente)
  "day_of_week": 6,
  "programmed_exercises": []
}
```
