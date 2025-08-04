// ===========================
// ENUMS Y CONSTANTES
// ===========================

// Tipos de programa de entrenamiento
export const ProgramType = {
  HYPERTROPHY: 'hypertrophy',
  STRENGTH: 'strength',
  PEAKING: 'peaking'
};

// Tipos de bloque
export const BlockType = {
  MAIN: 'main',
  ACCESSORY: 'accessory'
};

// Tipos de carga
export const LoadType = {
  RPE: 'rpe',
  PERCENTAGE: 'percentage',
  WEIGHT: 'weight'
};

// Tipos de serie
export const SetType = {
  STRENGTH: 'strength',
  HYPERTROPHY: 'hypertrophy',
  TECHNIQUE: 'technique'
};

// Unidades de peso
export const WeightUnit = {
  KG: 'kg',
  LBS: 'lbs'
};

// Códigos de error
export const ErrorCode = {
  // Auth Errors
  INVALID_CREDENTIALS: 'invalid_credentials',
  TOKEN_EXPIRED: 'token_expired',
  USER_NOT_FOUND: 'user_not_found',
  EMAIL_NOT_VERIFIED: 'email_not_verified',
  
  // Session Errors
  SESSION_NOT_FOUND: 'session_not_found',
  SESSION_ALREADY_STARTED: 'session_already_started',
  NO_ACTIVE_SESSION: 'no_active_session',
  SESSION_ALREADY_FINISHED: 'session_already_finished',
  
  // Exercise Errors
  EXERCISE_NOT_FOUND: 'exercise_not_found',
  INVALID_EXERCISE_DATA: 'invalid_exercise_data',
  
  // Program Errors
  PROGRAM_NOT_FOUND: 'program_not_found',
  WEEK_NOT_FOUND: 'week_not_found',
  
  // Network Errors
  NETWORK_ERROR: 'network_error',
  SERVER_ERROR: 'server_error',
  TIMEOUT_ERROR: 'timeout_error',
  
  // Validation Errors
  VALIDATION_ERROR: 'validation_error',
  RATE_LIMIT_EXCEEDED: 'rate_limit_exceeded'
};

// ===========================
// CONSTANTES DE CONFIGURACIÓN
// ===========================

// Rate Limits
export const RATE_LIMITS = {
  GENERAL: 100, // requests per minute
  AUTH: 10,     // requests per minute
  CHAT: 30      // requests per minute
};

// Configuración de paginación
export const PAGINATION_DEFAULTS = {
  PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100
};

// Rangos de validación
export const VALIDATION_RULES = {
  email: {
    required: true,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message: "Email debe tener formato válido"
  },
  
  password: {
    required: true,
    minLength: 8,
    pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]+$/,
    message: "Password debe tener al menos 8 caracteres con letras y números"
  },
  
  weight: {
    required: true,
    min: 0.5,
    max: 999,
    step: 0.5,
    message: "Peso debe estar entre 0.5 y 999 kg"
  },
  
  reps: {
    required: true,
    min: 1,
    max: 100,
    message: "Repeticiones deben estar entre 1 y 100"
  },
  
  rpe: {
    required: false,
    min: 6,
    max: 10,
    step: 0.5,
    message: "RPE debe estar entre 6 y 10"
  },
  
  rir: {
    required: false,
    min: 0,
    max: 10,
    message: "RIR debe estar entre 0 y 10"
  }
};

// Patrones de tempo
export const TEMPO_PATTERNS = {
  basic: /^\d-\d-\d-\d$/, // e.g., "2-1-2-1"
  advanced: /^\d{1,2}-\d{1,2}-\d{1,2}-\d{1,2}$/ // e.g., "10-1-3-1"
};

// ===========================
// CLASES DE VALIDACIÓN
// ===========================

export class Validator {
  static validateExerciseLog(data) {
    const errors = [];

    // Validar campos requeridos
    if (!data.exercise_name) {
      errors.push({ field: 'exercise_name', message: 'Nombre del ejercicio es requerido' });
    }

    if (!data.repetitions_done || data.repetitions_done < 1) {
      errors.push({ field: 'repetitions_done', message: 'Repeticiones debe ser al menos 1' });
    }

    // Validar coherencia entre RPE y RIR
    if (data.perceived_rpe && data.perceived_rir) {
      if (data.perceived_rpe >= 9 && data.perceived_rir > 2) {
        errors.push({ 
          field: 'perceived_rir', 
          message: 'RIR inconsistente con RPE alto' 
        });
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  static validateEmail(email) {
    if (!email) return { isValid: false, message: VALIDATION_RULES.email.message };
    return {
      isValid: VALIDATION_RULES.email.pattern.test(email),
      message: VALIDATION_RULES.email.message
    };
  }

  static validatePassword(password) {
    if (!password) return { isValid: false, message: VALIDATION_RULES.password.message };
    return {
      isValid: password.length >= VALIDATION_RULES.password.minLength && 
               VALIDATION_RULES.password.pattern.test(password),
      message: VALIDATION_RULES.password.message
    };
  }
}

export class TempoValidator {
  static validate(tempo) {
    if (!tempo) return true; // Tempo es opcional
    
    return TEMPO_PATTERNS.basic.test(tempo) || TEMPO_PATTERNS.advanced.test(tempo);
  }

  static parse(tempo) {
    if (!this.validate(tempo)) return null;
    
    const [eccentric, pause1, concentric, pause2] = tempo.split('-').map(Number);
    
    return {
      eccentric,    // Fase excéntrica (bajada)
      pause1,       // Pausa en posición inferior
      concentric,   // Fase concéntrica (subida)
      pause2        // Pausa en posición superior
    };
  }
}

// ===========================
// CLASE DE ERROR PERSONALIZADA
// ===========================

export class ApiError extends Error {
  constructor(code, message, details = null, status = null) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.details = details;
    this.status = status;
  }

  static fromResponse(error) {
    const status = error.response?.status;
    const data = error.response?.data;
    
    if (status === 401) {
      return new ApiError(ErrorCode.TOKEN_EXPIRED, 'Token expirado', data, status);
    }
    
    if (status === 404) {
      return new ApiError(ErrorCode.EXERCISE_NOT_FOUND, 'Recurso no encontrado', data, status);
    }
    
    if (status === 429) {
      return new ApiError(ErrorCode.RATE_LIMIT_EXCEEDED, 'Límite de solicitudes excedido', data, status);
    }
    
    if (status >= 500) {
      return new ApiError(ErrorCode.SERVER_ERROR, 'Error del servidor', data, status);
    }
    
    return new ApiError(ErrorCode.NETWORK_ERROR, error.message, data, status);
  }
}

// ===========================
// TRADUCCIONES
// ===========================

export const TRANSLATIONS = {
  es: {
    common: {
      save: "Guardar",
      cancel: "Cancelar",
      delete: "Eliminar",
      edit: "Editar",
      loading: "Cargando...",
      error: "Error",
      success: "Éxito"
    },
    auth: {
      login: "Iniciar Sesión",
      register: "Registrarse",
      logout: "Cerrar Sesión",
      forgot_password: "¿Olvidaste tu contraseña?"
    },
    exercises: {
      weight: "Peso",
      reps: "Repeticiones",
      sets: "Series",
      rest: "Descanso",
      rpe: "Esfuerzo Percibido (RPE)",
      rir: "Repeticiones en Reserva (RIR)",
      tempo: "Tempo",
      notes: "Notas"
    },
    programs: {
      hypertrophy: "Hipertrofia",
      strength: "Fuerza",
      peaking: "Pico",
      week: "Semana",
      session: "Sesión",
      view_sessions: "Ver Sesiones",
      view_details: "Ver Detalles"
    },
    errors: {
      [ErrorCode.INVALID_CREDENTIALS]: "Credenciales inválidas",
      [ErrorCode.TOKEN_EXPIRED]: "Sesión expirada",
      [ErrorCode.USER_NOT_FOUND]: "Usuario no encontrado",
      [ErrorCode.EMAIL_NOT_VERIFIED]: "Email no verificado",
      [ErrorCode.SESSION_NOT_FOUND]: "Sesión no encontrada",
      [ErrorCode.SESSION_ALREADY_STARTED]: "Sesión ya iniciada",
      [ErrorCode.NO_ACTIVE_SESSION]: "No hay sesión activa",
      [ErrorCode.SESSION_ALREADY_FINISHED]: "Sesión ya finalizada",
      [ErrorCode.EXERCISE_NOT_FOUND]: "Ejercicio no encontrado",
      [ErrorCode.INVALID_EXERCISE_DATA]: "Datos de ejercicio inválidos",
      [ErrorCode.PROGRAM_NOT_FOUND]: "Programa no encontrado",
      [ErrorCode.WEEK_NOT_FOUND]: "Semana no encontrada",
      [ErrorCode.NETWORK_ERROR]: "Error de conexión",
      [ErrorCode.SERVER_ERROR]: "Error del servidor",
      [ErrorCode.TIMEOUT_ERROR]: "Tiempo de espera agotado",
      [ErrorCode.VALIDATION_ERROR]: "Error de validación",
      [ErrorCode.RATE_LIMIT_EXCEEDED]: "Límite de solicitudes excedido"
    }
  }
};

// ===========================
// FORMATEADORES
// ===========================

export class LocaleFormatter {
  constructor(locale = 'es-ES') {
    this.locale = locale;
  }

  formatDate(date) {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(this.locale, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    }).format(dateObj);
  }

  formatTime(date) {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return new Intl.DateTimeFormat(this.locale, {
      hour: '2-digit',
      minute: '2-digit'
    }).format(dateObj);
  }

  formatWeight(weight, unit) {
    return `${weight.toFixed(1)} ${unit}`;
  }

  formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
}
