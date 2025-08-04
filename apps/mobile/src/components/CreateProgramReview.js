import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';

const CreateProgramReview = ({ programData }) => {
  // Función para obtener el nombre del tipo de programa
  const getProgramTypeName = (type) => {
    const names = {
      'strength': 'Fuerza',
      'hypertrophy': 'Hipertrofia',
      'peaking': 'Picos/Competición',
    };
    return names[type] || type;
  };

  // Función para obtener el nombre del día
  const getDayName = (day) => {
    const days = {
      1: 'Lunes',
      2: 'Martes',
      3: 'Miércoles',
      4: 'Jueves',
      5: 'Viernes',
      6: 'Sábado',
      7: 'Domingo',
    };
    return days[day] || 'Desconocido';
  };

  // Calcular estadísticas
  const totalSessions = programData.training_weeks.reduce(
    (total, week) => total + week.training_sessions.length,
    0
  );

  const totalExercises = programData.training_weeks.reduce(
    (total, week) => total + week.training_sessions.reduce(
      (sessionTotal, session) => sessionTotal + session.exercise_blocks.reduce(
        (blockTotal, block) => blockTotal + block.programmed_exercises.length,
        0
      ),
      0
    ),
    0
  );

  const totalBlocks = programData.training_weeks.reduce(
    (total, week) => total + week.training_sessions.reduce(
      (sessionTotal, session) => sessionTotal + session.exercise_blocks.length,
      0
    ),
    0
  );

  const renderProgramInfo = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Información del Programa</Text>
      
      <View style={styles.infoCard}>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Nombre:</Text>
          <Text style={styles.infoValue}>{programData.name}</Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Tipo:</Text>
          <Text style={styles.infoValue}>{getProgramTypeName(programData.program_type)}</Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Duración:</Text>
          <Text style={styles.infoValue}>
            {programData.duration_weeks} semana{programData.duration_weeks !== 1 ? 's' : ''}
          </Text>
        </View>
        
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Estado:</Text>
          <Text style={[styles.infoValue, programData.is_active && styles.activeText]}>
            {programData.is_active ? 'Activo' : 'Inactivo'}
          </Text>
        </View>
      </View>
      
      <View style={styles.descriptionCard}>
        <Text style={styles.descriptionTitle}>Descripción</Text>
        <Text style={styles.descriptionText}>{programData.description}</Text>
      </View>
    </View>
  );

  const renderStatistics = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Estadísticas del Programa</Text>
      
      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <View style={styles.statIcon}>
            <Ionicons name="calendar" size={24} color={COLORS.primary} />
          </View>
          <Text style={styles.statValue}>{programData.duration_weeks}</Text>
          <Text style={styles.statLabel}>Semanas</Text>
        </View>
        
        <View style={styles.statCard}>
          <View style={styles.statIcon}>
            <Ionicons name="fitness" size={24} color={COLORS.info} />
          </View>
          <Text style={styles.statValue}>{totalSessions}</Text>
          <Text style={styles.statLabel}>Sesiones</Text>
        </View>
        
        <View style={styles.statCard}>
          <View style={styles.statIcon}>
            <Ionicons name="layers" size={24} color={COLORS.warning} />
          </View>
          <Text style={styles.statValue}>{totalBlocks}</Text>
          <Text style={styles.statLabel}>Bloques</Text>
        </View>
        
        <View style={styles.statCard}>
          <View style={styles.statIcon}>
            <Ionicons name="barbell" size={24} color={COLORS.success} />
          </View>
          <Text style={styles.statValue}>{totalExercises}</Text>
          <Text style={styles.statLabel}>Ejercicios</Text>
        </View>
      </View>
    </View>
  );

  const renderWeeksSummary = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>Resumen por Semanas</Text>
      
      {programData.training_weeks.map((week, weekIndex) => (
        <View key={weekIndex} style={styles.weekSummaryCard}>
          <View style={styles.weekSummaryHeader}>
            <View style={styles.weekNumber}>
              <Text style={styles.weekNumberText}>{week.week_number}</Text>
            </View>
            <View style={styles.weekInfo}>
              <Text style={styles.weekTitle}>{week.description}</Text>
              <Text style={styles.weekSubtitle}>
                {week.training_sessions.length} sesiones
              </Text>
            </View>
          </View>
          
          <View style={styles.sessionsList}>
            {week.training_sessions.map((session, sessionIndex) => (
              <View key={sessionIndex} style={styles.sessionSummary}>
                <View style={styles.sessionHeader}>
                  <Text style={styles.sessionName}>{session.name}</Text>
                  <Text style={styles.sessionDay}>{getDayName(session.day_of_week)}</Text>
                </View>
                
                <View style={styles.sessionStats}>
                  <View style={styles.sessionStat}>
                    <Ionicons name="layers-outline" size={14} color={COLORS.textMedium} />
                    <Text style={styles.sessionStatText}>
                      {session.exercise_blocks.length} bloques
                    </Text>
                  </View>
                  
                  <View style={styles.sessionStat}>
                    <Ionicons name="barbell-outline" size={14} color={COLORS.textMedium} />
                    <Text style={styles.sessionStatText}>
                      {session.exercise_blocks.reduce((total, block) => total + block.programmed_exercises.length, 0)} ejercicios
                    </Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        </View>
      ))}
    </View>
  );

  const renderConfirmation = () => (
    <View style={styles.section}>
      <View style={styles.confirmationCard}>
        <View style={styles.confirmationIcon}>
          <Ionicons name="checkmark-circle" size={48} color={COLORS.success} />
        </View>
        <Text style={styles.confirmationTitle}>¡Programa Listo!</Text>
        <Text style={styles.confirmationText}>
          Tu programa de entrenamiento ha sido configurado correctamente. 
          Revisa todos los detalles y presiona "Crear Programa" para finalizar.
        </Text>
      </View>
    </View>
  );

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.mainTitle}>Revisar y Crear Programa</Text>
      
      {renderProgramInfo()}
      {renderStatistics()}
      {renderWeeksSummary()}
      {renderConfirmation()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingVertical: SPACING.lg,
  },
  mainTitle: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.xl,
    textAlign: 'center',
  },
  section: {
    marginBottom: SPACING.xl,
  },
  sectionTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.md,
  },
  infoCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    marginBottom: SPACING.md,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.input,
  },
  infoLabel: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    fontWeight: '500',
  },
  infoValue: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textDark,
    fontWeight: '600',
  },
  activeText: {
    color: COLORS.success,
  },
  descriptionCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
  },
  descriptionTitle: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.sm,
  },
  descriptionText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    lineHeight: 20,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: SPACING.md,
  },
  statCard: {
    flex: 1,
    minWidth: '45%',
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    alignItems: 'center',
  },
  statIcon: {
    marginBottom: SPACING.sm,
  },
  statValue: {
    fontSize: FONT_SIZE.xxl,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  statLabel: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  weekSummaryCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    marginBottom: SPACING.md,
    overflow: 'hidden',
  },
  weekSummaryHeader: {
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
  weekInfo: {
    flex: 1,
  },
  weekTitle: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  weekSubtitle: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  sessionsList: {
    padding: SPACING.md,
    gap: SPACING.md,
  },
  sessionSummary: {
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.sm,
    padding: SPACING.sm,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.sm,
  },
  sessionName: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textDark,
  },
  sessionDay: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.primary,
    fontWeight: '600',
  },
  sessionStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sessionStat: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  sessionStatText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  confirmationCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.xl,
    alignItems: 'center',
  },
  confirmationIcon: {
    marginBottom: SPACING.md,
  },
  confirmationTitle: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.md,
  },
  confirmationText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default CreateProgramReview;
