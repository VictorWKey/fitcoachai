import { useState, useCallback } from 'react';
import { sessionService } from '../services/apiService';
import { ApiError, ErrorCode, TRANSLATIONS } from '../types/api';
import { useSessionStore } from '../store/sessionStore';

/**
 * Hook personalizado para manejar sesiones de entrenamiento
 * @returns {Object} Funciones y estado de sesiones
 */
export const useSessions = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sessionLogs, setSessionLogs] = useState([]);

  // Usar el store global para activeSession
  const { 
    activeSession, 
    setActiveSession: setGlobalActiveSession, 
    clearActiveSession 
  } = useSessionStore();

  // Función para manejar errores con mensajes localizados
  const handleError = useCallback((err) => {
    let errorMessage = 'Error desconocido';
    
    if (err instanceof ApiError) {
      errorMessage = TRANSLATIONS.es.errors[err.code] || err.message;
    } else {
      errorMessage = err.message || 'Error de conexión';
    }
    
    setError(errorMessage);
    console.error('Session error:', err);
  }, []);

  // Limpiar errores
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Iniciar una sesión
  const startSession = useCallback(async (sessionId) => {
    setIsLoading(true);
    setError(null);
    try {
      console.log('=== HOOK: Starting session ===');
      console.log('sessionId:', sessionId);
      const sessionData = await sessionService.startSession(sessionId);
      console.log('=== HOOK: Session started successfully ===');
      console.log('sessionData:', sessionData);
      console.log('Updating global store with session data');
      setGlobalActiveSession(sessionData); // Actualizar store global
      return sessionData;
    } catch (err) {
      console.error('=== HOOK: Error starting session ===', err);
      handleError(err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [handleError, setGlobalActiveSession]);

  // Finalizar una sesión
  const finishSession = useCallback(async (sessionId = null) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await sessionService.finishSession(sessionId);
      console.log('Session finished successfully:', result);
      clearActiveSession(); // Limpiar store global
      setSessionLogs([]);
      return result;
    } catch (err) {
      handleError(err);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [handleError, clearActiveSession]);
  
  // Verificar estado de la sesión (nuevo para el sistema de monitoreo)
  const checkSessionStatus = useCallback(async () => {
    setError(null);
    try {
      const statusData = await sessionService.getSessionStatus();
      if (statusData.has_active_session) {
        console.log('Session status check: Active session found');
        setGlobalActiveSession(statusData.session);
        return statusData.session;
      } else {
        console.log('Session status check: No active session');
        clearActiveSession();
        return null;
      }
    } catch (err) {
      console.error('Error al verificar estado de sesión:', err);
      // En caso de error de conexión, mantener el estado actual
      return activeSession;
    }
  }, [activeSession, setGlobalActiveSession, clearActiveSession]);
  
  // Enviar heartbeat para actualizar actividad (nuevo para el sistema de monitoreo)
  const sendHeartbeat = useCallback(async () => {
    try {
      const result = await sessionService.sendHeartbeat();
      return result;
    } catch (err) {
      console.error('Error al enviar heartbeat:', err);
      return null;
    }
  }, []);
  
  // Pausar sesión manualmente (nuevo para el sistema de monitoreo)
  const pauseSession = useCallback(async () => {
    setError(null);
    try {
      const result = await sessionService.pauseSession();
      // Actualizar el estado de la sesión a 'paused'
      if (activeSession) {
        setGlobalActiveSession({...activeSession, status: 'paused'});
      }
      return result;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, [activeSession, setGlobalActiveSession, handleError]);
  
  // Reanudar sesión (nuevo para el sistema de monitoreo)
  const resumeSession = useCallback(async () => {
    setError(null);
    try {
      const result = await sessionService.resumeSession();
      // Actualizar el estado de la sesión a 'active'
      if (activeSession) {
        setGlobalActiveSession({...activeSession, status: 'active'});
      }
      return result;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, [activeSession, setGlobalActiveSession, handleError]);
  
  // Abandonar sesión (nuevo para el sistema de monitoreo)
  const abandonSession = useCallback(async () => {
    setError(null);
    try {
      const result = await sessionService.abandonSession();
      clearActiveSession(); // Limpiar store global
      setSessionLogs([]);
      return result;
    } catch (err) {
      handleError(err);
      return null;
    }
  }, [handleError, clearActiveSession]);

  // Obtener sesión activa
  const getActiveSession = useCallback(async () => {
    setError(null);
    try {
      const sessionData = await sessionService.getActiveSession();
      console.log('Session service returned:', sessionData ? 'SESSION_DATA' : 'NULL');
      setGlobalActiveSession(sessionData); // Actualizar store global
      return sessionData;
    } catch (err) {
      console.error('Error al obtener sesión activa:', err);
      // Si no hay sesión activa (404), no es un error
      if (err.response?.status === 404) {
        console.log('No active session found (404)');
        clearActiveSession(); // Limpiar store global
        return null;
      }
      // Para otros errores, no limpiar la sesión activa inmediatamente
      // Solo registrar el error
      console.log('Error temporal al obtener sesión activa, manteniendo estado actual');
      setError('No se pudo obtener la sesión activa');
      return activeSession; // Retornar la sesión actual si existe
    } finally {
      setIsLoading(false);
    }
  }, [activeSession, setGlobalActiveSession, clearActiveSession]);

  // Registrar ejercicio de fuerza
  const logStrengthExercise = useCallback(async (exerciseData) => {
    setError(null);
    try {
      const response = await sessionService.logStrengthExercise(exerciseData);
      // La API devuelve { message, log, programmed_sets, completed_sets, remaining_sets }
      const loggedExercise = response.log;
      // Actualizar logs locales
      setSessionLogs(prev => [...prev, loggedExercise]);
      return response; // Retornar toda la respuesta para acceder a log, programmed_sets, etc.
    } catch (err) {
      console.error('Error al registrar ejercicio de fuerza:', err);
      setError('No se pudo registrar el ejercicio');
      return null;
    }
  }, []);

  // Registrar ejercicio de cardio
  const logCardioExercise = useCallback(async (exerciseData) => {
    setError(null);
    try {
      const response = await sessionService.logCardioExercise(exerciseData);
      const loggedExercise = response.log;
      // Actualizar logs locales
      setSessionLogs(prev => [...prev, loggedExercise]);
      return response;
    } catch (err) {
      console.error('Error al registrar ejercicio de cardio:', err);
      setError('No se pudo registrar el ejercicio de cardio');
      return null;
    }
  }, []);

  // Obtener progreso de un ejercicio
  const getExerciseProgress = useCallback(async (exerciseId) => {
    try {
      const progress = await sessionService.getExerciseProgress(exerciseId);
      return progress;
    } catch (err) {
      console.error('Error al obtener progreso del ejercicio:', err);
      setError('No se pudo obtener el progreso del ejercicio');
      return null;
    }
  }, []);

  // Obtener logs de la sesión
  const getSessionLogs = useCallback(async () => {
    setError(null);
    try {
      const logs = await sessionService.getSessionLogs();
      setSessionLogs(logs);
      return logs;
    } catch (err) {
      console.error('Error al obtener logs de la sesión:', err);
      setError('No se pudieron obtener los logs de la sesión');
      return [];
    }
  }, []);

  return {
    isLoading,
    error,
    activeSession,
    sessionLogs,
    startSession,
    finishSession,
    getActiveSession,
    logStrengthExercise,
    logCardioExercise,
    getExerciseProgress,
    getSessionLogs,
    clearError,
    // Nuevos métodos para el sistema de monitoreo
    checkSessionStatus,
    sendHeartbeat,
    pauseSession,
    resumeSession,
    abandonSession
  };
};
