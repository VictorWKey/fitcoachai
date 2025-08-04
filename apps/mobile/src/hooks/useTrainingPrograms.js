import { useState, useEffect } from 'react';
import { trainingProgramsService } from '../services/apiService';

export const useTrainingPrograms = () => {
  const [programs, setPrograms] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Obtener todas las programaciones
  const fetchPrograms = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await trainingProgramsService.getAll();
      setPrograms(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Obtener una programación específica
  const getProgram = async (id) => {
    try {
      const data = await trainingProgramsService.getById(id);
      return data;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  // Crear una nueva programación
  const createProgram = async (programData) => {
    setIsLoading(true);
    setError(null);
    try {
      const newProgram = await trainingProgramsService.create(programData);
      setPrograms(prev => [...prev, newProgram]);
      return newProgram;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Actualizar una programación
  const updateProgram = async (id, programData) => {
    setIsLoading(true);
    setError(null);
    try {
      const updatedProgram = await trainingProgramsService.update(id, programData);
      setPrograms(prev => prev.map(program => 
        program.id === id ? updatedProgram : program
      ));
      return updatedProgram;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Eliminar una programación
  const deleteProgram = async (id) => {
    setIsLoading(true);
    setError(null);
    try {
      await trainingProgramsService.delete(id);
      setPrograms(prev => prev.filter(program => program.id !== id));
      return true;
    } catch (err) {
      setError(err.message);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  // Clonar una programación
  const cloneProgram = async (id) => {
    setIsLoading(true);
    setError(null);
    try {
      const clonedProgram = await trainingProgramsService.clone(id);
      setPrograms(prev => [...prev, clonedProgram]);
      return clonedProgram;
    } catch (err) {
      setError(err.message);
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  // Obtener progreso del programa
  const getProgramProgress = async (id) => {
    try {
      const progressData = await trainingProgramsService.getProgress(id);
      return progressData;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  // Obtener programa con información de progreso
  const getProgramWithProgress = async (id) => {
    try {
      // Primero obtener el programa básico
      const programData = await trainingProgramsService.getById(id);
      
      // Intentar obtener información de progreso, pero no fallar si no está disponible
      try {
        const progressData = await trainingProgramsService.getProgress(id);
        
        // Combinar datos del programa con información de progreso si existe
        if (progressData && progressData.session_completion_data) {
          programData.training_weeks = programData.training_weeks?.map(week => {
            const weekProgress = progressData.session_completion_data.find(
              w => w.week_number === week.week_number
            );
            
            if (weekProgress) {
              week.training_sessions = week.training_sessions?.map(session => {
                const sessionProgress = weekProgress.sessions.find(
                  s => s.session_id === session.id
                );
                
                if (sessionProgress) {
                  session.is_completed = sessionProgress.is_completed;
                  session.completed_at = sessionProgress.completed_at;
                } else {
                  // Si no hay información de progreso, marcar como no completado
                  session.is_completed = false;
                  session.completed_at = null;
                }
                
                return session;
              });
            } else {
              // Si no hay información de la semana, marcar todas las sesiones como no completadas
              week.training_sessions = week.training_sessions?.map(session => ({
                ...session,
                is_completed: false,
                completed_at: null
              }));
            }
            
            return week;
          });
        } else {
          // Si no hay información de progreso, marcar todas las sesiones como no completadas
          programData.training_weeks = programData.training_weeks?.map(week => ({
            ...week,
            training_sessions: week.training_sessions?.map(session => ({
              ...session,
              is_completed: false,
              completed_at: null
            }))
          }));
        }
      } catch (progressError) {
        console.warn('Progress information not available, using basic program data:', progressError);
        // Si falla la obtención del progreso, marcar todas las sesiones como no completadas
        programData.training_weeks = programData.training_weeks?.map(week => ({
          ...week,
          training_sessions: week.training_sessions?.map(session => ({
            ...session,
            is_completed: false,
            completed_at: null
          }))
        }));
      }
      
      return programData;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  // Obtener detalles de sesión
  const getSessionDetails = async (programId, sessionId) => {
    try {
      const sessionData = await trainingProgramsService.getSessionDetails(programId, sessionId);
      return sessionData;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  // Verificar estado de sesión
  const checkSessionStatus = async (sessionId) => {
    try {
      const statusData = await trainingProgramsService.checkSessionStatus(sessionId);
      return statusData;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  // Iniciar sesión
  const startSession = async (sessionId) => {
    try {
      const workoutData = await trainingProgramsService.startSession(sessionId);
      return workoutData;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  // Limpiar errores
  const clearError = () => {
    setError(null);
  };

  // Efecto para cargar programaciones al montar el componente
  useEffect(() => {
    fetchPrograms();
  }, []);

  return {
    programs,
    isLoading,
    error,
    fetchPrograms,
    getProgram,
    getProgramWithProgress,
    createProgram,
    updateProgram,
    deleteProgram,
    cloneProgram,
    getProgramProgress,
    getSessionDetails,
    checkSessionStatus,
    startSession,
    clearError,
  };
};
