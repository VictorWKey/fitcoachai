# Guía de Integración Frontend - FitCoach AI

Esta guía proporciona toda la información necesaria para implementar correctamente el frontend de FitCoach AI, complementando la documentación específica de cada API con detalles técnicos, valores permitidos, consideraciones de arquitectura y mejores prácticas.

## 📋 Índice

1. [Configuración Inicial](#configuración-inicial)
2. [Autenticación y Seguridad](#autenticación-y-seguridad)
3. [Enumeraciones y Constantes](#enumeraciones-y-constantes)
4. [Gestión de Estado](#gestión-de-estado)
5. [Manejo de Errores](#manejo-de-errores)
6. [Optimización y Performance](#optimización-y-performance)
7. [Consideraciones UX/UI](#consideraciones-uxui)
8. [Validaciones Frontend](#validaciones-frontend)
9. [Internacionalización](#internacionalización)
10. [Testing](#testing)

---

## 🚀 Configuración Inicial

### URLs Base y Entornos

```typescript
const API_CONFIG = {
  development: {
    baseURL: 'http://localhost:8000',
    wsURL: 'ws://localhost:8000'
  },
  production: {
    baseURL: 'https://api.fitcoachai.com',
    wsURL: 'wss://api.fitcoachai.com'
  }
};
```

### Headers Requeridos

```typescript
const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'X-Client-Version': '1.0.0',
  'X-Platform': 'web' // o 'mobile', 'desktop'
};

// Para requests autenticados
const AUTHENTICATED_HEADERS = {
  ...DEFAULT_HEADERS,
  'Authorization': `Bearer ${accessToken}`
};
```

### CORS y Configuración

El backend está configurado para aceptar estos orígenes:
- `http://localhost:3000` (React/Next.js dev)
- `http://localhost:8080` (Vue.js dev)
- `http://localhost:4200` (Angular dev)
- `exp://` URLs para React Native/Expo

---

## 🔐 Autenticación y Seguridad

### Flujo de Tokens JWT

```typescript
interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_in: number; // 3600 segundos (1 hora)
}

interface UserProfile {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
}
```

### Gestión de Tokens

```typescript
class AuthManager {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private tokenExpiry: Date | null = null;

  // Almacenar tokens de forma segura
  setTokens(tokens: TokenResponse) {
    this.accessToken = tokens.access_token;
    this.refreshToken = tokens.refresh_token;
    this.tokenExpiry = new Date(Date.now() + tokens.expires_in * 1000);
    
    // En production, usar secure storage
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
  }

  // Verificar si el token necesita renovación
  needsRefresh(): boolean {
    if (!this.tokenExpiry) return true;
    // Renovar 5 minutos antes del vencimiento
    return Date.now() > (this.tokenExpiry.getTime() - 5 * 60 * 1000);
  }
}
```

### Rate Limiting

El backend implementa rate limiting:
- **General**: 100 requests por minuto por IP
- **Auth endpoints**: 10 requests por minuto por IP
- **Chat endpoint**: 30 requests por minuto por usuario

Implementa retry con exponential backoff para códigos 429.

### Bloqueo de Cuenta

```typescript
interface AccountLockInfo {
  failed_attempts: number;
  max_attempts: 5;
  lockout_duration: 15; // minutos
  account_locked_until?: string;
}
```

---

## 📊 Enumeraciones y Constantes

### Tipos de Programa de Entrenamiento

```typescript
enum ProgramType {
  HYPERTROPHY = "hypertrophy",  // Hipertrofia muscular
  STRENGTH = "strength",        // Desarrollo de fuerza
  PEAKING = "peaking"          // Pico para competencia
}

const PROGRAM_TYPE_LABELS = {
  [ProgramType.HYPERTROPHY]: "Hipertrofia",
  [ProgramType.STRENGTH]: "Fuerza",
  [ProgramType.PEAKING]: "Pico"
};

const PROGRAM_TYPE_DESCRIPTIONS = {
  [ProgramType.HYPERTROPHY]: "Enfocado en crecimiento muscular y volumen",
  [ProgramType.STRENGTH]: "Enfocado en desarrollo de fuerza máxima",
  [ProgramType.PEAKING]: "Enfocado en pico para competencia"
};
```

### Tipos de Bloques de Ejercicio

```typescript
enum BlockType {
  MAIN = "main",           // Ejercicios principales
  ACCESSORY = "accessory"  // Ejercicios accesorios
}

const BLOCK_TYPE_LABELS = {
  [BlockType.MAIN]: "Principal",
  [BlockType.ACCESSORY]: "Accesorio"
};
```

### Tipos de Carga

```typescript
enum LoadType {
  RPE = "rpe",           // Tasa de Esfuerzo Percibido (6-10)
  PERCENTAGE = "percentage", // Porcentaje de 1RM (30-100%)
  WEIGHT = "weight"      // Peso absoluto
}

const LOAD_TYPE_LABELS = {
  [LoadType.RPE]: "RPE",
  [LoadType.PERCENTAGE]: "% 1RM",
  [LoadType.WEIGHT]: "Peso"
};

// Rangos válidos para cada tipo de carga
const LOAD_RANGES = {
  [LoadType.RPE]: { min: 6, max: 10, step: 0.5 },
  [LoadType.PERCENTAGE]: { min: 30, max: 100, step: 5 },
  [LoadType.WEIGHT]: { min: 0, max: 999, step: 0.5 }
};
```

### Tipos de Serie

```typescript
enum SetType {
  STRENGTH = "strength",      // Series de fuerza (1-5 reps)
  HIPERTROPHY = "hypertrophy", // Series de hipertrofia (6-12 reps)
  TECHNIQUE = "technique"     // Series técnicas (>12 reps)
}

const SET_TYPE_LABELS = {
  [SetType.STRENGTH]: "Fuerza",
  [SetType.HIPERTROPHY]: "Hipertrofia",
  [SetType.TECHNIQUE]: "Técnica"
};
```

### Unidades de Medida

```typescript
enum WeightUnit {
  KG = "kg",
  LB = "lb"
}

enum DistanceUnit {
  KM = "km",
  MI = "mi"
}

enum CardioType {
  HIIT = "hiit",
  STEADY_STATE = "steady_state"
}

const UNIT_LABELS = {
  [WeightUnit.KG]: "Kilogramos",
  [WeightUnit.LB]: "Libras",
  [DistanceUnit.KM]: "Kilómetros",
  [DistanceUnit.MI]: "Millas"
};
```

### Grupos Musculares

```typescript
enum MuscleGroup {
  PECTORAL = "pectoral",
  ESPALDA = "espalda",
  BICEPS = "biceps",
  TRICEPS = "triceps",
  ABDOMEN = "abdomen",
  GLUTEO = "gluteo",
  CUADRICEPS = "cuadriceps",
  ADUCTOR = "aductor",
  ISQUIOTIBIALES = "isquiotibiales",
  PANTORRILLA = "pantorrilla",
  TRAPECIO = "trapecio",
  DELTOIDES_POSTERIOR = "hombro_posterior",
  DELTOIDES_MEDIO = "hombro_lateral",
  DELTOIDES_FRONTAL = "hombro_frontal",
  ANTEBRAZO = "antebrazo",
  CORE = "core",
  OBLICUOS = "oblicuos",
  ZONA_LUMBAR = "zona_lumbar",
  CUELLO = "cuello"
}

enum EquipmentType {
  BARRA = "barra",
  MANCUERNAS = "mancuernas",
  MAQUINA = "maquina",
  POLEAS = "poleas",
  PESO_CORPORAL = "peso_corporal",
  DISCOS = "discos"
}

enum ExerciseType {
  COMPUESTO = "compuesto",
  AISLADO = "aislado"
}
```

---

## 🔄 Gestión de Estado

### Estado Global Recomendado

```typescript
interface AppState {
  auth: {
    user: UserProfile | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    tokens: TokenResponse | null;
  };
  training: {
    activeProgram: TrainingProgram | null;
    activeSession: TrainingSession | null;
    currentWorkout: Workout | null;
    exerciseHistory: ExerciseLog[];
  };
  chat: {
    messages: ChatMessage[];
    isTyping: boolean;
    sessionId: string | null;
  };
  ui: {
    theme: 'light' | 'dark';
    language: 'es' | 'en';
    notifications: Notification[];
    isOffline: boolean;
  };
  cache: {
    exercises: StandardExercise[];
    lastSync: Date | null;
  };
}
```

### Persistencia Local

```typescript
const STORAGE_KEYS = {
  AUTH_TOKENS: 'fitcoach_auth_tokens',
  USER_PROFILE: 'fitcoach_user_profile',
  ACTIVE_WORKOUT: 'fitcoach_active_workout',
  EXERCISE_CACHE: 'fitcoach_exercise_cache',
  APP_SETTINGS: 'fitcoach_app_settings'
};

class StateManager {
  // Guardar estado crítico localmente
  persistCriticalState(state: Partial<AppState>) {
    if (state.training?.currentWorkout) {
      localStorage.setItem(
        STORAGE_KEYS.ACTIVE_WORKOUT, 
        JSON.stringify(state.training.currentWorkout)
      );
    }
  }

  // Recuperar estado al inicializar
  hydrateCriticalState(): Partial<AppState> {
    const savedWorkout = localStorage.getItem(STORAGE_KEYS.ACTIVE_WORKOUT);
    return {
      training: {
        currentWorkout: savedWorkout ? JSON.parse(savedWorkout) : null
      }
    };
  }
}
```

---

## ⚠️ Manejo de Errores

### Códigos de Error Comunes

```typescript
enum ErrorCode {
  // Auth Errors
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  EMAIL_NOT_VERIFIED = 'EMAIL_NOT_VERIFIED',
  ACCOUNT_LOCKED = 'ACCOUNT_LOCKED',
  
  // Validation Errors
  INVALID_INPUT = 'INVALID_INPUT',
  MISSING_REQUIRED_FIELD = 'MISSING_REQUIRED_FIELD',
  
  // Business Logic Errors
  SESSION_ALREADY_ACTIVE = 'SESSION_ALREADY_ACTIVE',
  EXERCISE_NOT_FOUND = 'EXERCISE_NOT_FOUND',
  PROGRAM_NOT_FOUND = 'PROGRAM_NOT_FOUND',
  
  // System Errors
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',
  SERVER_ERROR = 'SERVER_ERROR',
  NETWORK_ERROR = 'NETWORK_ERROR'
}

interface ApiError {
  detail: string;
  code?: ErrorCode;
  field?: string;
  context?: Record<string, any>;
}
```

### Error Handler Global

```typescript
class ErrorHandler {
  static handle(error: any): UserFriendlyError {
    if (error.response?.status === 401) {
      return {
        title: "Sesión Expirada",
        message: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.",
        action: "redirect_to_login"
      };
    }

    if (error.response?.status === 429) {
      return {
        title: "Demasiadas Solicitudes",
        message: "Has excedido el límite de solicitudes. Intenta nuevamente en unos minutos.",
        action: "retry_later"
      };
    }

    if (error.response?.status === 403 && error.response?.data?.detail?.includes('not verified')) {
      return {
        title: "Email No Verificado",
        message: "Debes verificar tu email antes de continuar.",
        action: "show_verification_prompt"
      };
    }

    // Error genérico
    return {
      title: "Error Inesperado",
      message: "Ha ocurrido un error. Por favor, intenta nuevamente.",
      action: "retry"
    };
  }
}
```

---

## ⚡ Optimización y Performance

### Caché y Sincronización

```typescript
class CacheManager {
  private exerciseCache = new Map<number, StandardExercise>();
  private cacheExpiry = 24 * 60 * 60 * 1000; // 24 horas

  async getExercise(id: number): Promise<StandardExercise> {
    // Verificar caché local primero
    const cached = this.exerciseCache.get(id);
    if (cached && this.isCacheValid(cached.cached_at)) {
      return cached;
    }

    // Fetch desde API si no está en caché
    const exercise = await api.exercises.getById(id);
    exercise.cached_at = Date.now();
    this.exerciseCache.set(id, exercise);
    
    return exercise;
  }

  // Pre-cargar ejercicios comunes
  async preloadCommonExercises() {
    const commonExerciseIds = [1, 2, 3, 4, 5]; // IDs más usados
    await Promise.all(
      commonExerciseIds.map(id => this.getExercise(id))
    );
  }
}
```

### Paginación y Lazy Loading

```typescript
interface PaginationParams {
  page: number;
  limit: number;
  offset?: number;
}

const PAGINATION_DEFAULTS = {
  exercises: { limit: 20 },
  chatHistory: { limit: 50 },
  workoutHistory: { limit: 10 }
};

class DataLoader {
  async loadExerciseHistory(
    params: PaginationParams = PAGINATION_DEFAULTS.exercises
  ) {
    const { page, limit } = params;
    const offset = (page - 1) * limit;
    
    return api.exercises.getRecent({ limit, offset });
  }
}
```

---

## 🎨 Consideraciones UX/UI

### Estados de Carga

```typescript
interface LoadingState {
  isLoading: boolean;
  loadingMessage?: string;
  progress?: number; // 0-100
}

const LOADING_MESSAGES = {
  login: "Iniciando sesión...",
  saving_workout: "Guardando entrenamiento...",
  generating_program: "Generando programa con IA...",
  uploading_data: "Sincronizando datos..."
};
```

### Feedback Visual

```typescript
interface NotificationConfig {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number; // ms
  persistent?: boolean;
}

const NOTIFICATION_PRESETS = {
  workout_saved: {
    type: 'success',
    title: '¡Entrenamiento Guardado!',
    message: 'Tu progreso ha sido registrado correctamente.',
    duration: 3000
  },
  session_started: {
    type: 'info',
    title: 'Sesión Iniciada',
    message: 'Tu entrenamiento ha comenzado. ¡Dale todo!',
    duration: 2000
  }
};
```

### Offline Support

```typescript
class OfflineManager {
  private pendingActions: OfflineAction[] = [];

  // Detectar cambio de conexión
  setupOfflineDetection() {
    window.addEventListener('online', this.syncPendingActions);
    window.addEventListener('offline', this.handleOfflineMode);
  }

  // Guardar acciones para sincronizar después
  queueAction(action: OfflineAction) {
    this.pendingActions.push({
      ...action,
      timestamp: Date.now(),
      id: generateUniqueId()
    });
    
    localStorage.setItem('pending_actions', JSON.stringify(this.pendingActions));
  }

  // Sincronizar cuando vuelva la conexión
  async syncPendingActions() {
    for (const action of this.pendingActions) {
      try {
        await this.executeAction(action);
        this.removePendingAction(action.id);
      } catch (error) {
        console.error('Failed to sync action:', action, error);
      }
    }
  }
}
```

---

## ✅ Validaciones Frontend

### Validaciones de Input

```typescript
const VALIDATION_RULES = {
  username: {
    required: true,
    minLength: 3,
    maxLength: 30,
    pattern: /^[a-zA-Z0-9_]+$/,
    message: "Username debe tener 3-30 caracteres alfanuméricos"
  },
  
  email: {
    required: true,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: "Email debe tener formato válido"
  },
  
  password: {
    required: true,
    minLength: 8,
    pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]+$/,
    message: "Password debe tener al menos 8 caracteres con letras y números"
  },
  
  weight: {
    required: true,
    min: 0.5,
    max: 999,
    step: 0.5,
    message: "Peso debe estar entre 0.5 y 999 kg"
  },
  
  reps: {
    required: true,
    min: 1,
    max: 100,
    message: "Repeticiones deben estar entre 1 y 100"
  },
  
  rpe: {
    required: false,
    min: 6,
    max: 10,
    step: 0.5,
    message: "RPE debe estar entre 6 y 10"
  },
  
  rir: {
    required: false,
    min: 0,
    max: 10,
    message: "RIR debe estar entre 0 y 10"
  }
};

class Validator {
  static validateExerciseLog(data: Partial<StrengthLogCreate>): ValidationResult {
    const errors: ValidationError[] = [];

    // Validar campos requeridos
    if (!data.exercise_name) {
      errors.push({ field: 'exercise_name', message: 'Nombre del ejercicio es requerido' });
    }

    if (!data.repetitions_done || data.repetitions_done < 1) {
      errors.push({ field: 'repetitions_done', message: 'Repeticiones debe ser al menos 1' });
    }

    // Validar coherencia entre RPE y RIR
    if (data.perceived_rpe && data.perceived_rir) {
      if (data.perceived_rpe >= 9 && data.perceived_rir > 2) {
        errors.push({ 
          field: 'perceived_rir', 
          message: 'RIR inconsistente con RPE alto' 
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }
}
```

### Validaciones de Tempo

```typescript
const TEMPO_PATTERNS = {
  basic: /^\d-\d-\d-\d$/, // e.g., "2-1-2-1"
  advanced: /^\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}$/ // e.g., "10-1-3-1"
};

class TempoValidator {
  static validate(tempo: string): boolean {
    if (!tempo) return true; // Tempo es opcional
    
    return TEMPO_PATTERNS.basic.test(tempo) || TEMPO_PATTERNS.advanced.test(tempo);
  }

  static parse(tempo: string): TempoPhases | null {
    if (!this.validate(tempo)) return null;
    
    const [eccentric, pause1, concentric, pause2] = tempo.split('-').map(Number);
    
    return {
      eccentric,    // Fase excéntrica (bajada)
      pause1,       // Pausa en posición inferior
      concentric,   // Fase concéntrica (subida)
      pause2        // Pausa en posición superior
    };
  }
}
```

---

## 🌍 Internacionalización

### Estructura de Traducciones

```typescript
const TRANSLATIONS = {
  es: {
    common: {
      save: "Guardar",
      cancel: "Cancelar",
      delete: "Eliminar",
      edit: "Editar",
      loading: "Cargando..."
    },
    auth: {
      login: "Iniciar Sesión",
      register: "Registrarse",
      logout: "Cerrar Sesión",
      forgot_password: "¿Olvidaste tu contraseña?"
    },
    exercises: {
      weight: "Peso",
      reps: "Repeticiones",
      sets: "Series",
      rest: "Descanso",
      rpe: "Esfuerzo Percibido (RPE)",
      rir: "Repeticiones en Reserva (RIR)"
    },
    programs: {
      hypertrophy: "Hipertrofia",
      strength: "Fuerza",
      peaking: "Pico",
      week: "Semana",
      session: "Sesión"
    }
  },
  en: {
    // English translations...
  }
};
```

### Formateo de Fechas y Números

```typescript
class LocaleFormatter {
  private locale: string;

  constructor(locale: string = 'es-ES') {
    this.locale = locale;
  }

  formatDate(date: Date | string): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(this.locale, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(dateObj);
  }

  formatTime(date: Date | string): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(this.locale, {
      hour: '2-digit',
      minute: '2-digit'
    }).format(dateObj);
  }

  formatWeight(weight: number, unit: WeightUnit): string {
    return `${weight.toFixed(1)} ${unit}`;
  }

  formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
}
```

---

## 🧪 Testing

### Test Utilities

```typescript
// Mock API responses
const mockApiResponses = {
  auth: {
    login: {
      access_token: "mock_access_token",
      refresh_token: "mock_refresh_token",
      token_type: "bearer",
      expires_in: 3600
    }
  },
  exercises: {
    recent: [
      {
        exercise_name: "Press de banca",
        type: "strength",
        exercise_date: "2025-01-20T10:30:00",
        set_number: 3,
        reps: 10,
        weight: 80.0,
        weight_unit: "kg"
      }
    ]
  }
};

// Test helpers
class TestHelpers {
  static createMockUser(): UserProfile {
    return {
      id: 1,
      username: "testuser",
      email: "test@example.com",
      full_name: "Test User",
      is_active: true,
      is_verified: true,
      created_at: new Date().toISOString()
    };
  }

  static createMockWorkout(): Workout {
    return {
      id: 1,
      user_id: 1,
      name: "Test Workout",
      start_time: new Date().toISOString(),
      is_finished: false
    };
  }
}
```

### Integration Test Scenarios

```typescript
describe('Workout Flow Integration', () => {
  test('Complete workout session', async () => {
    // 1. Login
    await authService.login('testuser', 'password123');
    
    // 2. Start session
    const session = await sessionsService.start(1);
    expect(session.is_active).toBe(true);
    
    // 3. Log exercises
    const exerciseLog = await exercisesService.logStrength({
      exercise_name: "Press de banca",
      repetitions_done: 10,
      used_weight: 80,
      used_weight_unit: "kg"
    });
    expect(exerciseLog.id).toBeDefined();
    
    // 4. Finish session
    const finishedSession = await sessionsService.finish();
    expect(finishedSession.is_finished).toBe(true);
  });
});
```

---

## 📱 Consideraciones Mobile-Specific

### React Native / Expo

```typescript
// Detección de plataforma
import { Platform } from 'react-native';

const API_CONFIG = {
  ...baseConfig,
  timeout: Platform.OS === 'ios' ? 10000 : 15000,
  headers: {
    ...DEFAULT_HEADERS,
    'X-Platform': Platform.OS
  }
};

// Manejo de deep links
const DEEP_LINK_PATTERNS = {
  workout: /fitcoach:\/\/workout\/(\d+)/,
  exercise: /fitcoach:\/\/exercise\/(\d+)/,
  program: /fitcoach:\/\/program\/(\d+)/
};
```

### PWA Support

```typescript
// Service Worker para caché
const CACHE_STRATEGIES = {
  api: 'networkFirst',
  static: 'cacheFirst',
  images: 'staleWhileRevalidate'
};

// Manifest.json
const PWA_MANIFEST = {
  name: "FitCoach AI",
  short_name: "FitCoach",
  theme_color: "#1976d2",
  background_color: "#ffffff",
  display: "standalone",
  start_url: "/",
  icons: [
    {
      src: "/icon-192.png",
      sizes: "192x192",
      type: "image/png"
    }
  ]
};
```

---

## 🔧 Herramientas de Desarrollo

### Debug Tools

```typescript
class DebugTools {
  static enableApiLogging() {
    if (process.env.NODE_ENV === 'development') {
      window.FitCoachDebug = {
        logApiCalls: true,
        logStateChanges: true,
        mockOfflineMode: false
      };
    }
  }

  static logApiCall(method: string, url: string, data?: any) {
    if (window.FitCoachDebug?.logApiCalls) {
      console.group(`🌐 API Call: ${method} ${url}`);
      if (data) console.log('Data:', data);
      console.groupEnd();
    }
  }
}
```

### Environment Variables

```bash
# .env.development
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENABLE_DEBUG=true
REACT_APP_MOCK_API=false

# .env.production
REACT_APP_API_BASE_URL=https://api.fitcoachai.com
REACT_APP_WS_URL=wss://api.fitcoachai.com
REACT_APP_ENABLE_DEBUG=false
REACT_APP_MOCK_API=false
```

---

## 📚 Recursos Adicionales

### Documentación de APIs
- [Auth API](./auth_api.md)
- [Chat API](./chat_api.md)
- [Exercises API](./exercises_api.md)
- [Sessions API](./sessions_api.md)
- [Training Program API](./training_program_api.md)

### Ejemplos de Implementación
- [React Example App](../examples/react/)
- [React Native Example](../examples/react-native/)
- [Vue.js Example](../examples/vue/)

### Bibliotecas Recomendadas
- **HTTP Client**: Axios, Fetch API
- **State Management**: Redux Toolkit, Zustand, React Query
- **Forms**: React Hook Form, Formik
- **UI Components**: Material-UI, Chakra UI, React Native Elements
- **Charts**: Chart.js, Recharts, Victory Native

---

## 🔄 Changelog

### v1.0.0 (2025-07-21)
- Versión inicial de la guía de integración
- Documentación completa de enums y constantes
- Patrones de manejo de errores
- Consideraciones de performance y UX

---

**¿Necesitas ayuda adicional?** 

Consulta la documentación específica de cada API o contacta al equipo de desarrollo para obtener soporte técnico adicional.
