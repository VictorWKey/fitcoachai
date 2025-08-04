import React, { useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';
import InputField from './InputField';

const CreateProgramBasicInfo = ({ programData, setProgramData }) => {
  const programTypes = [
    { 
      id: 'strength', 
      name: 'Fuerza', 
      description: 'Desarrollo de fuerza máxima y potencia', 
      icon: 'barbell', 
      color: '#E53E3E',
      lightColor: '#FED7D7'
    },
    { 
      id: 'hypertrophy', 
      name: 'Hipertrofia', 
      description: 'Enfoque en crecimiento muscular', 
      icon: 'fitness', 
      color: '#38B2AC',
      lightColor: '#B2F5EA'
    },
    { 
      id: 'peaking', 
      name: 'Peaking', 
      description: 'Preparación para competición', 
      icon: 'trophy', 
      color: '#D69E2E',
      lightColor: '#FAF089'
    },
  ];  

  // Establecer valor por defecto para la duración si no existe
  useEffect(() => {
    if (!programData.duration_weeks) {
      handleInputChange('duration_weeks', 4);
    }
  }, []);

  const handleInputChange = (field, value) => {
    setProgramData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleTypeSelect = (typeId) => {
    handleInputChange('program_type', typeId);
  };

  const handleDurationChange = (weeks) => {
    const parsedWeeks = parseInt(weeks, 10);
    if (!isNaN(parsedWeeks) && parsedWeeks > 0) {
      handleInputChange('duration_weeks', parsedWeeks);
      setProgramData(prev => ({
        ...prev,
        duration_weeks: parsedWeeks,
        training_weeks: []
      }));
    }
  };

  const incrementDuration = () => {
    const currentWeeks = programData.duration_weeks || 4;
    handleInputChange('duration_weeks', currentWeeks + 1);
  };

  const decrementDuration = () => {
    const currentWeeks = programData.duration_weeks || 4;
    if (currentWeeks > 1) {
      handleInputChange('duration_weeks', currentWeeks - 1);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Información del Programa</Text>
      
      {/* Nombre del programa */}
      <View style={styles.inputContainer}>
        <Text style={styles.label}>Nombre del Programa *</Text>
        <InputField
          placeholder="Ej: Programa de Fuerza 12 semanas"
          value={programData.name}
          onChangeText={(value) => handleInputChange('name', value)}
          multiline={false}
        />
      </View>

      {/* Descripción */}
      <View style={styles.inputContainer}>
        <Text style={styles.label}>Descripción *</Text>
        <InputField
          placeholder="Describe los objetivos y características del programa..."
          value={programData.description}
          onChangeText={(value) => handleInputChange('description', value)}
          multiline={true}
          numberOfLines={3}
          style={styles.textArea}
        />
      </View>

      {/* Tipo de programa */}
      <View style={styles.inputContainer}>
        <Text style={styles.label}>Tipo de Programa *</Text>
        <View style={styles.optionsGrid}>
          {programTypes.map((type) => (
            <TouchableOpacity
              key={type.id}
              style={[
                styles.optionCard,
                programData.program_type === type.id && styles.selectedOption
              ]}
              onPress={() => handleTypeSelect(type.id)}
              activeOpacity={0.8}
            >
              <View style={[
                styles.optionIconContainer, 
                { backgroundColor: type.color },
                programData.program_type === type.id && styles.selectedIconContainer
              ]}>
                <Ionicons name={type.icon} size={28} color="#FFFFFF" />
              </View>
              <View style={styles.optionContent}>
                <Text style={[
                  styles.optionTitle,
                  programData.program_type === type.id && styles.selectedOptionTitle
                ]}>
                  {type.name}
                </Text>
                <Text style={[
                  styles.optionDescription,
                  programData.program_type === type.id && styles.selectedOptionDescription
                ]}>
                  {type.description}
                </Text>
              </View>
              {programData.program_type === type.id && (
                <View style={styles.selectedIndicator}>
                  <Ionicons name="checkmark-circle" size={20} color={type.color} />
                </View>
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Duración */}
      <View style={styles.inputContainer}>
        <Text style={styles.label}>Duración del Programa (en semanas) *</Text>
        <View style={styles.durationWrapper}>
          <TouchableOpacity 
            style={styles.durationButton} 
            onPress={decrementDuration}
            activeOpacity={0.7}
          >
            <Ionicons name="remove" size={20} color={COLORS.background} />
          </TouchableOpacity>
          
          <View style={styles.durationDisplayWrapper}>
            <Text style={styles.durationText}>
              {programData.duration_weeks || 4}
            </Text>
          </View>
          
          <TouchableOpacity 
            style={styles.durationButton} 
            onPress={incrementDuration}
            activeOpacity={0.7}
          >
            <Ionicons name="add" size={20} color={COLORS.background} />
          </TouchableOpacity>
        </View>
      </View>

      {/* Configuración adicional */}
      <View style={styles.inputContainer}>
        <Text style={styles.label}>Configuración</Text>
        <TouchableOpacity
          style={[
            styles.checkboxContainer,
            programData.is_active && styles.checkboxChecked
          ]}
          onPress={() => handleInputChange('is_active', !programData.is_active)}
        >
          <View style={styles.checkbox}>
            {programData.is_active && (
              <Ionicons name="checkmark" size={16} color={COLORS.background} />
            )}
          </View>
          <Text style={styles.checkboxLabel}>Activar programa al crearlo</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: SPACING.lg,
  },
  sectionTitle: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.lg,
    textAlign: 'center',
  },
  inputContainer: {
    marginBottom: SPACING.lg,
  },
  label: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.sm,
  },
  textArea: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
  optionsGrid: {
    gap: SPACING.md,
  },
  optionCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.lg,
    borderWidth: 2,
    borderColor: 'transparent',
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.sm,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.08,
    shadowRadius: 8,
    transition: 'all 0.2s ease-in-out',
  },
  selectedOption: {
    borderColor: COLORS.primary,
    backgroundColor: COLORS.input,
    elevation: 4,
    shadowOpacity: 0.15,
    shadowRadius: 12,
  },
  optionIconContainer: {
    width: 60,
    height: 60,
    borderRadius: BORDER_RADIUS.lg,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.lg,
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.2,
    shadowRadius: 6,
  },
  selectedIconContainer: {
    elevation: 5,
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  optionContent: {
    flex: 1,
    marginRight: SPACING.sm,
  },
  optionTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '700',
    color: COLORS.textDark,
    marginBottom: 2,
    letterSpacing: 0.3,
  },
  selectedOptionTitle: {
    color: COLORS.primary,
  },
  optionDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    lineHeight: 18,
    fontWeight: '400',
  },
  selectedOptionDescription: {
    color: COLORS.textLight,
  },
  selectedIndicator: {
    position: 'absolute',
    top: 16,
    right: 16,
    backgroundColor: COLORS.background,
    borderRadius: 12,
    padding: 2,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: COLORS.textMedium,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.sm,
  },
  checkboxChecked: {
    borderColor: COLORS.primary,
  },
  checkboxLabel: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textDark,
  },
  durationButton: {
    width: 40,
    height: 40,
    backgroundColor: COLORS.primary,
    borderRadius: BORDER_RADIUS.md,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.2,
    shadowRadius: 1.5,
  },
  durationWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: SPACING.sm,
    gap: SPACING.md,
  },
  durationDisplayWrapper: {
    minWidth: 100,
    height: 50,
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: COLORS.primary,
    paddingHorizontal: SPACING.md,
  },
  durationText: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.primary,
    textAlign: 'center',
  },
  durationLabel: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    textAlign: 'center',
    marginTop: 2,
  },
});

export default CreateProgramBasicInfo;
