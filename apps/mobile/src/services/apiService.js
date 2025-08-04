import axios from 'axios';
// Importar SecureStore de expo-secure-store
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import { ApiError, ErrorCode, RATE_LIMITS } from '../types/api';

// Funciones de ayuda para SecureStore
const saveSecureValue = async (key, value) => {
  try {
    console.log(`🔐 Guardando ${key} en SecureStore`);
    if (!value) {
      console.warn(`⚠️ Intento de guardar valor vacío para ${key}`);
      return false;
    }
    
    const available = await isSecureStoreAvailable();
    if (!available) {
      console.error('❌ SecureStore no está disponible en este dispositivo');
      return false;
    }
    
    await SecureStore.setItemAsync(key, value);
    console.log(`✅ ${key} guardado correctamente`);
    return true;
  } catch (error) {
    console.error(`❌ Error al guardar ${key} en SecureStore:`, error);
    return false;
  }
};

const getSecureValue = async (key) => {
  try {
    console.log(`🔐 Leyendo ${key} de SecureStore`);
    const available = await isSecureStoreAvailable();
    if (!available) {
      console.error('❌ SecureStore no está disponible en este dispositivo');
      return null;
    }
    
    const value = await SecureStore.getItemAsync(key);
    console.log(`${key} encontrado: ${value ? '✅ Sí' : '❌ No'}`);
    return value;
  } catch (error) {
    console.error(`❌ Error al leer ${key} de SecureStore:`, error);
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

// Crear instancia de axios con la configuración base según plataforma
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: Platform.OS === 'ios' ? 10000 : 15000, // iOS timeout más corto
  headers: {
    ...API_HEADERS,
    'X-Platform': Platform.OS,
    'X-App-Version': '1.0.0'
  },
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

// Interceptor para manejar errores de autenticación (401) y otros errores
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // Manejo específico de errores según el frontend integration guide
    if (error.response?.status === 401 && !originalRequest._retry) {
      console.log('🔄 Token expirado, intentando refresh...');
      
      if (originalRequest.url.includes('/auth/refresh')) {
        console.error('❌ Error refrescando token - endpoint de refresh falló');
        // No borrar el token aquí para evitar borrados prematuros
        // Propagar error pero no intentar refresh de nuevo
        throw ApiError.fromResponse(error);
      }
      
      originalRequest._retry = true;
      let refreshToken = null;
      
      try {
        // Guardar el refresh token en una variable primero antes de cualquier operación
        refreshToken = await getSecureValue('refreshToken');
        console.log(`🔑 Refresh token encontrado: ${refreshToken ? 'Sí' : 'No'}`);
        
        if (!refreshToken) {
          console.error('❌ No se encontró refresh token');
          throw new ApiError(ErrorCode.TOKEN_EXPIRED, 'No refresh token');
        }
        
        console.log('🔄 Enviando solicitud de refresh...');
        const response = await axios.post(
          `${API_BASE_URL}${API_ENDPOINTS.REFRESH_TOKEN}`,
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );
        
        console.log('✅ Refresh exitoso, procesando nuevos tokens');
        const { access_token, refresh_token } = response.data;
        
        // Primero establecer el token en memoria antes de cualquier operación que pueda fallar
        if (!access_token) {
          console.error('❌ No se recibió access token del servidor');
          throw new Error('No se recibió access token del servidor');
        }
        
        setAccessToken(access_token);
        console.log('✅ Nuevo access token establecido en memoria');
        
        // Guardar el nuevo refresh token solo si recibimos uno válido
        if (refresh_token) {
          try {
            const saved = await saveSecureValue('refreshToken', refresh_token);
            console.log(`✅ Nuevo refresh token guardado: ${saved ? 'Sí' : 'No'}`);
            
            // Verificar que se guardó correctamente pero no fallar si no se puede verificar
            try {
              const storedToken = await getSecureValue('refreshToken');
              console.log(`✅ Verificación de nuevo refresh token: ${storedToken ? 'Presente' : 'Ausente'}`);
            } catch (verifyError) {
              console.warn('⚠️ No se pudo verificar el token guardado:', verifyError);
              // Continuar aunque no se pueda verificar
            }
          } catch (saveError) {
            console.error('❌ Error al guardar nuevo refresh token:', saveError);
            // Continuar a pesar del error de guardado, ya que el token de acceso está en memoria
          }
        } else {
          console.warn('⚠️ No se recibió un nuevo refresh token del servidor, manteniendo el actual');
          // No borrar el token actual si no recibimos uno nuevo
        }
        
        // Establecer el nuevo token en la solicitud original
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        console.error('❌ Error en el proceso de refresh:', refreshError);
        
        // Solo limpiar tokens si es un error de autenticación real y no hay posibilidad de recuperación
        if (refreshError.response?.status === 401) {
          console.log('🧹 Limpiando tokens debido a error 401 en refresh');
          setAccessToken(null);
          // Registrar estado antes de borrar
          const tokenBeforeDelete = await getSecureValue('refreshToken');
          console.log(`⚠️ Estado del token antes de borrar: ${tokenBeforeDelete ? 'Presente' : 'Ausente'}`);
          
          await deleteSecureValue('refreshToken');
          
          // Verificar borrado
          const tokenAfterDelete = await getSecureValue('refreshToken');
          console.log(`⚠️ Estado del token después de borrar: ${tokenAfterDelete ? 'Aún presente' : 'Eliminado correctamente'}`);
        } else {
          console.warn('⚠️ Error no relacionado con autenticación, manteniendo tokens');
        }
        
        throw ApiError.fromResponse(refreshError);
      }
    }
    
    // Lanzar ApiError personalizado para todos los demás errores
    throw ApiError.fromResponse(error);
  }
);

// Servicios de autenticación
export const authService = {
  // Iniciar sesión
  login: async ({ username, password }) => {
    try {
      console.log('🔑 Iniciando proceso de login...');
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      // Limpiar cualquier token existente antes de iniciar sesión
      setAccessToken(null);
      
      // Verificar el estado del refresh token antes de borrarlo
      try {
        const currentToken = await getSecureValue('refreshToken');
        if (currentToken) {
          console.log('🧹 Limpiando refresh token anterior antes de login');
          await deleteSecureValue('refreshToken');
        }
      } catch (tokenError) {
        console.warn('⚠️ Error al verificar token existente:', tokenError);
        // Continuar con el proceso de login
      }
      
      const response = await apiClient.post(API_ENDPOINTS.LOGIN, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      const { access_token, refresh_token } = response.data;
      console.log('✅ Login exitoso, procesando tokens');
      
      // Verificar y guardar el token de acceso en memoria
      if (!access_token) {
        console.error('❌ No se recibió access token del servidor');
        throw new Error('No se recibió access token del servidor');
      }
      
      setAccessToken(access_token);
      console.log('✅ Access token guardado en memoria');
      
      // Guardar el refresh token en SecureStore
      if (refresh_token) {
        try {
          console.log('📝 Guardando refresh token en SecureStore...');
          const saved = await saveSecureValue('refreshToken', refresh_token);
          console.log(`✅ Refresh token guardado: ${saved ? 'Sí' : 'No'}`);
          
          // Verificación adicional
          try {
            const storedToken = await getSecureValue('refreshToken');
            console.log(`✅ Verificación de refresh token: ${storedToken ? 'Presente' : 'Ausente'}`);
            
            if (!storedToken) {
              console.error('⚠️ Advertencia: El refresh token no se guardó correctamente');
              // Intentar guardar nuevamente
              console.log('🔄 Intentando guardar el refresh token nuevamente...');
              await saveSecureValue('refreshToken', refresh_token);
              
              // Verificar segunda vez
              const secondCheck = await getSecureValue('refreshToken');
              console.log(`✅ Segunda verificación: ${secondCheck ? 'Exitosa' : 'Fallida'}`);
            }
          } catch (verifyError) {
            console.error('❌ Error al verificar refresh token guardado:', verifyError);
            // Intentar guardar en un segundo intento
            try {
              console.log('🔄 Intentando guardar el refresh token nuevamente después de error...');
              await saveSecureValue('refreshToken', refresh_token);
            } catch (secondSaveError) {
              console.error('❌❌ Error crítico al guardar refresh token en segundo intento:', secondSaveError);
            }
          }
        } catch (saveError) {
          console.error('❌ Error al guardar refresh token:', saveError);
          // Intentar guardar en un segundo intento
          try {
            console.log('🔄 Intentando guardar el refresh token nuevamente después de error...');
            await saveSecureValue('refreshToken', refresh_token);
          } catch (secondSaveError) {
            console.error('❌❌ Error crítico al guardar refresh token en segundo intento:', secondSaveError);
          }
          // Continuamos de todos modos, ya que el token de acceso está en memoria
        }
      } else {
        console.error('❌ No se recibió refresh token del servidor');
      }
      
      return response.data;
    } catch (error) {
      console.error('❌ Error en login:', error.message || error);
      
      // Limpiar estado en caso de error
      setAccessToken(null);
      
      // No borrar automáticamente el refresh token en caso de error general
      // Solo borrar si es un error de autenticación (401)
      if (error.response?.status === 401) {
        console.log('🧹 Limpiando refresh token debido a error 401 en login');
        await deleteSecureValue('refreshToken').catch(e => {
          console.warn('⚠️ Error al intentar borrar refresh token:', e);
        });
      }
      
      throw error;
    }
  },

  // Registrar usuario
  register: async (userData) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.REGISTER, userData);
      return response.data;
    } catch (error) {
      console.error('Error en registro:', error.message);
      throw error;
    }
  },

  // Cerrar sesión
  logout: async () => {
    try {
      const refreshToken = await getSecureValue('refreshToken');
      await apiClient.post(API_ENDPOINTS.LOGOUT, { refresh_token: refreshToken });
    } catch (error) {
      console.error('Error en logout:', error.message);
      // Ignorar
    } finally {
      setAccessToken(null);
      await deleteSecureValue('refreshToken');
    }
  },

  // Verificar si el usuario está autenticado
  isAuthenticated: async () => {
    try {
      console.log('🔐 Verificando autenticación...');
      
      // Primero verificar si tenemos un access token válido en memoria
      const memoryToken = getAccessTokenMem();
      if (memoryToken) {
        try {
          const tokenParts = memoryToken.split('.');
          if (tokenParts.length !== 3) {
            console.error('❌ Token malformado');
            // No borrar el token aquí para evitar borrados innecesarios
          } else {
            const tokenPayload = JSON.parse(atob(tokenParts[1]));
            const now = Math.floor(Date.now() / 1000);
            // Consideramos válido si no está a punto de expirar (más de 5 minutos de vida)
            if (tokenPayload.exp && tokenPayload.exp > now + 300) {
              console.log('✅ Access token válido en memoria');
              return true;
            } else {
              console.log(`⚠️ Access token expirado o próximo a expirar. Exp: ${tokenPayload.exp}, Now: ${now}`);
            }
          }
        } catch (e) {
          console.error('❌ Error al decodificar token:', e);
          // No borrar el token aquí para evitar borrados innecesarios
        }
      } else {
        console.log('⚠️ No hay access token en memoria');
      }
      
      // Intentar refrescar con refresh token
      console.log('🔄 Intentando usar refresh token...');
      
      // Obtener y verificar el refresh token primero antes de cualquier operación
      let refreshToken = null;
      try {
        refreshToken = await getSecureValue('refreshToken');
        console.log(`🔍 Refresh token encontrado: ${refreshToken ? 'Sí' : 'No'}`);
      } catch (tokenError) {
        console.error('❌ Error al leer refresh token:', tokenError);
      }
      
      if (!refreshToken) {
        console.error('❌ No hay refresh token disponible');
        return false;
      }
      
      // Guardar una copia del token para recuperación de emergencia
      const originalRefreshToken = refreshToken;
      
      try {
        console.log('🔄 Enviando solicitud de refresh...');
        const response = await axios.post(
          `${API_BASE_URL}${API_ENDPOINTS.REFRESH_TOKEN}`,
          { refresh_token: refreshToken },
          { 
            headers: { 'Content-Type': 'application/json' },
            // Añadir un timeout más corto para no bloquear el flujo
            timeout: 5000
          }
        );
        
        console.log('✅ Refresh exitoso, procesando nuevos tokens');
        const { access_token, refresh_token } = response.data;
        
        // Verificar el access token antes de guardarlo
        if (!access_token) {
          console.error('❌ No se recibió access token en refresh');
          throw new Error('No access token en respuesta');
        }
        
        // Guardar access token en memoria
        setAccessToken(access_token);
        console.log('✅ Nuevo access token guardado en memoria');
        
        // Luego guardar el nuevo refresh token si existe
        if (refresh_token) {
          try {
            console.log('📝 Intentando guardar nuevo refresh token...');
            const saved = await saveSecureValue('refreshToken', refresh_token);
            console.log(`✅ Nuevo refresh token guardado: ${saved ? 'Sí' : 'No'}`);
            
            // Verificar que se guardó correctamente
            try {
              const storedToken = await getSecureValue('refreshToken');
              console.log(`✅ Verificación de nuevo refresh token: ${storedToken ? 'Presente' : 'Ausente'}`);
              
              if (!storedToken) {
                console.warn('⚠️ El nuevo refresh token no se verificó, intentando recuperar');
                // Intentar restaurar el token original como respaldo
                await saveSecureValue('refreshToken', originalRefreshToken);
                console.log('🔄 Intento de recuperación del token original completado');
              }
            } catch (verifyError) {
              console.warn('⚠️ Error al verificar el token guardado:', verifyError);
              // Intentar restaurar el token original como respaldo
              await saveSecureValue('refreshToken', originalRefreshToken);
              console.log('🔄 Intento de recuperación del token original completado');
            }
          } catch (saveError) {
            console.error('❌ Error al guardar nuevo refresh token:', saveError);
            // Intentar restaurar el token original como respaldo
            try {
              await saveSecureValue('refreshToken', originalRefreshToken);
              console.log('🔄 Token original restaurado como respaldo');
            } catch (restoreError) {
              console.error('❌❌ Error crítico: No se pudo restaurar token original:', restoreError);
            }
          }
        } else {
          console.warn('⚠️ No se recibió un nuevo refresh token, manteniendo el actual');
          // Verificar que el token original sigue disponible
          try {
            const currentToken = await getSecureValue('refreshToken');
            if (!currentToken) {
              console.warn('⚠️ El token original se perdió, intentando recuperar');
              await saveSecureValue('refreshToken', originalRefreshToken);
            }
          } catch (checkError) {
            console.error('❌ Error al verificar token actual:', checkError);
          }
        }
        
        return true;
      } catch (error) {
        console.error('❌ Error al refrescar token:', error.response?.data || error.message || error);
        
        // Limpiar tokens solo en caso de error de autenticación (401)
        if (error.response?.status === 401) {
          console.log('🧹 Limpiando token de memoria debido a error 401 en refresh');
          setAccessToken(null);
          
          // Verificar el estado del refresh token antes de borrarlo
          try {
            const currentToken = await getSecureValue('refreshToken');
            console.log(`⚠️ Estado del refresh token antes de borrar: ${currentToken ? 'Presente' : 'Ausente'}`);
            
            if (!currentToken) {
              console.warn('⚠️ El refresh token ya no existe, no es necesario borrarlo');
            } else {
              await deleteSecureValue('refreshToken');
              console.log('🧹 Refresh token eliminado');
              
              // Verificar que se borró correctamente
              const tokenAfterDelete = await getSecureValue('refreshToken');
              console.log(`⚠️ Estado del token después de borrar: ${tokenAfterDelete ? 'Aún presente' : 'Eliminado correctamente'}`);
            }
          } catch (tokenError) {
            console.error('❌ Error al verificar estado del token:', tokenError);
          }
        } else {
          console.warn('⚠️ Error no relacionado con autenticación, manteniendo tokens');
        }
        
        return false;
      }
    } catch (e) {
      console.error('❌ Error general al verificar autenticación:', e);
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

// Servicios de sessions (reemplaza workouts)
export const sessionService = {
  // Iniciar una sesión de entrenamiento
  startSession: async (sessionId) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS_START(sessionId));
      // Devolver solo el objeto session, no toda la respuesta
      return response.data.session;
    } catch (error) {
      console.error(`Error al iniciar sesión ${sessionId}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Finalizar una sesión de entrenamiento (sin sessionId en URL)
  finishSession: async (sessionId = null) => {
    try {
      const params = sessionId ? { session_id: sessionId } : {};
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS_FINISH, {}, { params });
      return response.data;
    } catch (error) {
      console.error('Error al finalizar sesión:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener sesión activa
  getActiveSession: async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.SESSIONS_ACTIVE);
      return response.data.active_session; 
    } catch (error) {
      console.error('Error al obtener sesión activa:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Verificar estado de la sesión (nuevo endpoint para el sistema de monitoreo)
  getSessionStatus: async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.SESSIONS_STATUS);
      return response.data;
    } catch (error) {
      console.error('Error al verificar estado de sesión:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Enviar heartbeat para actualizar actividad (nuevo endpoint para el sistema de monitoreo)
  sendHeartbeat: async () => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS_HEARTBEAT);
      return response.data;
    } catch (error) {
      console.error('Error al enviar heartbeat:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Pausar sesión manualmente (nuevo endpoint para el sistema de monitoreo)
  pauseSession: async () => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS_PAUSE);
      return response.data;
    } catch (error) {
      console.error('Error al pausar sesión:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Reanudar sesión (nuevo endpoint para el sistema de monitoreo)
  resumeSession: async () => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS_RESUME);
      return response.data;
    } catch (error) {
      console.error('Error al reanudar sesión:', error.response?.data || error.message);
      throw error;
    }
  },
  
  // Abandonar sesión (nuevo endpoint para el sistema de monitoreo)
  abandonSession: async () => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS_ABANDON);
      return response.data;
    } catch (error) {
      console.error('Error al abandonar sesión:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener historial de sesiones
  getSessionHistory: async (limit = 10, offset = 0) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.SESSIONS_HISTORY, {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener historial de sesiones:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener detalles de una sesión específica
  getSessionById: async (sessionId) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.SESSIONS_BY_ID(sessionId));
      return response.data;
    } catch (error) {
      console.error(`Error al obtener sesión ${sessionId}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Registrar log de ejercicio de fuerza
  logStrengthExercise: async (exerciseData) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS_LOGS_STRENGTH, exerciseData);
      return response.data;
    } catch (error) {
      console.error('Error al registrar ejercicio de fuerza:', error.response?.data || error.message);
      throw error;
    }
  },

  // Registrar log de ejercicio de cardio
  logCardioExercise: async (exerciseData) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.SESSIONS_LOGS_CARDIO, exerciseData);
      return response.data;
    } catch (error) {
      console.error('Error al registrar ejercicio de cardio:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener progreso de un ejercicio en la sesión
  getExerciseProgress: async (exerciseId) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.SESSIONS_LOGS_EXERCISE_PROGRESS(exerciseId));
      return response.data;
    } catch (error) {
      console.error(`Error al obtener progreso del ejercicio ${exerciseId}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener todos los logs de la sesión activa
  getSessionLogs: async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.SESSIONS_LOGS);
      return response.data;
    } catch (error) {
      console.error('Error al obtener logs de la sesión:', error.response?.data || error.message);
      throw error;
    }
  },
};

// Servicios de ejercicios
export const exerciseService = {
  // Obtener ejercicios recientes
  getRecentExercises: async (limit = 10) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.EXERCISES_RECENT, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener ejercicios recientes:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener ejercicios populares
  getPopularExercises: async (limit = 10) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.EXERCISES_POPULAR, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener ejercicios populares:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener estadísticas de ejercicios
  getExerciseStats: async (days = 30) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.EXERCISES_STATS, {
        params: { days },
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas de ejercicios:', error.response?.data || error.message);
      throw error;
    }
  },

  // Buscar ejercicios
  searchExercises: async (query, limit = 20) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.EXERCISES_SEARCH, {
        params: { query, limit },
      });
      return response.data;
    } catch (error) {
      console.error('Error al buscar ejercicios:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener progreso de un ejercicio
  getExerciseProgress: async (exerciseName, days = 90) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.EXERCISES_PROGRESS(exerciseName), {
        params: { days },
      });
      return response.data;
    } catch (error) {
      console.error(`Error al obtener progreso del ejercicio ${exerciseName}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener catálogo de ejercicios
  getExerciseCatalog: async () => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.EXERCISES_CATALOG);
      return response.data;
    } catch (error) {
      console.error('Error al obtener catálogo de ejercicios:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener ejercicios estándar
  getStandardExercises: async (params = {}) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.EXERCISES_STANDARD, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener ejercicios estándar:', error.response?.data || error.message);
      throw error;
    }
  },

  // Autocompletado de ejercicios
  autocompleteExercises: async (query, limit = 10) => {
    try {
      const response = await apiClient.get('/exercises/autocomplete', {
        params: { query, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error en autocompletado de ejercicios:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener tipos de equipamiento
  getEquipmentTypes: async () => {
    try {
      const response = await apiClient.get('/exercises/equipment-types');
      return response.data;
    } catch (error) {
      console.error('Error al obtener tipos de equipamiento:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener grupos musculares
  getMuscleGroups: async () => {
    try {
      const response = await apiClient.get('/exercises/muscle-groups');
      return response.data;
    } catch (error) {
      console.error('Error al obtener grupos musculares:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener tipos de ejercicio
  getExerciseTypes: async () => {
    try {
      const response = await apiClient.get('/exercises/exercise-types');
      return response.data;
    } catch (error) {
      console.error('Error al obtener tipos de ejercicio:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener récords personales
  getPersonalRecords: async () => {
    try {
      const response = await apiClient.get('/exercises/personal-records');
      return response.data;
    } catch (error) {
      console.error('Error al obtener récords personales:', error.response?.data || error.message);
      throw error;
    }
  },
};

// Servicio para programaciones de entrenamiento
// Servicio API genérico para métodos HTTP básicos
export const apiService = {
  get: async (url, config = {}) => {
    try {
      const response = await apiClient.get(url, config);
      return response;
    } catch (error) {
      console.error(`Error en GET ${url}:`, error.response?.data || error.message);
      throw error;
    }
  },
  
  post: async (url, data = {}, config = {}) => {
    try {
      const response = await apiClient.post(url, data, config);
      return response;
    } catch (error) {
      console.error(`Error en POST ${url}:`, error.response?.data || error.message);
      throw error;
    }
  },
  
  put: async (url, data = {}, config = {}) => {
    try {
      const response = await apiClient.put(url, data, config);
      return response;
    } catch (error) {
      console.error(`Error en PUT ${url}:`, error.response?.data || error.message);
      throw error;
    }
  },
  
  delete: async (url, config = {}) => {
    try {
      const response = await apiClient.delete(url, config);
      return response;
    } catch (error) {
      console.error(`Error en DELETE ${url}:`, error.response?.data || error.message);
      throw error;
    }
  },
  
  // También incluimos métodos específicos para ejercicios para mantener compatibilidad
  getStandardExercises: async (params = {}) => {
    try {
      const response = await apiClient.get(API_ENDPOINTS.EXERCISES_STANDARD, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener ejercicios estándar:', error.response?.data || error.message);
      throw error;
    }
  },
  
  autocompleteExercises: async (query, limit = 10) => {
    try {
      const response = await apiClient.get('/exercises/autocomplete', {
        params: { query, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error en autocompletado de ejercicios:', error.response?.data || error.message);
      throw error;
    }
  }
};

export const trainingProgramsService = {
  // Obtener todas las programaciones
  getAll: async (skip = 0, limit = 100) => {
    try {
      const response = await apiClient.get('/training-programs/', {
        params: { skip, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener programaciones de entrenamiento:', error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener una programación específica
  getById: async (id) => {
    try {
      const response = await apiClient.get(`/training-programs/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error al obtener programación ${id}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Crear una nueva programación
  create: async (programData) => {
    try {
      const response = await apiClient.post('/training-programs/', programData);
      return response.data;
    } catch (error) {
      console.error('Error al crear programación:', error.response?.data || error.message);
      throw error;
    }
  },

  // Actualizar una programación
  update: async (id, programData) => {
    try {
      const response = await apiClient.put(`/training-programs/${id}`, programData);
      return response.data;
    } catch (error) {
      console.error(`Error al actualizar programación ${id}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Eliminar una programación
  delete: async (id) => {
    try {
      const response = await apiClient.delete(`/training-programs/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error al eliminar programación ${id}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Clonar una programación
  clone: async (id) => {
    try {
      const response = await apiClient.post(`/training-programs/${id}/clone`);
      return response.data;
    } catch (error) {
      console.error(`Error al clonar programación ${id}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener progreso del programa
  getProgress: async (id) => {
    try {
      const response = await apiClient.get(`/training-programs/${id}/progress`);
      return response.data;
    } catch (error) {
      // Si es un error 404, es probable que el endpoint no esté implementado o el programa no tenga progreso aún
      if (error.response?.status === 404) {
        console.warn(`Progress not found for program ${id} - this is normal for new programs`);
        return null;
      }
      console.error(`Error al obtener progreso del programa ${id}:`, error.response?.data || error.message);
      throw error;
    }
  },

  // Obtener detalles de una sesión específica
  getSessionDetails: async (programId, sessionId) => {
    try {
      // Obtener el programa completo para acceder a la estructura de la sesión
      const programResponse = await apiClient.get(`/training-programs/${programId}`);
      const program = programResponse.data;
      
      // Buscar la sesión específica en las semanas del programa
      let sessionData = null;
      if (program.training_weeks) {
        for (const week of program.training_weeks) {
          if (week.training_sessions) {
            const session = week.training_sessions.find(s => s.id === parseInt(sessionId));
            if (session) {
              sessionData = {
                ...session,
                week_number: week.week_number,
                week_description: week.description
              };
              break;
            }
          }
        }
      }
      
      if (!sessionData) {
        throw new Error('Sesión no encontrada en el programa');
      }
      
      return sessionData;
    } catch (error) {
      console.error(`Error al obtener detalles de sesión ${sessionId}:`, error);
      throw error;
    }
  },

    // Verificar estado de una sesión
  checkSessionStatus: async (sessionId) => {
    try {
      // Usar el endpoint de sesión activa para verificar si esta sesión está activa
      const activeResponse = await apiClient.get('/sessions/active');
      const activeSession = activeResponse.data.active_session;
      
      if (activeSession && activeSession.id === parseInt(sessionId)) {
        return {
          is_active: true,
          session: activeSession
        };
      } else {
        return {
          is_active: false,
          session: null
        };
      }
    } catch (error) {
      console.warn(`Error checking session status for session ${sessionId}:`, error);
      return {
        is_active: false,
        session: null
      };
    }
  },

  // Iniciar sesión 
  startSession: async (sessionId) => {
    try {
      const response = await apiClient.post(`/sessions/start/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error(`Error al iniciar sesión ${sessionId}:`, error);
      throw error;
    }
  },
};

export default apiClient; 