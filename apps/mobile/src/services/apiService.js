import axios from 'axios';
// Importar SecureStore de expo-secure-store
import * as SecureStore from 'expo-secure-store';

// Funciones de ayuda para SecureStore
const saveSecureValue = async (key, value) => {
  try {
    await SecureStore.setItemAsync(key, value);
    return true;
  } catch (error) {
    console.error('Error al guardar en SecureStore:', error);
    return false;
  }
};

const getSecureValue = async (key) => {
  try {
    return await SecureStore.getItemAsync(key);
  } catch (error) {
    console.error('Error al leer de SecureStore:', error);
    return null;
  }
};

const deleteSecureValue = async (key) => {
  try {
    await SecureStore.deleteItemAsync(key);
    return true;
  } catch (error) {
    console.error('Error al eliminar de SecureStore:', error);
    return false;
  }
};

// Verificar si SecureStore está disponible
const isSecureStoreAvailable = async () => {
  try {
    return await SecureStore.isAvailableAsync();
  } catch (error) {
    console.error('Error verificando disponibilidad de SecureStore:', error);
    return false;
  }
};

import { API_BASE_URL, API_HEADERS, API_TIMEOUT, API_ENDPOINTS } from '../config/api';

// Crear instancia de axios con la configuración base
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: API_HEADERS,
});

// =======================
//  ACCESS TOKEN IN MEMORY
// =======================
let accessTokenMemory = null;
const setAccessToken = (token) => { accessTokenMemory = token; };
const getAccessTokenMem = () => accessTokenMemory;

// Interceptor para añadir el token de autenticación a las peticiones
apiClient.interceptors.request.use(
  async (config) => {
    // Evitar enviar el token en las rutas de autenticación que no lo necesitan
    if (config.url && (config.url.includes(API_ENDPOINTS.LOGIN) || config.url.includes(API_ENDPOINTS.REGISTER))) {
      return config; // No agregar autorización
    }
    const token = getAccessTokenMem();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para manejar errores de autenticación (401)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url.includes('/auth/refresh')) {
        setAccessToken(null);
        await deleteSecureValue('refreshToken');
        return Promise.reject(error);
      }
      originalRequest._retry = true;
      try {
        const refreshToken = await getSecureValue('refreshToken');
        if (!refreshToken) throw new Error('No refresh token');
        const response = await axios.post(
          `${API_BASE_URL}${API_ENDPOINTS.REFRESH_TOKEN}`,
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );
        const { access_token, refresh_token } = response.data;
        setAccessToken(access_token);
        if (refresh_token) await saveSecureValue('refreshToken', refresh_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        setAccessToken(null);
        await deleteSecureValue('refreshToken');
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Servicios de autenticación
export const authService = {
  // Iniciar sesión
  login: async ({ username, password }) => {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      const response = await apiClient.post(API_ENDPOINTS.LOGIN, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const { access_token, refresh_token } = response.data;
      setAccessToken(access_token);
      await saveSecureValue('refreshToken', refresh_token);
      return response.data;
    } catch (error) {
      console.error('Error en login:', error.response?.data || error.message);
      throw error;
    }
  },

  // Registrar usuario
  register: async (userData) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.REGISTER, userData);
      return response.data;
    } catch (error) {
      console.error('Error en registro:', error.response?.data || error.message);
      throw error;
    }
  },

  // Cerrar sesión
  logout: async () => {
    try {
      const refreshToken = await getSecureValue('refreshToken');
      await apiClient.post(API_ENDPOINTS.LOGOUT, { refresh_token: refreshToken });
    } catch (error) {
      console.error('Error en logout:', error.response?.data || error.message);
      // Ignorar
    } finally {
      setAccessToken(null);
      await deleteSecureValue('refreshToken');
    }
  },

  // Verificar si el usuario está autenticado
  isAuthenticated: async () => {
    try {
      if (getAccessTokenMem()) {
        const tokenPayload = JSON.parse(atob(getAccessTokenMem().split('.')[1]));
        const now = Math.floor(Date.now() / 1000);
        if (tokenPayload.exp && tokenPayload.exp > now + 300) return true;
      }
      // Intentar refrescar con refresh token
      const refreshToken = await getSecureValue('refreshToken');
      if (!refreshToken) return false;
      try {
        const response = await axios.post(
          `${API_BASE_URL}${API_ENDPOINTS.REFRESH_TOKEN}`, 
          { 
            refresh_token: refreshToken 
          }
        );
        const { access_token, refresh_token } = response.data;
        setAccessToken(access_token);
        if (refresh_token) await saveSecureValue('refreshToken', refresh_token);
        return true;
      } catch {
        await deleteSecureValue('refreshToken');
        return false;
      }
    } catch (e) {
      console.error('Error al verificar autenticación:', e);
      return false;
    }
  },
};

// Servicios de chat
export const chatService = {
  // Enviar mensaje al chat
  sendMessage: async (message) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.CHAT, {
        input: message,
      });
      return response.data; // { id, role:"assistant", content }
    } catch (error) {
      console.error('Error al enviar mensaje:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener historial de chat (incremental)
  getHistory: async (afterId = 0, limit = 50) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.CHAT_HISTORY, {
        params: { after_id: afterId, limit },
      });
      return response.data; // array de mensajes
    } catch (error) {
      console.error('Error al obtener historial:', error.response?.data || error.message);
      throw error;
    }
  },
};

export default apiClient; 