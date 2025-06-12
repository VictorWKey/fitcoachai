import { create } from 'zustand';
import { authService } from '../services/apiService';
import { registerReset } from './storeRegistry';

export const useAuthStore = create((set) => ({
  // Estado inicial
  isAuthenticated: false,
  user: null,
  isLoading: false,
  error: null,
  
  // Acciones
  setIsAuthenticated: (value) => set({ isAuthenticated: value }),
  
  setUser: (user) => set({ user }),
  
  clearError: () => set({ error: null }),
  
  login: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authService.login({ username, password });
      set({ 
        isAuthenticated: true, 
        user: data.user || { username },
        isLoading: false,
        error: null
      });
      return data;
    } catch (error) {
      let errorMessage = 'Error al iniciar sesión';
      if (error.response?.status === 401) {
        // Verificar si el mensaje de error indica que la cuenta está bloqueada
        const errorDetail = error.response?.data?.detail || '';
        if (errorDetail.includes('Account locked')) {
          // Extraer los minutos restantes del mensaje de error
          const minutesMatch = errorDetail.match(/(\d+) minutes?/);
          const minutes = minutesMatch ? minutesMatch[1] : 'varios';
          errorMessage = `Cuenta bloqueada temporalmente. Intenta de nuevo en ${minutes} minutos.`;
        } else {
          errorMessage = 'Usuario o contraseña incorrectos';
        }
      } else if (error.response?.status === 403) {
        errorMessage = 'Por favor, verifica tu email antes de iniciar sesión';
      }
      set({ 
        isLoading: false, 
        error: errorMessage,
        isAuthenticated: false,
        user: null
      });
      throw new Error(errorMessage);
    }
  },
  
  register: async (userData) => {
    set({ isLoading: true, error: null });
    try {
      const data = await authService.register(userData);
      set({ isLoading: false });
      return data;
    } catch (error) {
      let errorMessage = 'Error al registrar usuario';
      if (error.response?.status === 400) {
        errorMessage = error.response.data.detail || 'Los datos ingresados no son válidos';
      } else if (error.response?.status === 409) {
        errorMessage = 'El usuario o email ya existe';
      }
      set({ 
        isLoading: false, 
        error: errorMessage 
      });
      throw error;
    }
  },
  
  logout: async () => {
    set({ isLoading: true, error: null });
    try {
      await authService.logout();

      set({ 
        isAuthenticated: false, 
        user: null,
        isLoading: false 
      });
    } catch (error) {
      // Asegurarse de limpiar los tokens incluso si hay un error
      await authService.deleteSecureValue('accessToken').catch(() => {});
      await authService.deleteSecureValue('refreshToken').catch(() => {});
      set({ 
        isAuthenticated: false,
        user: null,
        isLoading: false, 
        error: 'Se cerró la sesión localmente debido a un error' 
      });
      throw error;
    }
  },
  
  // Verificar el estado de autenticación actual
  checkAuth: async () => {
    try {
      const isAuthenticated = await authService.isAuthenticated();
      set({ 
        isAuthenticated,
        isInitialized: true 
      });
      return isAuthenticated;
    } catch (error) {
      console.error('Error al verificar autenticación:', error);
      set({ 
        isAuthenticated: false,
        isInitialized: true
      });
      return false;
    }
  },
  
  // Método para reiniciar este store
  reset: () => set({
    isAuthenticated: false,
    user: null,
    isLoading: false,
    error: null,
  })
}));

// Registrar el reset en el registry global
registerReset(useAuthStore.getState().reset);