# Guía de Integración: Sistema de Monitoreo de Sesiones

## Introducción

El backend ahora incluye un sistema automático de monitoreo de sesiones de entrenamiento que maneja:
- Auto-pausa de sesiones inactivas (después de 20 minutos)
- Auto-abandono de sesiones muy largas (después de 24 horas)
- Gestión de estados de sesión (active, paused, auto_paused, completed, abandoned)

Esta guía explica cómo el frontend debe interactuar con este sistema para una experiencia de usuario óptima.

## Estados de Sesión

Es una nueva propiedad que se añadio a la sesion

El sistema maneja cinco estados posibles para las sesiones de entrenamiento:

| Estado | Descripción | Causa | 
|--------|-------------|-------|
| `active` | Sesión activa normal | Inicio manual, reanudación |
| `paused` | Pausa manual | Usuario pausa explícitamente |
| `auto_paused` | Pausa automática | Inactividad de 20+ minutos |
| `completed` | Finalizada correctamente | Usuario completa entrenamiento |
| `abandoned` | Abandonada/cancelada | Usuario abandona o inactividad de 24+ horas |

## Endpoints Relevantes

### 1. Actualización de Actividad

```http
POST /sessions/heartbeat
```

**Cuándo llamar**:
- ✅ Al navegar entre pantallas de la sesión activa
- ✅ Al interactuar con elementos críticos de la sesión
- ❌ NO llamar automáticamente cada 30 segundos (innecesario)

**Ejemplo de uso**:
```javascript
// Al registrar un ejercicio no es necesario llamar a heartbeat
// ya que los endpoints de logs automáticamente actualizan last_activity
const logExercise = async (exerciseData) => {
  await api.post('/sessions/logs/strength', exerciseData);
  // El endpoint ya actualizó last_activity
};

// Para otras interacciones ocasionales
const updateSessionActivity = async () => {
  try {
    await api.post('/sessions/heartbeat');
  } catch (error) {
    console.error('Error updating session activity:', error);
  }
};
```

### 2. Verificación de Estado

```http
GET /sessions/status
```

**Cuándo llamar**:
- ✅ Al iniciar/reabrir la aplicación
- ✅ Al volver de background (después de un tiempo)
- ✅ Después de reconexión de red

**Ejemplo de uso**:
```javascript
const checkSessionStatus = async () => {
  try {
    const response = await api.get('/sessions/status');
    
    if (response.data.has_active_session) {
      const session = response.data.session;
      
      // Manejar estado auto_paused
      if (session.status === 'auto_paused') {
        showResumeDialog();
      }
      
      // Actualizar UI según el estado
      updateSessionUI(session);
    }
  } catch (error) {
    console.error('Error checking session status:', error);
  }
};

// Verificar al iniciar app
useEffect(() => {
  checkSessionStatus();
}, []);

// Verificar al volver de background
useEffect(() => {
  const handleAppStateChange = (nextAppState) => {
    if (nextAppState === 'active') {
      checkSessionStatus();
    }
  };
  
  // React Native
  AppState.addEventListener('change', handleAppStateChange);
  
  return () => {
    AppState.removeEventListener('change', handleAppStateChange);
  };
}, []);
```

### 3. Control Manual de Estado

```http
POST /sessions/pause    // Pausar manualmente
POST /sessions/resume   // Reanudar sesión
POST /sessions/abandon  // Abandonar sin completar
POST /sessions/finish   // Finalizar completada
```

**Ejemplo de uso**:
```javascript
const pauseSession = async () => {
  await api.post('/sessions/pause');
  updateSessionUI({ status: 'paused' });
};

const resumeSession = async () => {
  await api.post('/sessions/resume');
  updateSessionUI({ status: 'active' });
};

const abandonSession = async () => {
  await api.post('/sessions/abandon');
  navigateToHome();
};

const finishSession = async () => {
  await api.post('/sessions/finish');
  navigateToSummary();
};
```

## Flujos de Usuario Recomendados

### 1. Gestión de Sesiones Auto-Pausadas

Cuando una sesión ha sido auto-pausada por inactividad, muestra un diálogo con opciones para que el usuario decida qué hacer:

```javascript
const handleAutoPausedSession = (session) => {
  showDialog({
    title: "Sesión Pausada",
    message: "Tu entrenamiento fue pausado automáticamente por inactividad",
    buttons: [
      {
        text: "Continuar",
        onPress: resumeSession
      },
      {
        text: "Finalizar",
        onPress: finishSession
      },
      {
        text: "Abandonar",
        onPress: abandonSession
      }
    ]
  });
};
```

### 2. Manejo de Transiciones de App

Implementa la siguiente lógica para manejar correctamente las transiciones:

```javascript
// React Native
const useSessionStateManager = () => {
  const [appState, setAppState] = useState(AppState.currentState);
  const [lastActiveTime, setLastActiveTime] = useState(Date.now());
  
  useEffect(() => {
    const handleAppStateChange = (nextAppState) => {
      if (appState === 'active' && nextAppState.match(/inactive|background/)) {
        // App va a background
        setLastActiveTime(Date.now());
      } else if (appState.match(/inactive|background/) && nextAppState === 'active') {
        // App vuelve a foreground
        const timeSinceLastActive = Date.now() - lastActiveTime;
        
        // Si pasaron más de 2 minutos, verificar estado
        if (timeSinceLastActive > 2 * 60 * 1000) {
          checkSessionStatus();
        }
      }
      
      setAppState(nextAppState);
    };
    
    AppState.addEventListener('change', handleAppStateChange);
    
    return () => {
      AppState.removeEventListener('change', handleAppStateChange);
    };
  }, [appState, lastActiveTime]);
};
```

### 3. Persistencia Local

Guarda información básica de la sesión localmente para recuperación en caso de cierre inesperado:

```javascript
// Guardar info básica al iniciar sesión
const saveSessionLocally = (session) => {
  AsyncStorage.setItem('active_session', JSON.stringify({
    id: session.id,
    name: session.name,
    start_time: session.session_start_time,
    last_saved: Date.now()
  }));
};

// Limpiar al finalizar
const clearLocalSession = () => {
  AsyncStorage.removeItem('active_session');
};

// Verificar al iniciar app
const checkLocalSession = async () => {
  const savedSession = await AsyncStorage.getItem('active_session');
  
  if (savedSession) {
    // Verificar en el servidor si sigue activa
    checkSessionStatus();
  }
};
```

## Preguntas Frecuentes

### ¿Debo enviar heartbeats periódicamente?

**No**. El backend está diseñado para no requerir heartbeats constantes. Solo debes:

1. **Registrar ejercicios normalmente**: Los endpoints `/logs/strength` y `/logs/cardio` actualizan automáticamente la actividad.
2. **Verificar estado**: Al abrir la app o volver de background.
3. **Controlar estado**: Pausar/reanudar/finalizar manualmente según interacción del usuario.
4. **Llamar a heartbeat**: Solo en interacciones importantes que no sean registrar ejercicios.

### ¿Qué pasa si el usuario cierra la app?

Si el usuario cierra la app por completo:
1. Después de 20 minutos sin actividad: La sesión se pausa automáticamente.
2. Al reabrir la app: Se detecta el estado auto_paused y se muestra un diálogo.

### ¿Qué debo mostrar cuando una sesión está auto-pausada?

Muestra un diálogo con tres opciones:
- **Continuar**: Llama a `/sessions/resume`
- **Finalizar**: Llama a `/sessions/finish`
- **Abandonar**: Llama a `/sessions/abandon`

### ¿Cómo manejar la reconexión después de pérdida de red?

Al detectar que la conexión se restauró:
```javascript
NetInfo.addEventListener(state => {
  if (state.isConnected && previouslyDisconnected) {
    checkSessionStatus();
  }
  previouslyDisconnected = !state.isConnected;
});
```

## Tiempos y Configuraciones

- **Auto-pausa**: Después de 20 minutos de inactividad
- **Auto-abandono**: Después de 24 horas desde el inicio
- **Verificación periódica**: El backend revisa cada 5 minutos

## Métricas de Tiempo Disponibles

El endpoint `/sessions/status` proporciona métricas útiles:

```json
{
  "session": {
    "session_duration_seconds": 3600,
    "total_pause_duration_seconds": 300,
    "time_since_last_activity_seconds": 120,
    "auto_pause_count": 1
  }
}
```

Utiliza estos valores para mostrar información relevante al usuario.

---

## Resumen de Integración

1. **Verifica** el estado de la sesión al iniciar la app y al volver de background.
2. **No envíes** heartbeats constantes, solo en interacciones significativas.
3. **Muestra** diálogos apropiados cuando una sesión ha sido auto-pausada.
4. **Guarda** información básica localmente para recuperación.
5. **Llama** a los endpoints correctos según las acciones del usuario.

Para más detalles técnicos, consulta la documentación completa de la API en `/docs/frontend/sessions_api.md`.
