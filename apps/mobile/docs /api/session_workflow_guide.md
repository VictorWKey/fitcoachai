# Guía de Flujo de Trabajo: Gestión de Sesiones de Entrenamiento

## Introducción

Esta guía describe el flujo completo de endpoints que debe seguir el frontend para manejar correctamente los tres estados de una sesión de entrenamiento y las operaciones permitidas en cada uno.

## Estados de Sesión y Operaciones Permitidas

### 🚫 **Sesión Nunca Iniciada**
- **Estado**: `is_session_active = false` y `is_session_completed = false`
- **Operaciones permitidas**: Solo iniciar la sesión
- **Operaciones NO permitidas**: Agregar logs

### ✅ **Sesión Activa**
- **Estado**: `is_session_active = true`
- **Operaciones permitidas**: 
  - Agregar logs de ejercicios
  - Pausar/reanudar sesión
  - Finalizar sesión
  - Abandonar sesión

### 📝 **Sesión Finalizada**
- **Estado**: `is_session_completed = true` y `is_session_active = false`
- **Operaciones permitidas**:
  - Ver logs existentes
  - Modificar logs existentes
  - Agregar nuevos logs (para correcciones)
  - Eliminar logs

---

## Flujos de Frontend por Escenario

## 1. 🚫 **Entrada a Sesión Nunca Iniciada**

### Paso 1: Verificar Estado de la Sesión
```http
GET /sessions/{session_id}
```

**Validación en Frontend:**
```javascript
const checkSessionState = async (sessionId) => {
  const response = await api.get(`/sessions/${sessionId}`);
  const session = response.data.session;
  
  if (!session.is_session_active && !session.is_session_completed) {
    // Sesión nunca iniciada - mostrar botón "Iniciar Entrenamiento"
    showStartSessionButton(sessionId);
    disableLogButtons(); // Deshabilitar botones de agregar logs
  }
};
```

### Paso 2: Iniciar Sesión
```http
POST /sessions/start/{session_id}
```

**Implementación:**
```javascript
const startSession = async (sessionId) => {
  try {
    await api.post(`/sessions/start/${sessionId}`);
    // Redirigir a vista de sesión activa
    redirectToActiveSession(sessionId);
  } catch (error) {
    if (error.status === 400) {
      // Ya hay una sesión activa
      showError("Ya tienes una sesión activa. Finalízala primero.");
    }
  }
};
```

---

## 2. ✅ **Entrada a Sesión Activa**

### Paso 1: Verificar Estado y Cargar Datos
```http
GET /sessions/{session_id}
GET /sessions/{session_id}/logs
```

**Implementación:**
```javascript
const loadActiveSession = async (sessionId) => {
  // Obtener información de la sesión
  const sessionResponse = await api.get(`/sessions/${sessionId}`);
  const session = sessionResponse.data.session;
  
  if (session.is_session_active) {
    // Cargar logs existentes
    const logsResponse = await api.get(`/sessions/${sessionId}/logs`);
    
    displaySessionInterface({
      session: session,
      logs: logsResponse.data.logs,
      canAddLogs: true,
      canModifyLogs: true
    });
  }
};
```

### Paso 2: Agregar Logs de Ejercicios

#### Para Ejercicios de Fuerza:
```http
POST /sessions/logs/strength
```

**Para sesión activa (método actual):**
```javascript
const addStrengthLog = async (exerciseData) => {
  // Para sesión activa - usa el endpoint general
  const response = await api.post('/sessions/logs/strength', exerciseData);
  // Se actualiza automáticamente el heartbeat
  return response.data;
};
```

#### Para Ejercicios de Cardio:
```http
POST /sessions/logs/cardio
```

**Implementación:**
```javascript
const addCardioLog = async (cardioData) => {
  const response = await api.post('/sessions/logs/cardio', cardioData);
  return response.data;
};
```

### Paso 3: Verificar Progreso de Ejercicio
```http
GET /sessions/logs/exercise/{standard_exercise_id}/progress
```

**Implementación:**
```javascript
const checkExerciseProgress = async (exerciseId) => {
  const response = await api.get(`/sessions/logs/exercise/${exerciseId}/progress`);
  const progress = response.data;
  
  updateExerciseUI({
    exerciseId: exerciseId,
    completedSets: progress.completed_sets,
    remainingSets: progress.remaining_sets,
    nextSetNumber: progress.next_set_number,
    isComplete: progress.is_complete
  });
};
```

### Paso 4: Finalizar Sesión
```http
POST /sessions/finish
```

**Implementación:**
```javascript
const finishSession = async () => {
  try {
    const response = await api.post('/sessions/finish');
    // Redirigir a resumen de sesión
    redirectToSessionSummary(response.data.session);
  } catch (error) {
    showError("Error al finalizar la sesión");
  }
};
```

---

## 3. 📝 **Entrada a Sesión Finalizada**

### Paso 1: Cargar Sesión y Logs
```http
GET /sessions/{session_id}
GET /sessions/{session_id}/logs
```

**Implementación:**
```javascript
const loadCompletedSession = async (sessionId) => {
  const sessionResponse = await api.get(`/sessions/${sessionId}`);
  const session = sessionResponse.data.session;
  
  if (session.is_session_completed) {
    const logsResponse = await api.get(`/sessions/${sessionId}/logs`);
    
    displaySessionInterface({
      session: session,
      logs: logsResponse.data.logs,
      canAddLogs: true, // ✅ Permitir agregar logs para correcciones
      canModifyLogs: true, // ✅ Permitir modificar logs existentes
      showCompletedBadge: true
    });
  }
};
```

### Paso 2: Agregar Nuevos Logs (Correcciones)

#### Para Ejercicios de Fuerza:
```http
POST /sessions/{session_id}/logs/strength
```

**Para sesiones finalizadas:**
```javascript
const addStrengthLogToCompletedSession = async (sessionId, exerciseData) => {
  const response = await api.post(`/sessions/${sessionId}/logs/strength`, exerciseData);
  
  // Mostrar mensaje de confirmación
  showSuccess("Log agregado a sesión finalizada");
  
  // Recargar logs
  refreshSessionLogs(sessionId);
  
  return response.data;
};
```

#### Para Ejercicios de Cardio:
```http
POST /sessions/{session_id}/logs/cardio
```

### Paso 3: Modificar Logs Existentes

#### Actualizar Log de Fuerza:
```http
PUT /sessions/logs/strength/{log_id}
```

**Implementación:**
```javascript
const updateStrengthLog = async (logId, updatedData) => {
  const response = await api.put(`/sessions/logs/strength/${logId}`, updatedData);
  showSuccess("Log de fuerza actualizado");
  return response.data;
};
```

#### Actualizar Log de Cardio:
```http
PUT /sessions/logs/cardio/{log_id}
```

**Implementación:**
```javascript
const updateCardioLog = async (logId, updatedData) => {
  const response = await api.put(`/sessions/logs/cardio/${logId}`, updatedData);
  showSuccess("Log de cardio actualizado");
  return response.data;
};
```

### Paso 4: Eliminar Logs

#### Eliminar Log de Fuerza:
```http
DELETE /sessions/logs/strength/{log_id}
```

#### Eliminar Log de Cardio:
```http
DELETE /sessions/logs/cardio/{log_id}
```

**Implementación:**
```javascript
const deleteLog = async (logId, logType) => {
  const confirmed = await showConfirmDialog("¿Estás seguro de eliminar este log?");
  
  if (confirmed) {
    await api.delete(`/sessions/logs/${logType}/${logId}`);
    showSuccess("Log eliminado");
    refreshSessionLogs(sessionId);
  }
};
```

---

## Componente de Ejemplo: Interfaz de Sesión

```javascript
const SessionInterface = ({ sessionId }) => {
  const [session, setSession] = useState(null);
  const [logs, setLogs] = useState(null);
  const [sessionState, setSessionState] = useState('loading');
  
  useEffect(() => {
    loadSession();
  }, [sessionId]);
  
  const loadSession = async () => {
    try {
      const sessionResponse = await api.get(`/sessions/${sessionId}`);
      const sessionData = sessionResponse.data.session;
      
      // Determinar estado de la sesión
      if (!sessionData.is_session_active && !sessionData.is_session_completed) {
        setSessionState('never_started');
      } else if (sessionData.is_session_active) {
        setSessionState('active');
      } else if (sessionData.is_session_completed) {
        setSessionState('completed');
      }
      
      setSession(sessionData);
      
      // Cargar logs si la sesión fue iniciada
      if (sessionData.is_session_active || sessionData.is_session_completed) {
        const logsResponse = await api.get(`/sessions/${sessionId}/logs`);
        setLogs(logsResponse.data.logs);
      }
      
    } catch (error) {
      setSessionState('error');
    }
  };
  
  const renderInterface = () => {
    switch (sessionState) {
      case 'never_started':
        return (
          <div>
            <h2>{session.name}</h2>
            <p>Esta sesión aún no ha sido iniciada</p>
            <button onClick={() => startSession(sessionId)}>
              Iniciar Entrenamiento
            </button>
          </div>
        );
        
      case 'active':
        return (
          <ActiveSessionInterface 
            session={session}
            logs={logs}
            onAddLog={() => refreshLogs()}
            onFinishSession={() => finishSession()}
          />
        );
        
      case 'completed':
        return (
          <CompletedSessionInterface
            session={session}
            logs={logs}
            onAddLog={() => refreshLogs()}
            onModifyLog={() => refreshLogs()}
            onDeleteLog={() => refreshLogs()}
          />
        );
        
      default:
        return <LoadingSpinner />;
    }
  };
  
  return renderInterface();
};
```

---

## Validaciones Importantes

### 1. **Validación de Estado antes de Agregar Logs**
```javascript
const validateCanAddLogs = (session) => {
  if (!session.is_session_active && !session.is_session_completed) {
    throw new Error("No se pueden agregar logs a una sesión que nunca ha sido iniciada");
  }
  return true;
};
```

### 2. **Manejo de Errores Específicos**
```javascript
const handleLogError = (error) => {
  switch (error.status) {
    case 400:
      if (error.detail.includes("never been started")) {
        showError("Debes iniciar la sesión antes de agregar logs");
      } else if (error.detail.includes("already logged")) {
        showError("Este set ya está registrado. Usa editar para modificarlo.");
      }
      break;
    case 403:
      showError("No tienes permisos para modificar esta sesión");
      break;
    case 404:
      showError("Sesión no encontrada");
      break;
  }
};
```

---

## Resumen de Endpoints por Funcionalidad

### **Gestión de Sesiones:**
- `GET /sessions/{session_id}` - Obtener información de sesión
- `POST /sessions/start/{session_id}` - Iniciar sesión
- `POST /sessions/finish` - Finalizar sesión activa

### **Logs en Sesión Activa:**
- `POST /sessions/logs/strength` - Agregar log de fuerza (solo sesión activa)
- `POST /sessions/logs/cardio` - Agregar log de cardio (solo sesión activa)

### **Logs en Cualquier Sesión (Activa o Completada):**
- `POST /sessions/{session_id}/logs/strength` - Agregar log de fuerza
- `POST /sessions/{session_id}/logs/cardio` - Agregar log de cardio
- `GET /sessions/{session_id}/logs` - Obtener todos los logs
- `GET /sessions/{session_id}/logs/strength` - Obtener logs de fuerza
- `GET /sessions/{session_id}/logs/cardio` - Obtener logs de cardio

### **Modificación de Logs:**
- `PUT /sessions/logs/strength/{log_id}` - Actualizar log de fuerza
- `PUT /sessions/logs/cardio/{log_id}` - Actualizar log de cardio
- `DELETE /sessions/logs/strength/{log_id}` - Eliminar log de fuerza
- `DELETE /sessions/logs/cardio/{log_id}` - Eliminar log de cardio

### **Información de Progreso:**
- `GET /sessions/logs/exercise/{standard_exercise_id}/progress` - Progreso de ejercicio

---

## Casos Especiales

### **Sesión Auto-Pausada**
Si una sesión está en estado `auto_paused`, sigue el flujo normal de sesión activa pero muestra un diálogo de reanudación:

```javascript
const handleAutoPausedSession = async () => {
  const choice = await showResumeDialog();
  
  switch (choice) {
    case 'resume':
      await api.post('/sessions/resume');
      break;
    case 'finish':
      await api.post('/sessions/finish');
      break;
    case 'abandon':
      await api.post('/sessions/abandon');
      break;
  }
};
```

### **Múltiples Usuarios en la Misma Sesión**
El backend maneja automáticamente el filtrado de logs por usuario. Cada usuario solo ve y puede modificar sus propios logs.

---

Esta guía asegura que el frontend maneje correctamente todos los estados de sesión y proporcione la funcionalidad adecuada en cada caso.
