# Guía de Ordenamiento Automático - Semanas, Sesiones y Ejercicios

## 🎯 Descripción General

El sistema ahora asigna automáticamente los campos de orden basándose en la **posición en el array** cuando no se especifican explícitamente. Esto aplica para:

- `week_number` en semanas
- `session_order` en sesiones  
- `exercise_order` en ejercicios

## 🔄 Comportamiento Automático

### ✅ **Week Number (week_number)**
- Si NO se especifica → Se calcula como `posición_en_array + 1`
- Si se especifica → Se respeta el valor proporcionado
- **Ejemplo**: `[semana1, semana2, semana3]` → `week_number: [1, 2, 3]`

### ✅ **Session Order (session_order)**  
- Si NO se especifica → Se calcula como `posición_en_array` (0-indexed)
- Si se especifica → Se respeta el valor proporcionado
- **Ejemplo**: `[sesion1, sesion2, sesion3]` → `session_order: [0, 1, 2]`

### ✅ **Exercise Order (exercise_order)**
- Si NO se especifica → Se agrega al final (max_order + 1)
- Si se especifica → Se inserta en esa posición
- **Ejemplo**: `[ejercicio1, ejercicio2, ejercicio3]` → `exercise_order: [0, 1, 2]`

## 📊 Cambios en los Schemas

### **Campos Opcionales**
```python
class TrainingWeekBase(BaseModel):
    week_number: Optional[int] = None  # Auto-calculado si no se proporciona

class TrainingSessionBase(BaseModel):
    session_order: Optional[int] = None  # Auto-calculado si no se proporciona

class ProgrammedExerciseBase(BaseModel):
    exercise_order: Optional[int] = None  # Auto-calculado si no se proporciona
```

## 🔧 Casos de Uso

### **1. Crear Programa Completo (Orden Automático)**
```json
{
  "name": "Mi Programa",
  "training_weeks": [
    {
      "description": "Semana 1",  // week_number = 1 (auto)
      "training_sessions": [
        {
          "name": "Sesión A",  // session_order = 0 (auto)
          "programmed_exercises": [
            {
              "standard_exercise_id": 1,  // exercise_order = 0 (auto)
              "block": "main"
            },
            {
              "standard_exercise_id": 2,  // exercise_order = 1 (auto)
              "block": "main"
            }
          ]
        },
        {
          "name": "Sesión B",  // session_order = 1 (auto)
          "programmed_exercises": [...]
        }
      ]
    },
    {
      "description": "Semana 2",  // week_number = 2 (auto)
      "training_sessions": [...]
    }
  ]
}
```

### **2. Crear Semana Individual (POST /weeks)**
```json
{
  "description": "Nueva semana",  // week_number = max + 1 (auto)
  "training_sessions": [
    {
      "name": "Sesión nueva",  // session_order = 0 (auto)
      "programmed_exercises": [...]
    }
  ]
}
```

### **3. Crear Sesión Individual (POST /sessions)**
```json
{
  "name": "Nueva sesión",  // session_order = max + 1 (auto)
  "programmed_exercises": [
    {
      "standard_exercise_id": 1,  // exercise_order = 0 (auto)
      "block": "main"
    }
  ]
}
```

### **4. Crear Ejercicio Individual (POST /exercises)**
```json
{
  "standard_exercise_id": 1,  // exercise_order = max + 1 (auto)
  "block": "main",
  "sets": 3,
  "reps": 10
}
```

## 🎯 Ventajas

### ✅ **Para Frontend**
- **Menos código**: No necesita calcular órdenes manualmente
- **Menos errores**: No hay riesgo de órdendes duplicados
- **Más simple**: Solo ordena los arrays y el backend se encarga del resto

### ✅ **Para Backend**
- **Consistencia**: Órdenes siempre válidos y sin gaps
- **Flexibilidad**: Permite especificar orden custom cuando se necesite
- **Mantenimiento**: Reordenamiento automático al eliminar

## 📝 Notas Importantes

1. **Compatibilidad**: Los endpoints existentes siguen funcionando igual
2. **Retrocompatibilidad**: Programas existentes no se ven afectados
3. **Prioridad**: Si se especifica un orden, se respeta; si no, se calcula automáticamente
4. **Reordenamiento**: Al eliminar elementos, los órdenes se recompactan automáticamente

## 🚀 Endpoints Nuevos

- `POST /programs/{program_id}/weeks` - Crear semana con orden automático
- `POST /programs/{program_id}/weeks/{week_id}/sessions` - Crear sesión con orden automático
- `POST /programs/{program_id}/weeks/{week_id}/sessions/{session_id}/exercises` - Crear ejercicio con orden automático (ya existía)

## 🔍 Ejemplo Completo

Ver archivo: `test_auto_ordering.json` para un ejemplo completo de programa sin especificar ningún campo de orden.
