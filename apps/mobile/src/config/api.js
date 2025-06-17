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
  return 'https://tu-api-produccion.com';
};

console.log(getApiBaseUrl());
export const API_BASE_URL = getApiBaseUrl();

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

  // Workouts
  WORKOUTS: '/workouts/',
  WORKOUT_ACTIVE: '/workouts/active',
  WORKOUT_BY_ID: (id) => `/workouts/${id}`,
  WORKOUT_FINISH: (id) => `/workouts/${id}/finish`,
  WORKOUT_EXERCISES: (id) => `/workouts/${id}/exercises`,
  WORKOUT_EXERCISE_BY_ID: (workoutId, exerciseId) => `/workouts/${workoutId}/exercises/${exerciseId}`,

  // Exercises
  EXERCISES_RECENT: '/exercises/recent',
  EXERCISES_POPULAR: '/exercises/popular',
  EXERCISES_STATS: '/exercises/stats',
  EXERCISES_SEARCH: '/exercises/search',
  EXERCISES_PROGRESS: (exerciseName) => `/exercises/progress/${exerciseName}`,
  EXERCISES_CATALOG: '/exercises/catalog'
};

// Configuración de los headers para las peticiones
export const API_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Tiempo de espera para las peticiones en milisegundos
export const API_TIMEOUT = 10000; // 10 segundos 