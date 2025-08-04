// Utilidades para validación de datos de entrenamiento
// Basado en la documentación de frontend_integration_guide.md

/**
 * Valida el formato de tempo
 * @param {string} tempo - Tempo en formato "E-B-C-T" o "E-B-C"
 * @returns {boolean} - True si es válido
 */
export const validateTempo = (tempo) => {
  if (!tempo || typeof tempo !== 'string') return false;
  
  // Formato 4 partes: E-B-C-T
  const regex4Part = /^(\d+|X)-(\d+|X)-(\d+|X)-(\d+|X)$/;
  
  // Formato 3 partes: E-B-C
  const regex3Part = /^(\d+|X)-(\d+|X)-(\d+|X)$/;
  
  return regex4Part.test(tempo) || regex3Part.test(tempo);
};

/**
 * Valida el rango de RPE (Rate of Perceived Exertion)
 * @param {number|string} rpe - Valor de RPE
 * @returns {boolean} - True si es válido
 */
export const validateRPE = (rpe) => {
  const num = parseFloat(rpe);
  return !isNaN(num) && num >= 1.0 && num <= 10.0;
};

/**
 * Valida el rango de RIR (Reps in Reserve)
 * @param {number|string} rir - Valor de RIR
 * @returns {boolean} - True si es válido
 */
export const validateRIR = (rir) => {
  const num = parseInt(rir);
  return !isNaN(num) && num >= 0 && num <= 10;
};

/**
 * Valida el formato de peso
 * @param {number|string} weight - Peso
 * @returns {boolean} - True si es válido
 */
export const validateWeight = (weight) => {
  if (!weight) return true; // El peso puede ser opcional
  const num = parseFloat(weight);
  return !isNaN(num) && num >= 0;
};

/**
 * Valida el número de series
 * @param {number|string} sets - Número de series
 * @returns {boolean} - True si es válido
 */
export const validateSets = (sets) => {
  const num = parseInt(sets);
  return !isNaN(num) && num >= 1 && num <= 20;
};

/**
 * Valida el número de repeticiones
 * @param {number|string} reps - Número de repeticiones
 * @returns {boolean} - True si es válido
 */
export const validateReps = (reps) => {
  const num = parseInt(reps);
  return !isNaN(num) && num >= 1 && num <= 100;
};

/**
 * Valida el tiempo de descanso en segundos
 * @param {number|string} restSeconds - Tiempo de descanso
 * @returns {boolean} - True si es válido
 */
export const validateRestSeconds = (restSeconds) => {
  const num = parseInt(restSeconds);
  return !isNaN(num) && num >= 0 && num <= 3600; // Máximo 1 hora
};

/**
 * Valida el porcentaje de 1RM
 * @param {number|string} percentage - Porcentaje de 1RM
 * @returns {boolean} - True si es válido
 */
export const validatePercentage1RM = (percentage) => {
  if (!percentage) return true; // Puede ser opcional
  const num = parseFloat(percentage);
  return !isNaN(num) && num >= 10 && num <= 200;
};

/**
 * Valida el nombre del programa
 * @param {string} name - Nombre del programa
 * @returns {boolean} - True si es válido
 */
export const validateProgramName = (name) => {
  return typeof name === 'string' && name.trim().length >= 3 && name.trim().length <= 100;
};

/**
 * Valida la descripción del programa
 * @param {string} description - Descripción del programa
 * @returns {boolean} - True si es válido
 */
export const validateProgramDescription = (description) => {
  if (!description) return true; // Puede ser opcional
  return typeof description === 'string' && description.trim().length <= 500;
};

/**
 * Valida la duración del programa en semanas
 * @param {number|string} weeks - Número de semanas
 * @returns {boolean} - True si es válido
 */
export const validateProgramWeeks = (weeks) => {
  const num = parseInt(weeks);
  return !isNaN(num) && num >= 1 && num <= 52; // Máximo 1 año
};

/**
 * Valida el tipo de programa
 * @param {string} type - Tipo de programa
 * @returns {boolean} - True si es válido
 */
export const validateProgramType = (type) => {
  const validTypes = ['strength', 'hypertrophy', 'peaking'];
  return validTypes.includes(type);
};

/**
 * Valida el tipo de serie
 * @param {string} setType - Tipo de serie
 * @returns {boolean} - True si es válido
 */
export const validateSetType = (setType) => {
  const validTypes = ['strength', 'hypertrophy', 'technique'];
  return validTypes.includes(setType);
};

/**
 * Valida el tipo de bloque
 * @param {string} blockType - Tipo de bloque
 * @returns {boolean} - True si es válido
 */
export const validateBlockType = (blockType) => {
  const validTypes = ['main', 'accessory'];
  return validTypes.includes(blockType);
};

/**
 * Valida el tipo de carga
 * @param {string} loadType - Tipo de carga
 * @returns {boolean} - True si es válido
 */
export const validateLoadType = (loadType) => {
  const validTypes = ['rpe', 'percentage', 'weight'];
  return validTypes.includes(loadType);
};

/**
 * Valida la unidad de peso
 * @param {string} unit - Unidad de peso
 * @returns {boolean} - True si es válido
 */
export const validateWeightUnit = (unit) => {
  const validUnits = ['kg', 'lb'];
  return validUnits.includes(unit);
};

/**
 * Valida la unidad de distancia (para cardio)
 * @param {string} unit - Unidad de distancia
 * @returns {boolean} - True si es válido
 */
export const validateDistanceUnit = (unit) => {
  const validUnits = ['km', 'mi'];
  return validUnits.includes(unit);
};

/**
 * Valida el tipo de cardio
 * @param {string} cardioType - Tipo de cardio
 * @returns {boolean} - True si es válido
 */
export const validateCardioType = (cardioType) => {
  const validTypes = ['hiit', 'steady_state'];
  return validTypes.includes(cardioType);
};

/**
 * Valida la frecuencia cardíaca
 * @param {number|string} heartRate - Frecuencia cardíaca
 * @returns {boolean} - True si es válido
 */
export const validateHeartRate = (heartRate) => {
  if (!heartRate) return true; // Puede ser opcional
  const num = parseInt(heartRate);
  return !isNaN(num) && num >= 40 && num <= 220;
};

/**
 * Valida las calorías quemadas
 * @param {number|string} calories - Calorías quemadas
 * @returns {boolean} - True si es válido
 */
export const validateCalories = (calories) => {
  if (!calories) return true; // Puede ser opcional
  const num = parseInt(calories);
  return !isNaN(num) && num >= 0 && num <= 5000;
};

/**
 * Valida la distancia
 * @param {number|string} distance - Distancia
 * @returns {boolean} - True si es válido
 */
export const validateDistance = (distance) => {
  if (!distance) return true; // Puede ser opcional
  const num = parseFloat(distance);
  return !isNaN(num) && num >= 0 && num <= 1000;
};

/**
 * Valida la duración en segundos
 * @param {number|string} duration - Duración en segundos
 * @returns {boolean} - True si es válido
 */
export const validateDuration = (duration) => {
  if (!duration) return true; // Puede ser opcional
  const num = parseInt(duration);
  return !isNaN(num) && num >= 0 && num <= 86400; // Máximo 24 horas
};

/**
 * Convierte tempo a formato legible
 * @param {string} tempo - Tempo en formato "E-B-C-T"
 * @returns {string} - Tempo en formato legible
 */
export const formatTempo = (tempo) => {
  if (!validateTempo(tempo)) return 'Inválido';
  
  const parts = tempo.split('-');
  if (parts.length === 3) {
    return `${parts[0]}s bajada - ${parts[1]}s pausa - ${parts[2]}s subida`;
  } else if (parts.length === 4) {
    return `${parts[0]}s bajada - ${parts[1]}s pausa - ${parts[2]}s subida - ${parts[3]}s pausa`;
  }
  
  return tempo;
};

/**
 * Convierte RPE a descripción
 * @param {number} rpe - Valor de RPE
 * @returns {string} - Descripción del RPE
 */
export const getRPEDescription = (rpe) => {
  if (!validateRPE(rpe)) return 'Inválido';
  
  const num = parseFloat(rpe);
  if (num <= 3) return 'Muy fácil';
  if (num <= 6) return 'Moderado';
  if (num <= 8) return 'Difícil';
  if (num <= 10) return 'Máximo esfuerzo';
  return 'Inválido';
};

/**
 * Genera ejemplos de tempo válidos
 * @returns {string[]} - Array de ejemplos
 */
export const getTempoExamples = () => {
  return [
    '3-1-1-0', // Controlado
    '2-0-X-0', // Explosivo
    '4-2-1-1', // Lento y controlado
    '3-1-2',   // Formato 3 partes
    '1-0-1-0', // Rápido
  ];
};

/**
 * Valida un objeto de ejercicio programado completo
 * @param {object} exercise - Objeto de ejercicio
 * @returns {object} - Objeto con validación y errores
 */
export const validateProgrammedExercise = (exercise) => {
  const errors = {};
  
  if (!exercise.standard_exercise_id) {
    errors.standard_exercise_id = 'ID del ejercicio es requerido';
  }
  
  if (!validateSets(exercise.sets)) {
    errors.sets = 'Número de series debe ser entre 1 y 20';
  }
  
  if (!validateReps(exercise.reps)) {
    errors.reps = 'Número de repeticiones debe ser entre 1 y 100';
  }
  
  if (!validateLoadType(exercise.load_type)) {
    errors.load_type = 'Tipo de carga debe ser rpe, percentage o weight';
  }
  
  if (exercise.load_type === 'rpe' && !validateRPE(exercise.rpe_target)) {
    errors.rpe_target = 'RPE debe ser entre 1.0 y 10.0';
  }
  
  if (exercise.load_type === 'percentage' && !validatePercentage1RM(exercise.percentage_1rm)) {
    errors.percentage_1rm = 'Porcentaje debe ser entre 10 y 200';
  }
  
  if (exercise.tempo && !validateTempo(exercise.tempo)) {
    errors.tempo = 'Formato de tempo inválido';
  }
  
  if (!validateRestSeconds(exercise.rest_seconds)) {
    errors.rest_seconds = 'Tiempo de descanso debe ser entre 0 y 3600 segundos';
  }
  
  if (!validateSetType(exercise.sets_type)) {
    errors.sets_type = 'Tipo de serie debe ser strength, hypertrophy o technique';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};
