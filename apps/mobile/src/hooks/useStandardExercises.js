import { useState, useEffect } from 'react';
import { apiService } from '../services/apiService';

export const useStandardExercises = () => {
  const [exercises, setExercises] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    equipment: '',
    muscle_group: '',
    exercise_type: '',
    limit: 100
  });

  // Obtener ejercicios estándar
  const fetchExercises = async (filterParams = {}) => {
    setIsLoading(true);
    setError(null);
    try {
      const params = {};
      
      // Aplicar filtros
      if (filterParams.equipment) params.equipment = filterParams.equipment;
      if (filterParams.muscle_group) params.muscle_group = filterParams.muscle_group;
      if (filterParams.exercise_type) params.exercise_type = filterParams.exercise_type;
      if (filterParams.limit) params.limit = filterParams.limit;

      const data = await apiService.getStandardExercises(params);
      setExercises(data);
      return data;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  // Autocompletado de ejercicios
  const searchExercises = async (query, limit = 10) => {
    if (!query || query.length < 2) return [];
    
    try {
      return await apiService.autocompleteExercises(query, limit);
    } catch (err) {
      setError(err.message);
      return [];
    }
  };

  // Obtener tipos de equipamiento
  const getEquipmentTypes = async () => {
    try {
      const response = await apiService.get('/exercises/equipment-types');
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    }
  };

  // Obtener grupos musculares
  const getMuscleGroups = async () => {
    try {
      const response = await apiService.get('/exercises/muscle-groups');
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    }
  };

  // Obtener tipos de ejercicio
  const getExerciseTypes = async () => {
    try {
      const response = await apiService.get('/exercises/exercise-types');
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    }
  };

  // Obtener ejercicios recientes
  const getRecentExercises = async (limit = 10) => {
    try {
      const response = await apiService.get(`/exercises/recent?limit=${limit}`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    }
  };

  // Obtener ejercicios populares
  const getPopularExercises = async (limit = 10) => {
    try {
      const response = await apiService.get(`/exercises/popular?limit=${limit}`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    }
  };

  // Obtener catálogo de ejercicios
  const getExerciseCatalog = async () => {
    try {
      return await apiService.getExerciseCatalog();
    } catch (err) {
      setError(err.message);
      return {};
    }
  };

  // Obtener estadísticas de ejercicios
  const getExerciseStats = async (days = 30) => {
    try {
      const response = await apiService.get(`/exercises/stats?days=${days}`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  // Obtener progreso de un ejercicio específico
  const getExerciseProgress = async (exerciseName, days = 90) => {
    try {
      const response = await apiService.get(`/exercises/progress/${encodeURIComponent(exerciseName)}?days=${days}`);
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    }
  };

  // Obtener récords personales
  const getPersonalRecords = async () => {
    try {
      const response = await apiService.get('/exercises/personal-records');
      return response.data;
    } catch (err) {
      setError(err.message);
      return [];
    }
  };

  // Aplicar filtros
  const applyFilters = (newFilters) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    fetchExercises(updatedFilters);
  };

  // Limpiar filtros
  const clearFilters = () => {
    const defaultFilters = {
      equipment: '',
      muscle_group: '',
      exercise_type: '',
      limit: 100
    };
    setFilters(defaultFilters);
    fetchExercises(defaultFilters);
  };

  // Cargar ejercicios iniciales
  useEffect(() => {
    fetchExercises(filters);
  }, []);

  return {
    exercises,
    isLoading,
    error,
    filters,
    fetchExercises,
    searchExercises,
    getEquipmentTypes,
    getMuscleGroups,
    getExerciseTypes,
    getRecentExercises,
    getPopularExercises,
    getExerciseCatalog,
    getExerciseStats,
    getExerciseProgress,
    getPersonalRecords,
    applyFilters,
    clearFilters,
    setError
  };
};
