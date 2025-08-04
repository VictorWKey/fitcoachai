import React, { createContext, useContext, useState, useCallback } from 'react';
import { Alert } from 'react-native';
import { ApiError, ErrorCode, TRANSLATIONS } from '../types/api';

const ErrorContext = createContext();

export const useError = () => {
  const context = useContext(ErrorContext);
  if (!context) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
};

export const ErrorProvider = ({ children }) => {
  const [errors, setErrors] = useState([]);

  const showError = useCallback((error) => {
    let title = 'Error';
    let message = 'Ha ocurrido un error inesperado';

    if (error instanceof ApiError) {
      title = TRANSLATIONS.es.common.error;
      message = TRANSLATIONS.es.errors[error.code] || error.message;
    } else if (typeof error === 'string') {
      message = error;
    } else if (error?.message) {
      message = error.message;
    }

    Alert.alert(title, message, [
      { text: 'OK', style: 'default' }
    ]);

    // Almacenar error para debugging
    setErrors(prev => [...prev, {
      timestamp: new Date().toISOString(),
      error,
      message
    }]);
  }, []);

  const clearErrors = useCallback(() => {
    setErrors([]);
  }, []);

  const handleApiError = useCallback((error) => {
    // Log específico para errores de API
    console.error('API Error:', {
      code: error.code,
      message: error.message,
      status: error.status,
      details: error.details
    });

    // Mostrar error al usuario
    showError(error);
  }, [showError]);

  const value = {
    errors,
    showError,
    clearErrors,
    handleApiError
  };

  return (
    <ErrorContext.Provider value={value}>
      {children}
    </ErrorContext.Provider>
  );
};

export default ErrorProvider;
