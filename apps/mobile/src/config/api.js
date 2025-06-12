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
  
  // Chat
  CHAT: '/chat/',
  CHAT_HISTORY: '/chat/history',
};

// Configuración de los headers para las peticiones
export const API_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Tiempo de espera para las peticiones en milisegundos
export const API_TIMEOUT = 10000; // 10 segundos 