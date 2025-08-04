import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';
import InputField from './InputField';

const CreateProgramSessions = ({ programData, setProgramData }) => {
  const [expandedWeek, setExpandedWeek] = useState(0);

  const daysOfWeek = [
    { value: 1, label: 'Lunes', short: 'L' },
    { value: 2, label: 'Martes', short: 'M' },
    { value: 3, label: 'Miércoles', short: 'X' },
    { value: 4, label: 'Jueves', short: 'J' },
    { value: 5, label: 'Viernes', short: 'V' },
    { value: 6, label: 'Sábado', short: 'S' },
    { value: 7, label: 'Domingo', short: 'D' },
  ];

  const addSession = (weekIndex) => {
    const newSession = {
      name: `Sesión ${programData.training_weeks[weekIndex].training_sessions.length + 1}`,
      day_of_week: 1,
      description: '',
      exercise_blocks: []
    };

    setProgramData(prev => ({
      ...prev,
      training_weeks: prev.training_weeks.map((week, index) =>
        index === weekIndex
          ? { ...week, training_sessions: [...week.training_sessions, newSession] }
          : week
      )
    }));
  };

  const removeSession = (weekIndex, sessionIndex) => {
    Alert.alert(
      'Eliminar Sesión',
      '¿Estás seguro de que deseas eliminar esta sesión?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Eliminar',
          style: 'destructive',
          onPress: () => {
            setProgramData(prev => ({
              ...prev,
              training_weeks: prev.training_weeks.map((week, index) =>
                index === weekIndex
                  ? { ...week, training_sessions: week.training_sessions.filter((_, idx) => idx !== sessionIndex) }
                  : week
              )
            }));
          }
        }
      ]
    );
  };

  const updateSession = (weekIndex, sessionIndex, field, value) => {
    setProgramData(prev => ({
      ...prev,
      training_weeks: prev.training_weeks.map((week, wIndex) =>
        wIndex === weekIndex
          ? {
              ...week,
              training_sessions: week.training_sessions.map((session, sIndex) =>
                sIndex === sessionIndex ? { ...session, [field]: value } : session
              )
            }
          : week
      )
    }));
  };

  const renderDaySelector = (weekIndex, sessionIndex, selectedDay) => (
    <View style={styles.daySelector}>
      {daysOfWeek.map((day) => (
        <TouchableOpacity
          key={day.value}
          style={[
            styles.dayOption,
            selectedDay === day.value && styles.selectedDay
          ]}
          onPress={() => updateSession(weekIndex, sessionIndex, 'day_of_week', day.value)}
        >
          <Text style={[
            styles.dayText,
            selectedDay === day.value && styles.selectedDayText
          ]}>
            {day.short}
          </Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderSession = (session, weekIndex, sessionIndex) => (
    <View key={sessionIndex} style={styles.sessionCard}>
      <View style={styles.sessionHeader}>
        <Text style={styles.sessionTitle}>Sesión {sessionIndex + 1}</Text>
        <TouchableOpacity
          style={styles.deleteButton}
          onPress={() => removeSession(weekIndex, sessionIndex)}
        >
          <Ionicons name="trash-outline" size={20} color={COLORS.error} />
        </TouchableOpacity>
      </View>

      <View style={styles.sessionContent}>
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Nombre de la sesión</Text>
          <InputField
            placeholder="Ej: Tren Superior A"
            value={session.name}
            onChangeText={(value) => updateSession(weekIndex, sessionIndex, 'name', value)}
          />
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Día de la semana</Text>
          {renderDaySelector(weekIndex, sessionIndex, session.day_of_week)}
        </View>

        <View style={styles.inputGroup}>
          <Text style={styles.label}>Descripción</Text>
          <InputField
            placeholder="Describe los grupos musculares o tipo de entrenamiento..."
            value={session.description}
            onChangeText={(value) => updateSession(weekIndex, sessionIndex, 'description', value)}
            multiline={true}
            numberOfLines={2}
            style={styles.descriptionInput}
          />
        </View>

        <View style={styles.sessionInfo}>
          <View style={styles.infoItem}>
            <Ionicons name="barbell-outline" size={16} color={COLORS.textMedium} />
            <Text style={styles.infoText}>
              {session.exercise_blocks.length} bloques de ejercicios
            </Text>
          </View>
          <View style={styles.infoItem}>
            <Ionicons name="calendar-outline" size={16} color={COLORS.textMedium} />
            <Text style={styles.infoText}>
              {daysOfWeek.find(d => d.value === session.day_of_week)?.label}
            </Text>
          </View>
        </View>
      </View>
    </View>
  );

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
        <View style={styles.weekActions}>
          <Text style={styles.sessionCount}>
            {week.training_sessions.length} sesiones
          </Text>
          <Ionicons
            name={expandedWeek === weekIndex ? "chevron-up" : "chevron-down"}
            size={20}
            color={COLORS.textMedium}
          />
        </View>
      </TouchableOpacity>

      {expandedWeek === weekIndex && (
        <View style={styles.weekContent}>
          {week.training_sessions.map((session, sessionIndex) =>
            renderSession(session, weekIndex, sessionIndex)
          )}
          
          <TouchableOpacity
            style={styles.addSessionButton}
            onPress={() => addSession(weekIndex)}
          >
            <Ionicons name="add" size={20} color={COLORS.primary} />
            <Text style={styles.addSessionText}>Agregar Sesión</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );

  const totalSessions = programData.training_weeks.reduce(
    (total, week) => total + week.training_sessions.length,
    0
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.sectionTitle}>Sesiones de Entrenamiento</Text>
      <Text style={styles.sectionDescription}>
        Configura las sesiones de entrenamiento para cada semana
      </Text>

      <View style={styles.summary}>
        <Text style={styles.summaryTitle}>Resumen</Text>
        <View style={styles.summaryItems}>
          <View style={styles.summaryItem}>
            <Ionicons name="fitness" size={20} color={COLORS.primary} />
            <Text style={styles.summaryText}>
              {totalSessions} sesiones totales
            </Text>
          </View>
          <View style={styles.summaryItem}>
            <Ionicons name="calendar" size={20} color={COLORS.primary} />
            <Text style={styles.summaryText}>
              {programData.duration_weeks} semanas
            </Text>
          </View>
        </View>
      </View>

      <View style={styles.weeksContainer}>
        {programData.training_weeks.map((week, weekIndex) => renderWeek(week, weekIndex))}
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
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  summaryText: {
    fontSize: FONT_SIZE.sm,
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
  weekActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  sessionCount: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  weekContent: {
    padding: SPACING.md,
    gap: SPACING.md,
  },
  sessionCard: {
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    borderWidth: 1,
    borderColor: COLORS.input,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  sessionTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  deleteButton: {
    padding: SPACING.xs,
  },
  sessionContent: {
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
  descriptionInput: {
    minHeight: 60,
    textAlignVertical: 'top',
  },
  daySelector: {
    flexDirection: 'row',
    gap: SPACING.xs,
  },
  dayOption: {
    flex: 1,
    paddingVertical: SPACING.sm,
    backgroundColor: COLORS.input,
    borderRadius: BORDER_RADIUS.sm,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  selectedDay: {
    borderColor: COLORS.primary,
    backgroundColor: COLORS.primary,
  },
  dayText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    fontWeight: '600',
  },
  selectedDayText: {
    color: COLORS.background,
  },
  sessionInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: SPACING.sm,
    borderTopWidth: 1,
    borderTopColor: COLORS.input,
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
  addSessionButton: {
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
  addSessionText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.primary,
    fontWeight: '600',
  },
});

export default CreateProgramSessions;
