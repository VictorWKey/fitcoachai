import { useEffect } from 'react';
import { Alert } from 'react-native';
import { useAuthStore } from '../store/authStore';
import { resetAllStores } from '../store/storeRegistry';

/**
 * Hook personalizado para manejar la autenticación
 * @returns {Object} Funciones y estado de autenticación
 */
export const useAuth = () => {
  const { 
    isAuthenticated, 
    user, 
    isLoading, 
    error,
    login,
    register,
    logout,
    clearError
  } = useAuthStore();

  // Limpiar errores cuando el componente se desmonta
  useEffect(() => {
    return () => {
      if (error) clearError();
    };
  }, [error, clearError]);

  /**
   * Manejar inicio de sesión
   * @param {string} username - Nombre de usuario o email
   * @param {string} password - Contraseña
   * @returns {Promise<void>}
   */
  const handleLogin = async (username, password) => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Error', 'Por favor, completa todos los campos');
      return false;
    }

    try {
      const result = await login(username, password);
      console.log('Login exitoso, redirigiendo...');
      return true;
    } catch (error) {
      console.error('Error de login:', error);
      return false;
    }
  };

  /**
   * Manejar registro de usuario
   * @param {Object} userData - Datos del usuario
   * @returns {Promise<void>}
   */
  const handleRegister = async (userData) => {
    try {
      await register(userData);
      return true;
    } catch (error) {
      console.error('Error de registro:', error);
      // El error ya se maneja en el store
      return false;
    }
  };

  /**
   * Manejar cierre de sesión
   * @returns {Promise<void>}
   */
  const handleLogout = async () => {
    try {
      await logout();
      // Reiniciar todos los Zustand stores registrados (estado app limpio)
      resetAllStores();
    } catch (error) {
      console.error('Error de logout:', error);
      // El error ya se maneja en el store
    }
  };

  return {
    isAuthenticated,
    user,
    isLoading,
    error,
    handleLogin,
    handleRegister,
    handleLogout,
    clearError
  };
}; 