import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';
import InputField from './InputField';
import ValidationHelper from './ValidationHelper';
import { validateProgrammedExercise, validateTempo, validateRPE } from '../utils/validationUtils';

const ExerciseConfiguration = ({ exercise, onUpdate, onDelete }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [errors, setErrors] = useState({});

  const handleUpdate = (field, value) => {
    const updatedExercise = { ...exercise, [field]: value };
    
    // Validar el ejercicio completo
    const validation = validateProgrammedExercise(updatedExercise);
    setErrors(validation.errors);
    
    onUpdate(updatedExercise);
  };

  const handleLoadTypeChange = (loadType) => {
    const updatedExercise = { 
      ...exercise, 
      load_type: loadType,
      rpe_target: loadType === 'rpe' ? exercise.rpe_target : null,
      percentage_1rm: loadType === 'percentage' ? exercise.percentage_1rm : null,
      weight_range: loadType === 'weight' ? exercise.weight_range : '',
    };
    
    const validation = validateProgrammedExercise(updatedExercise);
    setErrors(validation.errors);
    
    onUpdate(updatedExercise);
  };

  const renderBasicInfo = () => (
    <View style={styles.basicInfo}>
      <Text style={styles.exerciseName} numberOfLines={2}>
        {exercise.exercise_name || 'Ejercicio sin nombre'}
      </Text>
      
      <View style={styles.quickInfo}>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>Series</Text>
          <Text style={styles.infoValue}>{exercise.sets || 0}</Text>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>Reps</Text>
          <Text style={styles.infoValue}>{exercise.reps || 0}</Text>
        </View>
        <View style={styles.infoItem}>
          <Text style={styles.infoLabel}>Carga</Text>
          <Text style={styles.infoValue}>
            {exercise.load_type === 'rpe' && exercise.rpe_target ? `RPE ${exercise.rpe_target}` :
             exercise.load_type === 'percentage' && exercise.percentage_1rm ? `${exercise.percentage_1rm}%` :
             exercise.load_type === 'weight' && exercise.weight_range ? exercise.weight_range :
             'Sin definir'}
          </Text>
        </View>
      </View>
    </View>
  );

  const renderExpandedForm = () => (
    <View style={styles.expandedForm}>
      {/* Series y Repeticiones */}
      <View style={styles.formRow}>
        <View style={[styles.formGroup, { flex: 1 }]}>
          <Text style={styles.label}>Series</Text>
          <InputField
            value={exercise.sets?.toString() || ''}
            onChangeText={(value) => handleUpdate('sets', parseInt(value) || 0)}
            placeholder="3"
            keyboardType="numeric"
            style={[styles.input, errors.sets && styles.inputError]}
          />
          {errors.sets && <Text style={styles.errorText}>{errors.sets}</Text>}
        </View>
        
        <View style={[styles.formGroup, { flex: 1 }]}>
          <Text style={styles.label}>Repeticiones</Text>
          <InputField
            value={exercise.reps?.toString() || ''}
            onChangeText={(value) => handleUpdate('reps', parseInt(value) || 0)}
            placeholder="10"
            keyboardType="numeric"
            style={[styles.input, errors.reps && styles.inputError]}
          />
          {errors.reps && <Text style={styles.errorText}>{errors.reps}</Text>}
        </View>
      </View>

      {/* Tipo de Carga */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Tipo de Carga</Text>
        <View style={styles.loadTypeContainer}>
          {[
            { id: 'rpe', name: 'RPE', description: 'Esfuerzo percibido' },
            { id: 'percentage', name: 'Porcentaje', description: '% de 1RM' },
            { id: 'weight', name: 'Peso', description: 'Peso absoluto' }
          ].map((type) => (
            <TouchableOpacity
              key={type.id}
              style={[
                styles.loadTypeButton,
                exercise.load_type === type.id && styles.loadTypeButtonActive
              ]}
              onPress={() => handleLoadTypeChange(type.id)}
            >
              <Text style={[
                styles.loadTypeText,
                exercise.load_type === type.id && styles.loadTypeTextActive
              ]}>
                {type.name}
              </Text>
              <Text style={[
                styles.loadTypeDescription,
                exercise.load_type === type.id && styles.loadTypeDescriptionActive
              ]}>
                {type.description}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Configuración de Carga */}
      {exercise.load_type === 'rpe' && (
        <View style={styles.formGroup}>
          <View style={styles.labelRow}>
            <Text style={styles.label}>RPE Objetivo</Text>
            <ValidationHelper type="rpe" value={exercise.rpe_target} />
          </View>
          <InputField
            value={exercise.rpe_target?.toString() || ''}
            onChangeText={(value) => handleUpdate('rpe_target', parseFloat(value) || 0)}
            placeholder="8.0"
            keyboardType="decimal-pad"
            style={[styles.input, errors.rpe_target && styles.inputError]}
          />
          {errors.rpe_target && <Text style={styles.errorText}>{errors.rpe_target}</Text>}
        </View>
      )}

      {exercise.load_type === 'percentage' && (
        <View style={styles.formGroup}>
          <Text style={styles.label}>Porcentaje 1RM</Text>
          <InputField
            value={exercise.percentage_1rm?.toString() || ''}
            onChangeText={(value) => handleUpdate('percentage_1rm', parseFloat(value) || 0)}
            placeholder="80"
            keyboardType="decimal-pad"
            style={[styles.input, errors.percentage_1rm && styles.inputError]}
          />
          {errors.percentage_1rm && <Text style={styles.errorText}>{errors.percentage_1rm}</Text>}
        </View>
      )}

      {exercise.load_type === 'weight' && (
        <View style={styles.formGroup}>
          <Text style={styles.label}>Rango de Peso</Text>
          <InputField
            value={exercise.weight_range || ''}
            onChangeText={(value) => handleUpdate('weight_range', value)}
            placeholder="80-90kg"
            style={[styles.input, errors.weight_range && styles.inputError]}
          />
          {errors.weight_range && <Text style={styles.errorText}>{errors.weight_range}</Text>}
        </View>
      )}

      {/* Tempo */}
      <View style={styles.formGroup}>
        <View style={styles.labelRow}>
          <Text style={styles.label}>Tempo</Text>
          <ValidationHelper type="tempo" value={exercise.tempo} />
        </View>
        <InputField
          value={exercise.tempo || ''}
          onChangeText={(value) => handleUpdate('tempo', value)}
          placeholder="3-1-1-0"
          style={[styles.input, errors.tempo && styles.inputError]}
        />
        {errors.tempo && <Text style={styles.errorText}>{errors.tempo}</Text>}
      </View>

      {/* Descanso */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Descanso (segundos)</Text>
        <InputField
          value={exercise.rest_seconds?.toString() || ''}
          onChangeText={(value) => handleUpdate('rest_seconds', parseInt(value) || 0)}
          placeholder="90"
          keyboardType="numeric"
          style={[styles.input, errors.rest_seconds && styles.inputError]}
        />
        {errors.rest_seconds && <Text style={styles.errorText}>{errors.rest_seconds}</Text>}
      </View>

      {/* Tipo de Serie */}
      <View style={styles.formGroup}>
        <Text style={styles.label}>Tipo de Serie</Text>
        <View style={styles.setTypeContainer}>
          {[
            { id: 'strength', name: 'Fuerza' },
            { id: 'hypertrophy', name: 'Hipertrofia' },
            { id: 'technique', name: 'Técnica' }
          ].map((type) => (
            <TouchableOpacity
              key={type.id}
              style={[
                styles.setTypeButton,
                exercise.sets_type === type.id && styles.setTypeButtonActive
              ]}
              onPress={() => handleUpdate('sets_type', type.id)}
            >
              <Text style={[
                styles.setTypeText,
                exercise.sets_type === type.id && styles.setTypeTextActive
              ]}>
                {type.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        {renderBasicInfo()}
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.expandButton}
            onPress={() => setIsExpanded(!isExpanded)}
          >
            <Ionicons 
              name={isExpanded ? 'chevron-up' : 'chevron-down'} 
              size={20} 
              color={COLORS.textMedium} 
            />
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.deleteButton}
            onPress={onDelete}
          >
            <Ionicons name="trash-outline" size={16} color={COLORS.error} />
          </TouchableOpacity>
        </View>
      </View>

      {isExpanded && renderExpandedForm()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.md,
    borderWidth: 1,
    borderColor: COLORS.border,
    marginBottom: SPACING.sm,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: SPACING.md,
  },
  basicInfo: {
    flex: 1,
  },
  exerciseName: {
    fontSize: FONT_SIZE.md,
    fontWeight: '500',
    color: COLORS.textPrimary,
    marginBottom: SPACING.xs,
  },
  quickInfo: {
    flexDirection: 'row',
    gap: SPACING.md,
  },
  infoItem: {
    alignItems: 'center',
  },
  infoLabel: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
    marginBottom: SPACING.xs,
  },
  infoValue: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '500',
    color: COLORS.textPrimary,
  },
  headerActions: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  expandButton: {
    padding: SPACING.xs,
  },
  deleteButton: {
    padding: SPACING.xs,
  },
  expandedForm: {
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    padding: SPACING.md,
  },
  formRow: {
    flexDirection: 'row',
    gap: SPACING.md,
  },
  formGroup: {
    marginBottom: SPACING.md,
  },
  label: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '500',
    color: COLORS.textPrimary,
    marginBottom: SPACING.xs,
  },
  labelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.xs,
  },
  input: {
    backgroundColor: COLORS.backgroundSecondary,
    borderRadius: BORDER_RADIUS.md,
  },
  inputError: {
    borderColor: COLORS.error,
    borderWidth: 1,
  },
  errorText: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.error,
    marginTop: SPACING.xs,
  },
  loadTypeContainer: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  loadTypeButton: {
    flex: 1,
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  loadTypeButtonActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  loadTypeText: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '500',
    color: COLORS.textPrimary,
  },
  loadTypeTextActive: {
    color: COLORS.white,
  },
  loadTypeDescription: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
    marginTop: SPACING.xs,
  },
  loadTypeDescriptionActive: {
    color: COLORS.white,
  },
  setTypeContainer: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  setTypeButton: {
    flex: 1,
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.sm,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  setTypeButtonActive: {
    backgroundColor: COLORS.primary,
    borderColor: COLORS.primary,
  },
  setTypeText: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '500',
    color: COLORS.textPrimary,
  },
  setTypeTextActive: {
    color: COLORS.white,
  },
});

export default ExerciseConfiguration;
