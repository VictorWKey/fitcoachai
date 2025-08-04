import { useEffect } from 'react';
import { Alert } from 'react-native';
import { useAuthStore } from '../store/authStore';
import { resetAllStores } from '../store/storeRegistry';
import { Validator, ApiError, TRANSLATIONS } from '../types/api';

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

  // Función para manejar errores con mensajes localizados
  const handleError = (error) => {
    let title = TRANSLATIONS.es.common.error;
    let message = 'Ha ocurrido un error inesperado';

    if (error instanceof ApiError) {
      message = TRANSLATIONS.es.errors[error.code] || error.message;
    } else if (typeof error === 'string') {
      message = error;
    } else if (error?.message) {
      message = error.message;
    }

    Alert.alert(title, message);
  };

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
   * @returns {Promise<boolean>}
   */
  const handleLogin = async (username, password) => {
    if (!username.trim() || !password.trim()) {
      Alert.alert(TRANSLATIONS.es.common.error, 'Por favor, completa todos los campos');
      return false;
    }

    // Validar formato de email si es un email
    if (username.includes('@')) {
      const emailValidation = Validator.validateEmail(username);
      if (!emailValidation.isValid) {
        Alert.alert(TRANSLATIONS.es.common.error, emailValidation.message);
        return false;
      }
    }

    // Validar contraseña
    const passwordValidation = Validator.validatePassword(password);
    if (!passwordValidation.isValid) {
      Alert.alert(TRANSLATIONS.es.common.error, passwordValidation.message);
      return false;
    }

    try {
      await login(username, password);
      console.log('Login exitoso, redirigiendo...');
      return true;
    } catch (error) {
      console.error('Error de login:', error);
      handleError(error);
      return false;
    }
  };

  /**
   * Manejar registro de usuario
   * @param {Object} userData - Datos del usuario
   * @returns {Promise<boolean>}
   */
  const handleRegister = async (userData) => {
    // Validaciones antes del registro
    if (userData.email) {
      const emailValidation = Validator.validateEmail(userData.email);
      if (!emailValidation.isValid) {
        Alert.alert(TRANSLATIONS.es.common.error, emailValidation.message);
        return false;
      }
    }

    if (userData.password) {
      const passwordValidation = Validator.validatePassword(userData.password);
      if (!passwordValidation.isValid) {
        Alert.alert(TRANSLATIONS.es.common.error, passwordValidation.message);
        return false;
      }
    }

    try {
      await register(userData);
      return true;
    } catch (error) {
      console.error('Error de registro:', error);
      handleError(error);
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
      handleError(error);
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