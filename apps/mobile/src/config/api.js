import { Platform } from 'react-native';

// Función para obtener la URL base según la plataforma
const getApiBaseUrl = () => {
  // Si estamos en desarrollo (__DEV__ es true)
  if (__DEV__) {
    // Para Android Emulator
    if (Platform.OS === 'android') {
      return 'http://10.0.2.2:8000';
    }
    // Para iOS Simulator
    if (Platform.OS === 'ios') {
      return 'http://localhost:8000';
    }
    // Para web
    return 'http://localhost:8000';
  }

  // En producción, usa la URL de tu API en producción
  return 'https://api.fitcoachai.com';
};

console.log(getApiBaseUrl());
export const API_BASE_URL = getApiBaseUrl();

// Rate limits según el frontend integration guide
export const RATE_LIMITS = {
  GENERAL: 100, // requests per minute
  AUTH: 10,     // requests per minute
  CHAT: 30      // requests per minute
};

// Endpoints de la API
export const API_ENDPOINTS = {
  // Autenticación
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  REFRESH_TOKEN: '/auth/refresh',
  LOGOUT: '/auth/logout',
  VERIFY_EMAIL: '/auth/verify-email',
  FORGOT_PASSWORD: '/auth/forgot-password',
  RESET_PASSWORD: '/auth/reset-password',
  VERIFY_RESET_TOKEN: '/auth/reset-password/verify',
  RESEND_VERIFICATION: '/auth/resend-verification',

  // Chat
  CHAT: '/chat/',
  CHAT_HISTORY: '/chat/history',

  // Training Programs
  TRAINING_PROGRAMS: '/training-programs/',
  TRAINING_PROGRAM_BY_ID: (id) => `/training-programs/${id}`,
  TRAINING_PROGRAM_PROGRESS: (id) => `/training-programs/${id}/progress`,
  TRAINING_PROGRAM_CLONE: (id) => `/training-programs/${id}/clone`,
  TRAINING_PROGRAM_SESSIONS: (programId) => `/training-programs/${programId}/sessions`,
  TRAINING_PROGRAM_WEEK_DETAILS: (programId, weekNumber) => `/training-programs/${programId}/weeks/${weekNumber}`,

  // Sessions
  SESSIONS_START: (sessionId) => `/sessions/start/${sessionId}`,
  SESSIONS_FINISH: '/sessions/finish',
  SESSIONS_ACTIVE: '/sessions/active',
  SESSIONS_STATUS: '/sessions/status',   // Nuevo endpoint para verificar estado
  SESSIONS_HEARTBEAT: '/sessions/heartbeat',  // Nuevo endpoint para actualizar actividad
  SESSIONS_PAUSE: '/sessions/pause',     // Nuevo endpoint para pausar manualmente
  SESSIONS_RESUME: '/sessions/resume',   // Nuevo endpoint para reanudar sesión
  SESSIONS_ABANDON: '/sessions/abandon', // Nuevo endpoint para abandonar sesión
  SESSIONS_HISTORY: '/sessions/history',
  SESSIONS_BY_ID: (sessionId) => `/sessions/${sessionId}`,
  SESSIONS_LOGS: '/sessions/logs',
  SESSIONS_LOGS_STRENGTH: '/sessions/logs/strength',
  SESSIONS_LOGS_CARDIO: '/sessions/logs/cardio',
  SESSIONS_LOGS_EXERCISE_PROGRESS: (exerciseId) => `/sessions/logs/exercise/${exerciseId}/progress`,

  // Exercises
  EXERCISES_RECENT: '/exercises/recent',
  EXERCISES_POPULAR: '/exercises/popular',
  EXERCISES_STATS: '/exercises/stats',
  EXERCISES_SEARCH: '/exercises/search',
  EXERCISES_PROGRESS: (exerciseName) => `/exercises/progress/${exerciseName}`,
  EXERCISES_CATALOG: '/exercises/catalog',
  EXERCISES_STANDARD: '/exercises/standard'
};

// Configuración de los headers para las peticiones según el frontend integration guide
export const API_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'X-Platform': Platform.OS,
  'X-App-Version': '1.0.0',
};

// Tiempo de espera para las peticiones en milisegundos (específico por plataforma)
export const API_TIMEOUT = Platform.OS === 'ios' ? 10000 : 15000; 