import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';
import InputField from './InputField';
import StandardExerciseSelector from './StandardExerciseSelector';

const CreateProgramExercises = ({ programData, setProgramData, exercises, isLoadingExercises }) => {
  const [expandedWeek, setExpandedWeek] = useState(0);
  const [expandedSession, setExpandedSession] = useState(null);
  const [showExerciseModal, setShowExerciseModal] = useState(false);
  const [selectedBlock, setSelectedBlock] = useState(null);

  const loadTypes = [
    { id: 'percentage', name: 'Porcentaje 1RM', example: '80%' },
    { id: 'weight', name: 'Peso Fijo', example: '80kg' },
    { id: 'rpe', name: 'RPE', example: 'RPE 8' },
  ];

  const setTypes = [
    { id: 'strength', name: 'Fuerza', description: 'Series de fuerza' },
    { id: 'hypertrophy', name: 'Hipertrofia', description: 'Series de hipertrofia' },
    { id: 'technique', name: 'Técnica', description: 'Series de técnica' },
  ];

  const blockTypes = [
    { id: 'main', name: 'Principal', description: 'Ejercicios principales' },
    { id: 'accessory', name: 'Accesorio', description: 'Ejercicios accesorios' },
  ];

  const addExerciseBlock = (weekIndex, sessionIndex) => {
    const newBlock = {
      name: `Bloque ${programData.training_weeks[weekIndex].training_sessions[sessionIndex].exercise_blocks.length + 1}`,
      block_type: 'main',
      order: programData.training_weeks[weekIndex].training_sessions[sessionIndex].exercise_blocks.length + 1,
      description: '',
      programmed_exercises: []
    };

    setProgramData(prev => ({
      ...prev,
      training_weeks: prev.training_weeks.map((week, wIndex) =>
        wIndex === weekIndex
          ? {
              ...week,
              training_sessions: week.training_sessions.map((session, sIndex) =>
                sIndex === sessionIndex
                  ? { ...session, exercise_blocks: [...session.exercise_blocks, newBlock] }
                  : session
              )
            }
          : week
      )
    }));
  };

  const removeExerciseBlock = (weekIndex, sessionIndex, blockIndex) => {
    Alert.alert(
      'Eliminar Bloque',
      '¿Estás seguro de que deseas eliminar este bloque de ejercicios?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: () => {
            setProgramData(prev => ({
              ...prev,
              training_weeks: prev.training_weeks.map((week, wIndex) =>
                wIndex === weekIndex
                  ? {
                      ...week,
                      training_sessions: week.training_sessions.map((session, sIndex) =>
                        sIndex === sessionIndex
                          ? { ...session, exercise_blocks: session.exercise_blocks.filter((_, idx) => idx !== blockIndex) }
                          : session
                      )
                    }
                  : week
              )
            }));
          }
        }
      ]
    );
  };

  const updateExerciseBlock = (weekIndex, sessionIndex, blockIndex, field, value) => {
    setProgramData(prev => ({
      ...prev,
      training_weeks: prev.training_weeks.map((week, wIndex) =>
        wIndex === weekIndex
          ? {
              ...week,
              training_sessions: week.training_sessions.map((session, sIndex) =>
                sIndex === sessionIndex
                  ? {
                      ...session,
                      exercise_blocks: session.exercise_blocks.map((block, bIndex) =>
                        bIndex === blockIndex ? { ...block, [field]: value } : block
                      )
                    }
                  : session
              )
            }
          : week
      )
    }));
  };

  const addExercise = (weekIndex, sessionIndex, blockIndex, exercise) => {
    const newExercise = {
      standard_exercise_id: exercise.id,
      exercise_name: exercise.standard_name || exercise.name,
      tempo: "3-1-1-0",
      sets: 3,
      reps: 10,
      load_type: "rpe",
      rpe_target: 8.0,
      percentage_1rm: null,
      weight_range: "",
      rest_seconds: 90,
      sets_type: "strength"
    };

    setProgramData(prev => ({
      ...prev,
      training_weeks: prev.training_weeks.map((week, wIndex) =>
        wIndex === weekIndex
          ? {
              ...week,
              training_sessions: week.training_sessions.map((session, sIndex) =>
                sIndex === sessionIndex
                  ? {
                      ...session,
                      exercise_blocks: session.exercise_blocks.map((block, bIndex) =>
                        bIndex === blockIndex
                          ? { ...block, programmed_exercises: [...block.programmed_exercises, newExercise] }
                          : block
                      )
                    }
                  : session
              )
            }
          : week
      )
    }));
  };

  const removeExercise = (weekIndex, sessionIndex, blockIndex, exerciseIndex) => {
    setProgramData(prev => ({
      ...prev,
      training_weeks: prev.training_weeks.map((week, wIndex) =>
        wIndex === weekIndex
          ? {
              ...week,
              training_sessions: week.training_sessions.map((session, sIndex) =>
                sIndex === sessionIndex
                  ? {
                      ...session,
                      exercise_blocks: session.exercise_blocks.map((block, bIndex) =>
                        bIndex === blockIndex
                          ? { ...block, programmed_exercises: block.programmed_exercises.filter((_, idx) => idx !== exerciseIndex) }
                          : block
                      )
                    }
                  : session
              )
            }
          : week
      )
    }));
  };

  const updateExercise = (weekIndex, sessionIndex, blockIndex, exerciseIndex, field, value) => {
    setProgramData(prev => ({
      ...prev,
      training_weeks: prev.training_weeks.map((week, wIndex) =>
        wIndex === weekIndex
          ? {
              ...week,
              training_sessions: week.training_sessions.map((session, sIndex) =>
                sIndex === sessionIndex
                  ? {
                      ...session,
                      exercise_blocks: session.exercise_blocks.map((block, bIndex) =>
                        bIndex === blockIndex
                          ? {
                              ...block,
                              programmed_exercises: block.programmed_exercises.map((exercise, eIndex) =>
                                eIndex === exerciseIndex ? { ...exercise, [field]: value } : exercise
                              )
                            }
                          : block
                      )
                    }
                  : session
              )
            }
          : week
      )
    }));
  };

  const openExerciseModal = (weekIndex, sessionIndex, blockIndex) => {
    setSelectedBlock({ weekIndex, sessionIndex, blockIndex });
    setShowExerciseModal(true);
  };

  const renderExerciseModal = () => (
    <StandardExerciseSelector
      visible={showExerciseModal}
      onClose={() => setShowExerciseModal(false)}
      onSelect={(exercise) => {
        if (selectedBlock) {
          addExercise(
            selectedBlock.weekIndex,
            selectedBlock.sessionIndex,
            selectedBlock.blockIndex,
            exercise
          );
        }
        setSelectedBlock(null);
      }}
      title="Seleccionar Ejercicio"
      exercises={exercises}
      isLoadingExercises={isLoadingExercises}
    />
  );

  const renderExercise = (exercise, weekIndex, sessionIndex, blockIndex, exerciseIndex) => (
    <View key={exerciseIndex} style={styles.exerciseCard}>
      <View style={styles.exerciseHeader}>
        <Text style={styles.exerciseName} numberOfLines={1}>
          {exercise.exercise_name || `Ejercicio ${exerciseIndex + 1}`}
        </Text>
        <TouchableOpacity
          style={styles.deleteButton}
          onPress={() => removeExercise(weekIndex, sessionIndex, blockIndex, exerciseIndex)}
        >
          <Ionicons name="trash-outline" size={16} color={COLORS.error} />
        </TouchableOpacity>
      </View>
      
      <View style={styles.exerciseParams}>
        <View style={styles.paramRow}>
          <View style={styles.paramGroup}>
            <Text style={styles.paramLabel}>Series</Text>
            <InputField
              value={exercise.sets.toString()}
              onChangeText={(value) => updateExercise(weekIndex, sessionIndex, blockIndex, exerciseIndex, 'sets', parseInt(value) || 0)}
              placeholder="3"
              keyboardType="numeric"
              style={styles.paramInput}
            />
          </View>
          <View style={styles.paramGroup}>
            <Text style={styles.paramLabel}>Repeticiones</Text>
            <InputField
              value={exercise.reps.toString()}
              onChangeText={(value) => updateExercise(weekIndex, sessionIndex, blockIndex, exerciseIndex, 'reps', parseInt(value) || 0)}
              placeholder="10"
              keyboardType="numeric"
              style={styles.paramInput}
            />
          </View>
          <View style={styles.paramGroup}>
            <Text style={styles.paramLabel}>Descanso (s)</Text>
            <InputField
              value={exercise.rest_seconds.toString()}
              onChangeText={(value) => updateExercise(weekIndex, sessionIndex, blockIndex, exerciseIndex, 'rest_seconds', parseInt(value) || 0)}
              placeholder="60"
              keyboardType="numeric"
              style={styles.paramInput}
            />
          </View>
        </View>
      </View>
    </View>
  );

  const renderExerciseBlock = (block, weekIndex, sessionIndex, blockIndex) => (
    <View key={blockIndex} style={styles.blockCard}>
      <View style={styles.blockHeader}>
        <Text style={styles.blockTitle}>Bloque {blockIndex + 1}</Text>
        <TouchableOpacity
          style={styles.deleteButton}
          onPress={() => removeExerciseBlock(weekIndex, sessionIndex, blockIndex)}
        >
          <Ionicons name="trash-outline" size={20} color={COLORS.error} />
        </TouchableOpacity>
      </View>

      <View style={styles.blockContent}>
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Nombre del bloque</Text>
          <InputField
            placeholder="Ej: Calentamiento, Fuerza, Accesorios"
            value={block.name}
            onChangeText={(value) => updateExerciseBlock(weekIndex, sessionIndex, blockIndex, 'name', value)}
          />
        </View>

        <View style={styles.exercisesContainer}>
          <Text style={styles.label}>Ejercicios ({block.programmed_exercises.length})</Text>
          
          {block.programmed_exercises.map((exercise, exerciseIndex) =>
            renderExercise(exercise, weekIndex, sessionIndex, blockIndex, exerciseIndex)
          )}
          
          <TouchableOpacity
            style={styles.addExerciseButton}
            onPress={() => openExerciseModal(weekIndex, sessionIndex, blockIndex)}
          >
            <Ionicons name="add" size={20} color={COLORS.primary} />
            <Text style={styles.addExerciseText}>Agregar Ejercicio</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );

  const renderSession = (session, weekIndex, sessionIndex) => {
    const isExpanded = expandedSession === `${weekIndex}-${sessionIndex}`;
    
    return (
      <View key={sessionIndex} style={styles.sessionContainer}>
        <TouchableOpacity
          style={styles.sessionHeader}
          onPress={() => setExpandedSession(isExpanded ? null : `${weekIndex}-${sessionIndex}`)}
        >
          <Text style={styles.sessionTitle}>{session.name}</Text>
          <View style={styles.sessionInfo}>
            <Text style={styles.sessionCount}>
              {session.exercise_blocks.length} bloques
            </Text>
            <Ionicons
              name={isExpanded ? "chevron-up" : "chevron-down"}
              size={20}
              color={COLORS.textMedium}
            />
          </View>
        </TouchableOpacity>

        {isExpanded && (
          <View style={styles.sessionContent}>
            {session.exercise_blocks.map((block, blockIndex) =>
              renderExerciseBlock(block, weekIndex, sessionIndex, blockIndex)
            )}
            
            <TouchableOpacity
              style={styles.addBlockButton}
              onPress={() => addExerciseBlock(weekIndex, sessionIndex)}
            >
              <Ionicons name="add" size={20} color={COLORS.primary} />
              <Text style={styles.addBlockText}>Agregar Bloque</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    );
  };

  const renderWeek = (week, weekIndex) => (
    <View key={weekIndex} style={styles.weekContainer}>
      <TouchableOpacity
        style={styles.weekHeader}
        onPress={() => setExpandedWeek(expandedWeek === weekIndex ? -1 : weekIndex)}
      >
        <View style={styles.weekTitleContainer}>
          <View style={styles.weekNumber}>
            <Text style={styles.weekNumberText}>{week.week_number}</Text>
          </View>
          <Text style={styles.weekTitle}>{week.description}</Text>
        </View>
        <Ionicons
          name={expandedWeek === weekIndex ? "chevron-up" : "chevron-down"}
          size={20}
          color={COLORS.textMedium}
        />
      </TouchableOpacity>

      {expandedWeek === weekIndex && (
        <View style={styles.weekContent}>
          {week.training_sessions.map((session, sessionIndex) =>
            renderSession(session, weekIndex, sessionIndex)
          )}
        </View>
      )}
    </View>
  );

  if (isLoadingExercises) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Cargando ejercicios...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.sectionTitle}>Ejercicios del Programa</Text>
      <Text style={styles.sectionDescription}>
        Configura los ejercicios para cada sesión de entrenamiento
      </Text>

      <View style={styles.weeksContainer}>
        {programData.training_weeks.map((week, weekIndex) => renderWeek(week, weekIndex))}
      </View>

      {renderExerciseModal()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingVertical: SPACING.lg,
  },
  sectionTitle: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.sm,
    textAlign: 'center',
  },
  sectionDescription: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    textAlign: 'center',
    marginBottom: SPACING.xl,
    lineHeight: 20,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
  },
  weeksContainer: {
    gap: SPACING.md,
  },
  weekContainer: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    overflow: 'hidden',
  },
  weekHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: COLORS.input,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
  },
  weekTitleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  weekNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.sm,
  },
  weekNumberText: {
    fontSize: FONT_SIZE.md,
    fontWeight: 'bold',
    color: COLORS.background,
  },
  weekTitle: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textDark,
    flex: 1,
  },
  weekContent: {
    padding: SPACING.md,
    gap: SPACING.md,
  },
  sessionContainer: {
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.md,
    overflow: 'hidden',
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: COLORS.input,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
  },
  sessionTitle: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  sessionInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  sessionCount: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  sessionContent: {
    padding: SPACING.md,
    gap: SPACING.md,
  },
  blockCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    borderWidth: 1,
    borderColor: COLORS.input,
  },
  blockHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: COLORS.input,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
  },
  blockTitle: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  blockContent: {
    padding: SPACING.md,
    gap: SPACING.md,
  },
  inputGroup: {
    gap: SPACING.sm,
  },
  label: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  exercisesContainer: {
    gap: SPACING.md,
  },
  exerciseCard: {
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.sm,
    padding: SPACING.sm,
    borderWidth: 1,
    borderColor: COLORS.input,
  },
  exerciseHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  exerciseName: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.textDark,
    flex: 1,
  },
  exerciseParams: {
    gap: SPACING.sm,
  },
  paramRow: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  paramGroup: {
    flex: 1,
    gap: SPACING.xs,
  },
  paramLabel: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
  },
  paramInput: {
    minHeight: 40,
    fontSize: FONT_SIZE.sm,
  },
  deleteButton: {
    padding: SPACING.xs,
  },
  addExerciseButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.sm,
    paddingVertical: SPACING.md,
    borderWidth: 2,
    borderColor: COLORS.primary,
    borderStyle: 'dashed',
    gap: SPACING.sm,
  },
  addExerciseText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.primary,
    fontWeight: '600',
  },
  addBlockButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.md,
    paddingVertical: SPACING.md,
    borderWidth: 2,
    borderColor: COLORS.primary,
    borderStyle: 'dashed',
    gap: SPACING.sm,
  },
  addBlockText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.primary,
    fontWeight: '600',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.card,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.input,
  },
  modalTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  exerciseItem: {
    paddingHorizontal: SPACING.lg,
    paddingVertical: SPACING.md,
  },
  exerciseCategory: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    marginTop: SPACING.xs,
  },
  separator: {
    height: 1,
    backgroundColor: COLORS.input,
    marginHorizontal: SPACING.lg,
  },
});

export default CreateProgramExercises;
