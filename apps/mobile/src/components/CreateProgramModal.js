import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Dimensions,
} from 'react-native';
import { Ionicons, FontAwesome5 } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS } from '../constants/theme';
import { useTrainingPrograms } from '../hooks/useTrainingPrograms';
import { exerciseService } from '../services/apiService';
import Button from './Button';
import LoadingIndicator from './LoadingIndicator';
import CreateProgramBasicInfo from './CreateProgramBasicInfo';
import CreateProgramWeeks from './CreateProgramWeeks';
import CreateProgramSessions from './CreateProgramSessions';
import CreateProgramExercises from './CreateProgramExercises';
import CreateProgramReview from './CreateProgramReview';

const { width } = Dimensions.get('window');

const CreateProgramModal = ({ visible, onClose, onSuccess }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [programData, setProgramData] = useState({
    name: '',
    description: '',
    program_type: 'hypertrophy',
    duration_weeks: 4,
    is_active: true,
    is_ai_generated: false,
    training_weeks: []
  });
  const [exercises, setExercises] = useState([]);
  const [isLoadingExercises, setIsLoadingExercises] = useState(false);

  const { createProgram, isLoading } = useTrainingPrograms();

  const steps = [
    {
      title: 'Información Básica',
      component: CreateProgramBasicInfo,
      icon: 'information-circle',
    },
    {
      title: 'Configurar Semanas',
      component: CreateProgramWeeks,
      icon: 'calendar',
    },
    {
      title: 'Sesiones de Entrenamiento',
      component: CreateProgramSessions,
      icon: 'fitness',
    },
    {
      title: 'Ejercicios',
      component: CreateProgramExercises,
      icon: 'barbell',
    },
    {
      title: 'Revisar y Crear',
      component: CreateProgramReview,
      icon: 'checkmark-circle',
    },
  ];

  // Cargar ejercicios al abrir el modal
  useEffect(() => {
    if (visible) {
      loadExercises();
    }
  }, [visible]);

    const loadExercises = async () => {
    setIsLoadingExercises(true);
    try {
      const exercisesData = await exerciseService.getStandardExercises();
      setExercises(exercisesData); // Los ejercicios ya vienen con el formato correcto desde la API
    } catch (error) {
      console.error('Error loading exercises:', error);
      // Crear algunos ejercicios de ejemplo si falla la carga
      setExercises([
        { 
          id: 1, 
          standard_name: 'Press de Banca', 
          main_muscle_group: 'pectoral',
          equipment: 'barra',
          type: 'compuesto' 
        },
        { 
          id: 2, 
          standard_name: 'Sentadillas', 
          main_muscle_group: 'cuadriceps',
          equipment: 'barra',
          type: 'compuesto' 
        },
        { 
          id: 3, 
          standard_name: 'Peso Muerto', 
          main_muscle_group: 'espalda',
          equipment: 'barra',
          type: 'compuesto' 
        },
        { 
          id: 4, 
          standard_name: 'Press Militar', 
          main_muscle_group: 'hombro_frontal',
          equipment: 'barra',
          type: 'compuesto' 
        },
        { 
          id: 5, 
          standard_name: 'Remo con Barra', 
          main_muscle_group: 'espalda',
          equipment: 'barra',
          type: 'compuesto' 
        },
      ]);
    } finally {
      setIsLoadingExercises(false);
    }
  };

  // Reiniciar el formulario
  const resetForm = () => {
    setCurrentStep(0);
    setProgramData({
      name: '',
      description: '',
      program_type: 'hypertrophy',
      duration_weeks: 4,
      is_active: true,
      is_ai_generated: false,
      training_weeks: []
    });
  };

  // Función para ir al siguiente paso
  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  // Función para ir al paso anterior
  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Función para validar el paso actual
  const validateCurrentStep = () => {
    switch (currentStep) {
      case 0: // Información básica
        return programData.name.trim() !== '' && programData.description.trim() !== '';
      case 1: // Semanas
        return programData.duration_weeks > 0 && programData.training_weeks.length === programData.duration_weeks;
      case 2: // Sesiones
        return programData.training_weeks.every(week => 
          week.training_sessions && week.training_sessions.length > 0
        );
      case 3: // Ejercicios
        return programData.training_weeks.every(week =>
          week.training_sessions.every(session =>
            session.exercise_blocks && session.exercise_blocks.length > 0 &&
            session.exercise_blocks.every(block =>
              block.programmed_exercises && block.programmed_exercises.length > 0
            )
          )
        );
      case 4: // Revisar
        return true;
      default:
        return false;
    }
  };

  // Función para crear el programa
  const handleCreateProgram = async () => {
    try {
      const newProgram = await createProgram(programData);
      if (newProgram) {
        onSuccess();
        resetForm();
      }
    } catch (error) {
      Alert.alert('Error', 'No se pudo crear el programa. Intenta nuevamente.');
    }
  };

  // Función para manejar el cierre del modal
  const handleClose = () => {
    Alert.alert(
      'Cerrar',
      '¿Estás seguro? Se perderán todos los datos ingresados.',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Cerrar', onPress: () => { resetForm(); onClose(); } }
      ]
    );
  };

  // Renderizar el paso actual
  const renderCurrentStep = () => {
    const StepComponent = steps[currentStep].component;
    return (
      <StepComponent
        programData={programData}
        setProgramData={setProgramData}
        exercises={exercises}
        isLoadingExercises={isLoadingExercises}
      />
    );
  };

  // Renderizar el progreso
  const renderProgress = () => (
    <View style={styles.progressContainer}>
      <View style={styles.progressBar}>
        <View 
          style={[
            styles.progressFill,
            { width: `${((currentStep + 1) / steps.length) * 100}%` }
          ]}
        />
      </View>
      <Text style={styles.progressText}>
        Paso {currentStep + 1} de {steps.length}
      </Text>
    </View>
  );

  if (!visible) return null;

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={handleClose}
    >
      <View style={styles.container}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={handleClose}>
            <Ionicons name="close" size={24} color={COLORS.textMedium} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>
            {steps[currentStep].title}
          </Text>
          <View style={styles.headerIcon}>
            <Ionicons 
              name={steps[currentStep].icon} 
              size={24} 
              color={COLORS.primary} 
            />
          </View>
        </View>

        {/* Progress */}
        {renderProgress()}

        {/* Content */}
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {renderCurrentStep()}
        </ScrollView>

        {/* Footer */}
        <View style={styles.footer}>
          <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={prevStep}
            disabled={currentStep === 0}
          >
            <Text style={[
              styles.buttonText,
              styles.secondaryButtonText,
              currentStep === 0 && styles.disabledButtonText
            ]}>
              Anterior
            </Text>
          </TouchableOpacity>

          {currentStep < steps.length - 1 ? (
            <TouchableOpacity
              style={[styles.button, styles.primaryButton]}
              onPress={nextStep}
              disabled={!validateCurrentStep()}
            >
              <Text style={[
                styles.buttonText,
                styles.primaryButtonText,
                !validateCurrentStep() && styles.disabledButtonText
              ]}>
                Siguiente
              </Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity
              style={[styles.button, styles.primaryButton]}
              onPress={handleCreateProgram}
              disabled={isLoading || !validateCurrentStep()}
            >
              {isLoading ? (
                <LoadingIndicator size="small" />
              ) : (
                <Text style={[styles.buttonText, styles.primaryButtonText]}>
                  Crear Programa
                </Text>
              )}
            </TouchableOpacity>
          )}
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.card,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.input,
  },
  headerTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  headerIcon: {
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressContainer: {
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.card,
  },
  progressBar: {
    height: 4,
    backgroundColor: COLORS.input,
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: SPACING.sm,
  },
  progressFill: {
    height: '100%',
    backgroundColor: COLORS.primary,
    borderRadius: 2,
  },
  progressText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    textAlign: 'center',
  },
  content: {
    flex: 1,
    paddingHorizontal: SPACING.lg,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.card,
    borderTopWidth: 1,
    borderTopColor: COLORS.input,
  },
  button: {
    flex: 1,
    paddingVertical: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    justifyContent: 'center',
    marginHorizontal: SPACING.xs,
  },
  primaryButton: {
    backgroundColor: COLORS.primary,
  },
  secondaryButton: {
    backgroundColor: COLORS.input,
    borderWidth: 1,
    borderColor: COLORS.textMedium,
  },
  buttonText: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
  },
  primaryButtonText: {
    color: COLORS.background,
  },
  secondaryButtonText: {
    color: COLORS.textDark,
  },
  disabledButtonText: {
    color: COLORS.textLight,
  },
});

export default CreateProgramModal;
