import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Modal,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { FontAwesome5, Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS } from '../../src/constants/theme';
import { useTrainingPrograms } from '../../src/hooks/useTrainingPrograms';
import { useSessions } from '../../src/hooks/useSessions';
import { useSessionStore } from '../../src/store/sessionStore';
import { Validator, VALIDATION_RULES, TRANSLATIONS, LocaleFormatter } from '../../src/types/api';
import InputField from '../../src/components/InputField';
import { useActiveSession } from '../../src/contexts/ActiveSessionContext';

export default function SessionExercises() {
  const router = useRouter();
  const { programId, sessionId, sessionName, weekNumber } = useLocalSearchParams();
  const insets = useSafeAreaInsets();
  const [sessionData, setSessionData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionLogs, setSessionLogs] = useState([]);
  const [showLogModal, setShowLogModal] = useState(false);
  const [showActiveSessionModal, setShowActiveSessionModal] = useState(false);
  const [conflictingSession, setConflictingSession] = useState(null);
  const [selectedExercise, setSelectedExercise] = useState(null);
  const [currentSet, setCurrentSet] = useState(1);
  const [logData, setLogData] = useState({
    repetitions_done: '',
    used_weight: '',
    used_weight_unit: 'kg',
    perceived_rir: '',
    notes: '',
  });
  const [validationErrors, setValidationErrors] = useState({});

  // Inicializar formateador de localización
  const formatter = new LocaleFormatter();

  // USAR SOLO EL STORE - ELIMINAR DUPLICACIÓN
  const { activeSession } = useSessionStore();

  // Hook del contexto SOLO para funciones, NO para estado
  const { 
    updateSessionInfo, 
    clearSession: clearGlobalSession,
    refreshActiveSession,
    setViewingActiveSessionState 
  } = useActiveSession();

  const { getSessionDetails } = useTrainingPrograms();
  const { 
    startSession, 
    finishSession, 
    logStrengthExercise, 
    getSessionLogs,
    getActiveSession,
    isLoading: sessionLoading 
  } = useSessions();
  
  useEffect(() => {
    // Validar que tenemos los parámetros necesarios
    if (!programId || !sessionId) {
      setError('Faltan parámetros requeridos para cargar la sesión');
      setIsLoading(false);
      return;
    }
    
    // Validar que los IDs son números válidos
    const programIdNum = parseInt(programId);
    const sessionIdNum = parseInt(sessionId);
    
    if (isNaN(programIdNum) || isNaN(sessionIdNum)) {
      setError('Los identificadores del programa y sesión deben ser números válidos');
      setIsLoading(false);
      return;
    }
    
    loadSessionData();
  }, [programId, sessionId]);

  // Efecto simple para establecer si estamos viendo la sesión activa
  useEffect(() => {
    const currentSessionId = parseInt(sessionId);
    const isViewingActive = activeSession && activeSession.id === currentSessionId;
    
    console.log('🎯 Actualizando viewingActiveSession:', {
      activeSessionId: activeSession?.id,
      currentSessionId,
      isViewingActive
    });
    
    setViewingActiveSessionState(isViewingActive);
  }, [activeSession, sessionId, setViewingActiveSessionState]);

  // Efecto para limpiar el estado cuando se desmonta el componente
  useEffect(() => {
    return () => {
      // Limpiar el estado de visualización cuando salimos de la pantalla
      setViewingActiveSessionState(false);
    };
  }, [setViewingActiveSessionState]);

  // Efecto para manejar el modal de conflicto
  useEffect(() => {
    if (!sessionData) return; // Esperar a que se carguen los datos de la sesión
    
    const currentSessionId = parseInt(sessionId);
    
    console.log('🔍 MODAL CONFLICT CHECK:', {
      hasActiveSession: !!activeSession,
      activeSessionId: activeSession?.id,
      currentSessionId,
      sessionIdType: typeof sessionId,
      sessionIdParsed: currentSessionId
    });
    
    if (activeSession) {
      const isCurrentSessionActive = activeSession.id === currentSessionId;
      
      console.log('🔍 SESSION COMPARISON:', {
        activeSessionId: activeSession.id,
        currentSessionId,
        isCurrentSessionActive,
        strictEqual: activeSession.id === currentSessionId,
        looseEqual: activeSession.id == currentSessionId
      });
      
      if (!isCurrentSessionActive) {
        // Hay una sesión activa diferente - mostrar modal
        console.log(`⚠️ Mostrando modal de conflicto: sesión activa ${activeSession.id} vs actual ${currentSessionId}`);
        setConflictingSession(activeSession);
        setShowActiveSessionModal(true);
      } else {
        // La sesión actual ES la activa - cargar logs si es necesario
        console.log(`✅ Sesión actual coincide con la activa: ${currentSessionId}`);
        if (sessionLogs.length === 0) {
          loadSessionLogs();
        }
        // Asegurar que el modal esté cerrado
        if (showActiveSessionModal) {
          console.log('🧹 Cerrando modal - sesiones coinciden');
          setShowActiveSessionModal(false);
          setConflictingSession(null);
        }
      }
    } else {
      // No hay sesión activa - limpiar modal si estaba abierto
      if (showActiveSessionModal) {
        console.log(`🧹 Cerrando modal - no hay sesión activa`);
        setShowActiveSessionModal(false);
        setConflictingSession(null);
      }
    }
  }, [activeSession, sessionData, sessionId]);

  const loadSessionLogs = async () => {
    try {
      const logs = await getSessionLogs();
      setSessionLogs(logs);
    } catch (error) {
      console.error('Error loading session logs:', error);
    }
  };

  const loadSessionData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log(`Cargando detalles de sesión: programId=${programId}, sessionId=${sessionId}`);
      const sessionDetails = await getSessionDetails(programId, sessionId);
      
      setSessionData(sessionDetails);
      
      // Refrescar el contexto global para asegurar datos actualizados
      await refreshActiveSession();
      
      // El manejo del estado activo se hace ahora en el useEffect que escucha globalActiveSession
      
    } catch (err) {
      console.error(`Error al obtener detalles de sesión ${sessionId}:`, err);
      if (err.message && err.message.includes('Recurso no encontrado')) {
        setError('La sesión solicitada no existe o ha sido eliminada');
      } else {
        setError('No se pudo cargar los datos de la sesión');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartSession = async () => {
    try {
      const currentSessionId = parseInt(sessionId);
      
      // Verificar si hay sesión activa conflictiva
      if (activeSession && activeSession.id !== currentSessionId) {
        setConflictingSession(activeSession);
        setShowActiveSessionModal(true);
        return;
      }
      
      console.log('🚀 Iniciando sesión...');
      const sessionResponse = await startSession(sessionId);
      
      if (sessionResponse) {
        console.log('✅ Sesión iniciada:', sessionResponse);
        
        // Verificar que tenemos el ID correcto
        console.log('🔍 Verificando ID de sesión:', {
          sessionResponseId: sessionResponse.id,
          expectedId: currentSessionId
        });
        
        // El hook ya actualiza el store automáticamente
        // Solo necesitamos establecer que estamos viendo la sesión activa
        setViewingActiveSessionState(true);
        
        // Actualizar programId si es necesario
        if (programId) {
          updateSessionInfo(sessionResponse, programId);
        }
        
        Alert.alert('¡Sesión iniciada!', 'Ya puedes comenzar a registrar tus ejercicios.');
      }
    } catch (error) {
      console.error('Error al iniciar sesión:', error);
      Alert.alert('Error', 'No se pudo iniciar la sesión');
    }
  };

  const handleFinishSession = async () => {
    Alert.alert(
      'Finalizar Sesión',
      '¿Estás seguro de que quieres finalizar esta sesión de entrenamiento?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Finalizar',
          style: 'destructive',
          onPress: async () => {
            try {
              await finishSession(); // Sin parámetro sessionId según la API
              // Limpiar todos los estados de sesión activa
              setSessionLogs([]);
              setConflictingSession(null);
              setShowActiveSessionModal(false);
              
              // Limpiar el contexto global
              clearGlobalSession();
              
              // Limpiar el estado de visualización
              setViewingActiveSessionState(false);
              
              Alert.alert('¡Sesión finalizada!', 'Tu entrenamiento ha sido completado.');
              if (weekNumber) {
                router.push({
                  pathname: '/week-sessions',
                  params: { 
                    programId: programId.toString(),
                    weekNumber: weekNumber.toString()
                  }
                });
              } else {
                router.back();
              }
            } catch (error) {
              Alert.alert('Error', 'No se pudo finalizar la sesión');
            }
          },
        },
      ]
    );
  };

  // Manejar el modal de sesión activa conflictiva
  const handleFinishConflictingSession = async () => {
    try {
      await finishSession();
      // Limpiar todos los estados relacionados con sesiones conflictivas
      setConflictingSession(null);
      setShowActiveSessionModal(false);
      // Los logs se limpian automáticamente cuando se limpia la sesión
      setSessionLogs([]);
      
      // Limpiar el contexto global
      clearGlobalSession();
      
      // Limpiar el estado de visualización
      setViewingActiveSessionState(false);
      
      Alert.alert('Sesión anterior finalizada', 'Ahora puedes iniciar esta sesión si lo deseas.');
    } catch (error) {
      Alert.alert('Error', 'No se pudo finalizar la sesión anterior');
    }
  };

  const handleGoToActiveSession = () => {
    setShowActiveSessionModal(false);
    
    // Navegar a la sesión activa
    if (conflictingSession && conflictingSession.id !== parseInt(sessionId)) {
      router.push({
        pathname: '/session-exercises',
        params: { 
          programId: programId.toString(),
          sessionId: conflictingSession.id.toString(),
          sessionName: conflictingSession.name
        }
      });
    }
  };

  const handleContinueViewing = () => {
    // Simplemente cerrar el modal y permitir ver la sesión sin iniciarla
    // El estado activeSession se mantiene como está (no es la sesión actual)
    setShowActiveSessionModal(false);
    setConflictingSession(null);
    // NO cambiar viewingActiveSession porque no estamos viendo la sesión activa
    setSessionLogs([]);
  };

  const handleDismissModal = () => {
    setShowActiveSessionModal(false);
    setConflictingSession(null);
  };

  const handleExercisePress = (exercise, exerciseIndex, blockIndex) => {
    if (!activeSession) {
      Alert.alert('Sesión no iniciada', 'Debes iniciar la sesión para registrar ejercicios.');
      return;
    }
    
    setSelectedExercise({ 
      ...exercise, 
      exercise_index: exerciseIndex, 
      block_index: blockIndex 
    });
    setCurrentSet(1);
    setLogData({
      repetitions_done: '',
      used_weight: '',
      used_weight_unit: 'kg',
      perceived_rir: '',
      notes: '',
    });
    setShowLogModal(true);
  };

  const validateLogData = (data) => {
    const errors = {};
    
    // Validar repeticiones
    const reps = parseInt(data.repetitions_done);
    if (!data.repetitions_done || isNaN(reps) || reps < VALIDATION_RULES.reps.min || reps > VALIDATION_RULES.reps.max) {
      errors.repetitions_done = VALIDATION_RULES.reps.message;
    }
    
    // Validar peso
    const weight = parseFloat(data.used_weight);
    if (!data.used_weight || isNaN(weight) || weight < VALIDATION_RULES.weight.min || weight > VALIDATION_RULES.weight.max) {
      errors.used_weight = VALIDATION_RULES.weight.message;
    }
    
    // Validar RIR si está presente
    if (data.perceived_rir) {
      const rir = parseInt(data.perceived_rir);
      if (isNaN(rir) || rir < VALIDATION_RULES.rir.min || rir > VALIDATION_RULES.rir.max) {
        errors.perceived_rir = VALIDATION_RULES.rir.message;
      }
    }
    
    return errors;
  };

  const handleSaveLog = async () => {
    // Validar datos antes de enviar
    const errors = validateLogData(logData);
    setValidationErrors(errors);
    
    if (Object.keys(errors).length > 0) {
      Alert.alert('Error de Validación', 'Por favor corrige los errores en el formulario.');
      return;
    }

    try {
      const exerciseData = {
        standard_exercise_id: selectedExercise.standard_exercise_id,
        set_number: currentSet,
        repetitions_done: parseInt(logData.repetitions_done),
        used_weight: parseFloat(logData.used_weight),
        used_weight_unit: logData.used_weight_unit,
        perceived_rir: logData.perceived_rir ? parseInt(logData.perceived_rir) : null,
        notes: logData.notes || null,
      };

      // Usar la validación del guide para ejercicios
      const validation = Validator.validateExerciseLog({
        exercise_name: selectedExercise.exercise_name,
        repetitions_done: exerciseData.repetitions_done,
        perceived_rpe: null, // No tenemos RPE en este caso
        perceived_rir: exerciseData.perceived_rir
      });

      if (!validation.isValid) {
        Alert.alert('Error de Validación', validation.errors.map(e => e.message).join('\n'));
        return;
      }

      const result = await logStrengthExercise(exerciseData);
      if (result) {
        // La API devuelve { message, log, programmed_sets, completed_sets, remaining_sets }
        setSessionLogs(prev => [...prev, result.log]);
        
        // Si hay más sets, pasar al siguiente
        if (currentSet < selectedExercise.sets) {
          setCurrentSet(currentSet + 1);
          setLogData({
            repetitions_done: '',
            used_weight: logData.used_weight, // Mantener el peso anterior
            used_weight_unit: logData.used_weight_unit,
            perceived_rir: '',
            notes: '',
          });
          setValidationErrors({});
        } else {
          setShowLogModal(false);
        }
      }
    } catch (error) {
      Alert.alert('Error', error.message || 'No se pudo registrar el ejercicio');
    }
  };

  const getCompletedSets = (exerciseId) => {
    return sessionLogs.filter(log => log.standard_exercise_id === exerciseId).length;
  };

  const renderExercise = (exercise, exerciseIndex, blockIndex) => {
    const completedSets = getCompletedSets(exercise.standard_exercise_id);
    const totalSets = exercise.sets;
    const isCompleted = completedSets >= totalSets;

    return (
      <TouchableOpacity
        key={`${blockIndex}-${exerciseIndex}`}
        style={[styles.exerciseCard, isCompleted && styles.completedExercise]}
        onPress={() => handleExercisePress(exercise, exerciseIndex, blockIndex)}
      >
        <View style={styles.exerciseHeader}>
          <Text style={styles.exerciseName} numberOfLines={2}>
            {exercise.exercise_name || exercise.standard_exercise?.standard_name || exercise.fullExercise?.standard_exercise?.standard_name || `Ejercicio #${exerciseIndex + 1}`}
          </Text>
          <View style={styles.progressContainer}>
            <Text style={styles.progressText}>
              {completedSets}/{totalSets}
            </Text>
            {isCompleted && (
              <Ionicons name="checkmark-circle" size={20} color={COLORS.success} />
            )}
          </View>
        </View>
        
        <View style={styles.exerciseSpecs}>
          <Text style={styles.specsText}>
            📊 {exercise.sets} series × {exercise.reps} repeticiones
          </Text>
          {exercise.load_type && (
            <Text style={styles.specsText}>
              💪 {exercise.load_type === 'rpe' ? `RPE ${exercise.rpe_target}` : 
                   exercise.load_type === 'percentage' ? `${exercise.percentage_1rm}% 1RM` :
                   exercise.weight_range || 'Peso libre'}
            </Text>
          )}
          {exercise.rest_seconds && (
            <Text style={styles.specsText}>
              ⏱️ Descanso: {Math.floor(exercise.rest_seconds / 60)}:{String(exercise.rest_seconds % 60).padStart(2, '0')} min
            </Text>
          )}
          {exercise.tempo && (
            <Text style={styles.specsText}>
              🎵 Tempo: {exercise.tempo}
            </Text>
          )}
        </View>
      </TouchableOpacity>
    );
  };

  const renderBlock = (block, blockIndex) => (
    <View key={blockIndex} style={styles.blockContainer}>
      <View style={styles.blockHeader}>
        <Text style={styles.blockTitle}>{block.name}</Text>
        <View style={[
          styles.blockTypeTag,
          block.block_type === 'main' ? styles.mainBlockTag : styles.accessoryBlockTag
        ]}>
          <Text style={styles.blockTypeText}>
            {block.block_type === 'main' ? 'Principal' : 'Accesorio'}
          </Text>
        </View>
      </View>
      
      {block.description && (
        <Text style={styles.blockDescription}>{block.description}</Text>
      )}
      
      <View style={styles.exercisesContainer}>
        {block.programmed_exercises.map((exercise, exerciseIndex) => 
          renderExercise(exercise, exerciseIndex, blockIndex)
        )}
      </View>
    </View>
  );

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.primary} />
          <Text style={styles.loadingText}>Cargando ejercicios...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error || !sessionData) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <FontAwesome5 name="exclamation-triangle" size={48} color={COLORS.error} />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadSessionData}>
            <Text style={styles.retryText}>Reintentar</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={[
        styles.header, 
        { 
          // paddingTop: insets.top + SPACING.sm,
          // paddingBottom: sessionPadding > 0 ? SPACING.lg : SPACING.sm
        }
      ]}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => {
            if (weekNumber) {
              router.push({
                pathname: '/week-sessions',
                params: { 
                  programId: programId.toString(),
                  weekNumber: weekNumber.toString()
                }
              });
            } else {
              router.back();
            }
          }}
        >
          <Ionicons name="arrow-back" size={24} color={COLORS.textDark} />
        </TouchableOpacity>
        <View style={styles.headerContent}>
          <Text style={styles.title} numberOfLines={1}>
            {sessionName}
          </Text>
          <Text style={styles.subtitle}>
            {sessionData.exercise_blocks?.length || 0} bloques • {
              sessionData.exercise_blocks?.reduce((total, block) => 
                total + (block.programmed_exercises?.length || 0), 0) || 0
            } ejercicios
          </Text>
        </View>
        {/* 
          Lógica del botón CORREGIDA:
          - Si NO hay sesión activa → mostrar "Iniciar"
          - Si hay sesión activa Y es la MISMA sesión → mostrar "Finalizar"
          - Si hay sesión activa PERO es DIFERENTE → mostrar "Iniciar" (se manejará el conflicto en el modal)
        */}
        {(() => {
          const currentSessionId = parseInt(sessionId);
          const isCurrentSessionActive = activeSession && activeSession.id === currentSessionId;
          
          console.log(`🔘 Debug botón - activeSession: ${activeSession ? `ID: ${activeSession.id}` : 'null'}, sessionId actual: ${sessionId}, isCurrentSessionActive: ${isCurrentSessionActive}`);
          
          if (isCurrentSessionActive) {
            // La sesión actual ES la activa → "Finalizar"
            return (
              <TouchableOpacity style={styles.finishButton} onPress={handleFinishSession}>
                <Ionicons name="checkmark" size={20} color={COLORS.background} />
                <Text style={styles.finishButtonText}>Finalizar</Text>
              </TouchableOpacity>
            );
          } else {
            // No hay sesión activa O hay una sesión activa diferente → "Iniciar"
            return (
              <TouchableOpacity style={styles.startButton} onPress={handleStartSession}>
                <Ionicons name="play" size={20} color={COLORS.background} />
                <Text style={styles.startButtonText}>Iniciar</Text>
              </TouchableOpacity>
            );
          }
        })()}
      </View>

      <ScrollView 
        style={styles.content} 
        contentContainerStyle={{ 
          // paddingTop: sessionPadding + (sessionPadding > 0 ? SPACING.xl : SPACING.md),
          // paddingBottom: insets.bottom + SPACING.lg 
        }}
        showsVerticalScrollIndicator={false}
      >
        {sessionData.exercise_blocks?.map((block, blockIndex) => 
          renderBlock(block, blockIndex)
        )}
      </ScrollView>

      {/* Modal para registrar sets */}
      <Modal
        visible={showLogModal}
        transparent={true}
        animationType="slide"
        onRequestClose={() => setShowLogModal(false)}
      >
        <SafeAreaView style={styles.modalOverlay}>
          <View style={[styles.modalContent, { marginTop: insets.top, marginBottom: insets.bottom }]}>
            <Text style={styles.modalTitle}>
              Registrar Set {currentSet}
            </Text>
            <Text style={styles.modalSubtitle}>
              {selectedExercise?.exercise_name || selectedExercise?.standard_exercise?.name || `Ejercicio #${selectedExercise?.exercise_index + 1 || ''}`}
            </Text>
            
            <View style={styles.inputRow}>
              <View style={styles.inputHalf}>
                <Text style={styles.inputLabel}>
                  {TRANSLATIONS.es.exercises.reps} *
                </Text>
                <InputField
                  value={logData.repetitions_done}
                  onChangeText={(value) => {
                    setLogData(prev => ({...prev, repetitions_done: value}));
                    if (validationErrors.repetitions_done) {
                      setValidationErrors(prev => ({...prev, repetitions_done: null}));
                    }
                  }}
                  placeholder="12"
                  keyboardType="numeric"
                  error={validationErrors.repetitions_done}
                />
                {validationErrors.repetitions_done && (
                  <Text style={styles.errorText}>{validationErrors.repetitions_done}</Text>
                )}
              </View>
              <View style={styles.inputHalf}>
                <Text style={styles.inputLabel}>
                  {TRANSLATIONS.es.exercises.weight} * ({logData.used_weight_unit})
                </Text>
                <InputField
                  value={logData.used_weight}
                  onChangeText={(value) => {
                    setLogData(prev => ({...prev, used_weight: value}));
                    if (validationErrors.used_weight) {
                      setValidationErrors(prev => ({...prev, used_weight: null}));
                    }
                  }}
                  placeholder="80"
                  keyboardType="numeric"
                  error={validationErrors.used_weight}
                />
                {validationErrors.used_weight && (
                  <Text style={styles.errorText}>{validationErrors.used_weight}</Text>
                )}
              </View>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {TRANSLATIONS.es.exercises.rir}
              </Text>
              <InputField
                value={logData.perceived_rir}
                onChangeText={(value) => {
                  setLogData(prev => ({...prev, perceived_rir: value}));
                  if (validationErrors.perceived_rir) {
                    setValidationErrors(prev => ({...prev, perceived_rir: null}));
                  }
                }}
                placeholder="2"
                keyboardType="numeric"
                error={validationErrors.perceived_rir}
              />
              {validationErrors.perceived_rir && (
                <Text style={styles.errorText}>{validationErrors.perceived_rir}</Text>
              )}
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>
                {TRANSLATIONS.es.exercises.notes}
              </Text>
              <InputField
                value={logData.notes}
                onChangeText={(value) => setLogData(prev => ({...prev, notes: value}))}
                placeholder="Notas opcionales..."
                multiline
                numberOfLines={3}
              />
            </View>

            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setShowLogModal(false)}
              >
                <Text style={styles.cancelButtonText}>Cancelar</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.saveButton}
                onPress={handleSaveLog}
              >
                <Text style={styles.saveButtonText}>Guardar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </SafeAreaView>
      </Modal>

      {/* Modal de sesión activa conflictiva */}
      <Modal
        visible={showActiveSessionModal}
        transparent={true}
        animationType="fade"
        onRequestClose={handleDismissModal}
        statusBarTranslucent={true}
      >
        <SafeAreaView style={styles.modalOverlay}>
          <View style={styles.activeSessionModalContent}>
            <View style={styles.modalHeader}>
              <Ionicons name="warning" size={32} color={COLORS.warning} />
              <Text style={styles.modalTitle}>Sesión Activa Detectada</Text>
            </View>
            
            <Text style={styles.modalDescription}>
              Tienes una sesión de entrenamiento activa que debe ser finalizada antes de iniciar una nueva.
            </Text>
            
            {conflictingSession && (
              <View style={styles.conflictingSessionInfo}>
                <Text style={styles.conflictingSessionName}>
                  📋 {conflictingSession.name}
                </Text>
                <Text style={styles.conflictingSessionDetails}>
                  ⏰ Iniciada: {new Date(conflictingSession.start_time).toLocaleTimeString()}
                </Text>
              </View>
            )}
            
            <Text style={styles.modalQuestion}>
              Selecciona una acción:
            </Text>
            
            <View style={styles.modalActionsColumn}>
              <TouchableOpacity 
                style={styles.continueViewingButton} 
                onPress={handleContinueViewing}
              >
                <Ionicons name="eye" size={20} color="white" />
                <Text style={styles.continueViewingButtonText}>Continuar (solo ver)</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={styles.goToActiveSessionButton} 
                onPress={handleGoToActiveSession}
              >
                <Ionicons name="arrow-forward" size={20} color="white" />
                <Text style={styles.goToActiveSessionButtonText}>Ir a sesión activa</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={styles.finishActiveSessionButton} 
                onPress={handleFinishConflictingSession}
              >
                <Ionicons name="checkmark-done" size={20} color="white" />
                <Text style={styles.finishActiveSessionButtonText}>Finalizar sesión activa</Text>
              </TouchableOpacity>
            </View>
          </View>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.card,
    ...SHADOWS.small,
  },
  backButton: {
    padding: SPACING.xs,
    marginRight: SPACING.sm,
  },
  headerContent: {
    flex: 1,
  },
  title: {
    fontSize: FONT_SIZE.lg,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  subtitle: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  startButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.success,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
    gap: SPACING.xs,
  },
  startButtonText: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.background,
  },
  finishButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.error,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
    gap: SPACING.xs,
  },
  finishButtonText: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.background,
  },
  content: {
    flex: 1,
    padding: SPACING.md,
  },
  blockContainer: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.md,
    marginBottom: SPACING.md,
    ...SHADOWS.small,
  },
  blockHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  blockTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: 'bold',
    color: COLORS.textDark,
    flex: 1,
  },
  blockTypeTag: {
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    borderRadius: BORDER_RADIUS.sm,
  },
  mainBlockTag: {
    backgroundColor: COLORS.primary,
  },
  accessoryBlockTag: {
    backgroundColor: COLORS.secondary,
  },
  blockTypeText: {
    fontSize: FONT_SIZE.xs,
    fontWeight: '600',
    color: COLORS.background,
  },
  blockDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    marginBottom: SPACING.md,
    fontStyle: 'italic',
  },
  exercisesContainer: {
    gap: SPACING.sm,
  },
  exerciseCard: {
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  completedExercise: {
    borderColor: COLORS.success,
    backgroundColor: `${COLORS.success}10`,
  },
  exerciseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
  },
  exerciseName: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textDark,
    flex: 1,
    marginRight: SPACING.sm,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  progressText: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.primary,
  },
  exerciseSpecs: {
    gap: SPACING.xs,
  },
  specsText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    marginTop: SPACING.md,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: SPACING.xl,
  },
  errorText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.error,
    textAlign: 'center',
    marginVertical: SPACING.md,
  },
  retryButton: {
    backgroundColor: COLORS.primary,
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
  },
  retryText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.background,
    fontWeight: '600',
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
    height: '100%',
  },
  modalContent: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.lg,
    width: '100%',
    maxWidth: 400,
  },
  modalTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: 'bold',
    color: COLORS.textDark,
    textAlign: 'center',
    marginBottom: SPACING.xs,
  },
  modalSubtitle: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    textAlign: 'center',
    marginBottom: SPACING.lg,
  },
  inputRow: {
    flexDirection: 'row',
    gap: SPACING.md,
    marginBottom: SPACING.md,
  },
  inputHalf: {
    flex: 1,
  },
  inputGroup: {
    marginBottom: SPACING.md,
  },
  inputLabel: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  errorText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.error,
    marginTop: SPACING.xs,
  },
  modalActions: {
    flexDirection: 'row',
    gap: SPACING.md,
    marginTop: SPACING.md,
  },
  modalActionsColumn: {
    flexDirection: 'column',
    width: '100%',
    marginTop: SPACING.lg,
  },
  saveButton: {
    flex: 1,
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
  },
  saveButtonText: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.background,
  },
  // Estilos para el modal de sesión activa
  activeSessionModalContent: {
    backgroundColor: '#1A1A1A', // Fondo oscuro para mejor contraste
    marginHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.xl,
    width: '95%',
    maxWidth: 550,
    ...SHADOWS.large,
    // Sombra más pronunciada para destacar sobre el fondo
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 6,
    },
    shadowOpacity: 0.37,
    shadowRadius: 7.49,
    elevation: 12,
  },
  modalHeader: {
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  modalTitle: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: 'white',
    marginTop: SPACING.sm,
  },
  modalDescription: {
    fontSize: FONT_SIZE.md,
    color: '#CCC', // Color claro para texto en fondo oscuro
    textAlign: 'center',
    marginBottom: SPACING.md,
  },
  conflictingSessionInfo: {
    backgroundColor: '#333', // Fondo más oscuro para el contenedor de información
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    marginBottom: SPACING.md,
    marginTop: SPACING.sm,
    borderLeftWidth: 4,
    borderLeftColor: COLORS.warning,
  },
  conflictingSessionName: {
    fontSize: FONT_SIZE.md,
    fontWeight: 'bold',
    color: 'white',
    marginBottom: SPACING.xs,
  },
  conflictingSessionDetails: {
    fontSize: FONT_SIZE.sm,
    color: '#CCC', // Color claro para texto en fondo oscuro
  },
  modalQuestion: {
    fontSize: FONT_SIZE.md,
    color: 'white',
    textAlign: 'center',
    marginBottom: SPACING.lg,
    fontWeight: '600',
  },
  continueButton: {
    backgroundColor: '#F29A2E', // Color naranja como en la imagen de referencia
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: SPACING.xs,
    marginBottom: SPACING.md,
    minHeight: 48,
    width: '100%',
  },
  continueButtonText: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: 'white',
    textAlign: 'center',
  },
  // Nuevos estilos para los botones del modal actualizado
  continueViewingButton: {
    backgroundColor: '#6B7280', // Color gris para "solo ver"
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: SPACING.xs,
    marginBottom: SPACING.md,
    minHeight: 48,
    width: '100%',
  },
  continueViewingButtonText: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: 'white',
    textAlign: 'center',
  },
  goToActiveSessionButton: {
    backgroundColor: '#3B82F6', // Color azul para "ir a sesión activa"
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: SPACING.xs,
    marginBottom: SPACING.md,
    minHeight: 48,
    width: '100%',
  },
  goToActiveSessionButtonText: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: 'white',
    textAlign: 'center',
  },
  finishActiveSessionButton: {
    backgroundColor: '#EF4444', // Color rojo para "finalizar sesión activa"
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: SPACING.xs,
    marginBottom: SPACING.sm,
    minHeight: 48,
    width: '100%',
  },
  finishActiveSessionButtonText: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: 'white',
    textAlign: 'center',
  },
  activeSessionFinishButton: {
    backgroundColor: '#41A85F', // Color verde como en la imagen de referencia
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    flexDirection: 'row',
    justifyContent: 'center',
    minHeight: 48,
    width: '100%',
    alignItems: 'center',
    gap: SPACING.xs,
    marginBottom: SPACING.sm,
  },
  activeSessionFinishButtonText: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: 'white',
    textAlign: 'center',
  },
  cancelButton: {
    backgroundColor: COLORS.input,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textMedium,
  },
});
