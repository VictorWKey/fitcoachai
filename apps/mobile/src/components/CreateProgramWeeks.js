import React, { useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';
import InputField from './InputField';

const CreateProgramWeeks = ({ programData, setProgramData }) => {
  // Inicializar las semanas si no existen
  useEffect(() => {
    if (programData.training_weeks.length !== programData.duration_weeks) {
      const weeks = Array.from({ length: programData.duration_weeks }, (_, index) => ({
        week_number: index + 1,
        description: `Semana ${index + 1}`,
        training_sessions: []
      }));
      
      setProgramData(prev => ({
        ...prev,
        training_weeks: weeks
      }));
    }
  }, [programData.duration_weeks]);

  const handleWeekDescriptionChange = (weekIndex, description) => {
    setProgramData(prev => ({
      ...prev,
      training_weeks: prev.training_weeks.map((week, index) => 
        index === weekIndex ? { ...week, description } : week
      )
    }));
  };

  const renderWeekCard = (week, index) => (
    <View key={index} style={styles.weekCard}>
      <View style={styles.weekHeader}>
        <View style={styles.weekNumber}>
          <Text style={styles.weekNumberText}>{week.week_number}</Text>
        </View>
        <Text style={styles.weekTitle}>Semana {week.week_number}</Text>
      </View>
      
      <View style={styles.weekContent}>
        <Text style={styles.label}>Descripción de la semana</Text>
        <InputField
          placeholder={`Describe los objetivos de la semana ${week.week_number}...`}
          value={week.description}
          onChangeText={(value) => handleWeekDescriptionChange(index, value)}
          multiline={true}
          numberOfLines={2}
          style={styles.descriptionInput}
        />
        
        <View style={styles.weekInfo}>
          <View style={styles.infoItem}>
            <Ionicons name="calendar-outline" size={16} color={COLORS.textMedium} />
            <Text style={styles.infoText}>
              Semana {week.week_number} de {programData.duration_weeks}
            </Text>
          </View>
          <View style={styles.infoItem}>
            <Ionicons name="fitness-outline" size={16} color={COLORS.textMedium} />
            <Text style={styles.infoText}>
              {week.training_sessions.length} sesiones configuradas
            </Text>
          </View>
        </View>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.sectionTitle}>Configurar Semanas</Text>
      <Text style={styles.sectionDescription}>
        Define la descripción y objetivos para cada semana del programa
      </Text>
      
      <View style={styles.weeksContainer}>
        {programData.training_weeks.map((week, index) => renderWeekCard(week, index))}
      </View>
      
      <View style={styles.summary}>
        <Text style={styles.summaryTitle}>Resumen del Programa</Text>
        <View style={styles.summaryItems}>
          <View style={styles.summaryItem}>
            <Ionicons name="calendar" size={20} color={COLORS.primary} />
            <Text style={styles.summaryText}>
              {programData.duration_weeks} semanas de entrenamiento
            </Text>
          </View>
          <View style={styles.summaryItem}>
            <Ionicons name="barbell" size={20} color={COLORS.primary} />
            <Text style={styles.summaryText}>
              Programa de {programData.program_type}
            </Text>
          </View>
        </View>
      </View>
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
  weeksContainer: {
    gap: SPACING.md,
    marginBottom: SPACING.xl,
  },
  weekCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    overflow: 'hidden',
  },
  weekHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.input,
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
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
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  weekContent: {
    padding: SPACING.md,
  },
  label: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.sm,
  },
  descriptionInput: {
    minHeight: 60,
    textAlignVertical: 'top',
    marginBottom: SPACING.md,
  },
  weekInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  infoText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  summary: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    marginBottom: SPACING.lg,
  },
  summaryTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.md,
    textAlign: 'center',
  },
  summaryItems: {
    gap: SPACING.md,
  },
  summaryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  summaryText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
  },
});

export default CreateProgramWeeks;
