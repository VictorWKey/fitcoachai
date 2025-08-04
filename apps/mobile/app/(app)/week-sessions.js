import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { FontAwesome5, Ionicons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS } from '../../src/constants/theme';
import { useTrainingPrograms } from '../../src/hooks/useTrainingPrograms';

const WeekSessionsScreen = () => {
  const router = useRouter();
  const { programId, weekNumber } = useLocalSearchParams();
  const insets = useSafeAreaInsets();
  const [weekData, setWeekData] = useState(null);
  const [programName, setProgramName] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const { getProgram } = useTrainingPrograms();

  // Mapeo de días de la semana
  const daysOfWeek = {
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes',
    6: 'Sábado',
    7: 'Domingo'
  };

  useEffect(() => {
    // Validar que tenemos los parámetros necesarios
    if (!programId || !weekNumber) {
      setError('Faltan parámetros requeridos para cargar la semana');
      setIsLoading(false);
      return;
    }
    
    // Validar que los IDs son números válidos
    const programIdNum = parseInt(programId);
    const weekNum = parseInt(weekNumber);
    
    if (isNaN(programIdNum) || isNaN(weekNum)) {
      setError('Los identificadores del programa y semana deben ser números válidos');
      setIsLoading(false);
      return;
    }
    
    loadWeekData();
  }, [programId, weekNumber]);

  const loadWeekData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log(`Cargando datos de semana: programId=${programId}, weekNumber=${weekNumber}`);
      const programData = await getProgram(programId);
      setProgramName(programData.name);
      
      const week = programData.training_weeks?.find(
        w => w.week_number === parseInt(weekNumber)
      );
      
      if (week) {
        setWeekData(week);
      } else {
        setError('No se encontró la semana especificada');
      }
    } catch (err) {
      console.error(`Error al cargar datos de semana ${weekNumber}:`, err);
      if (err.message && err.message.includes('Recurso no encontrado')) {
        setError('El programa solicitado no existe o ha sido eliminado');
      } else {
        setError('No se pudo cargar los datos de la semana');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSessionPress = (session) => {
    router.push({
      pathname: '/session-exercises',
      params: { 
        programId: programId.toString(),
        sessionId: session.id.toString(),
        sessionName: session.name,
        weekNumber: weekNumber.toString()
      }
    });
  };

  const getSessionDayText = (dayOfWeek) => {
    return dayOfWeek !== null && dayOfWeek !== undefined 
      ? daysOfWeek[dayOfWeek] || 'Sin día asignado'
      : 'Sin día asignado';
  };

  const renderSession = ({ item, index }) => {
    const exerciseBlocksCount = item.exercise_blocks?.length || 0;
    const totalExercises = item.exercise_blocks?.reduce((total, block) => {
      return total + (block.programmed_exercises?.length || 0);
    }, 0) || 0;

    return (
      <TouchableOpacity
        style={styles.sessionCard}
        onPress={() => handleSessionPress(item)}
      >
        <View style={styles.sessionHeader}>
          <View style={styles.sessionNumberContainer}>
            <Text style={styles.sessionNumber}>{index + 1}</Text>
          </View>
          <View style={styles.sessionInfo}>
            <Text style={styles.sessionName} numberOfLines={1}>
              {item.name}
            </Text>
            <Text style={styles.sessionDescription} numberOfLines={2}>
              {item.description || 'Sin descripción'}
            </Text>
            <Text style={styles.sessionDay}>
              📅 {getSessionDayText(item.day_of_week)}
            </Text>
          </View>
          <View style={styles.sessionStats}>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{exerciseBlocksCount}</Text>
              <Text style={styles.statLabel}>bloques</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statNumber}>{totalExercises}</Text>
              <Text style={styles.statLabel}>ejercicios</Text>
            </View>
          </View>
        </View>
        
        <View style={styles.sessionFooter}>
          <FontAwesome5 name="dumbbell" size={14} color={COLORS.textMedium} />
          <Text style={styles.sessionFooterText}>
            {exerciseBlocksCount} bloque{exerciseBlocksCount !== 1 ? 's' : ''} • {totalExercises} ejercicio{totalExercises !== 1 ? 's' : ''}
          </Text>
          <Ionicons name="chevron-forward" size={16} color={COLORS.textMedium} />
        </View>
      </TouchableOpacity>
    );
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={COLORS.primary} />
          <Text style={styles.loadingText}>Cargando sesiones...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error || !weekData) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <FontAwesome5 name="exclamation-triangle" size={48} color={COLORS.error} />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadWeekData}>
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
          onPress={() => router.push({
            pathname: '/program-sessions',
            params: { programId: programId.toString() }
          })}
        >
          <Ionicons name="arrow-back" size={24} color={COLORS.textDark} />
        </TouchableOpacity>
        <View style={styles.headerContent}>
          <Text style={styles.title}>Semana {weekNumber}</Text>
          <Text style={styles.subtitle} numberOfLines={1}>
            {programName}
          </Text>
          {weekData.description && (
            <Text style={styles.weekDescription} numberOfLines={2}>
              {weekData.description}
            </Text>
          )}
        </View>
      </View>

      <FlatList
        data={weekData.training_sessions}
        renderItem={renderSession}
        keyExtractor={(item) => item.id.toString()}
        contentContainerStyle={[
          styles.listContainer, 
          { 
            // paddingTop: sessionPadding + (sessionPadding > 0 ? SPACING.xl : SPACING.md),
            // paddingBottom: insets.bottom + SPACING.lg 
          }
        ]}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
        showsVerticalScrollIndicator={false}
        ListEmptyComponent={() => (
          <View style={styles.emptyContainer}>
            <FontAwesome5 name="calendar-times" size={48} color={COLORS.textLight} />
            <Text style={styles.emptyText}>
              No hay sesiones configuradas en esta semana
            </Text>
          </View>
        )}
      />
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
    alignItems: 'flex-start',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.card,
    ...SHADOWS.small,
  },
  backButton: {
    padding: SPACING.xs,
    marginRight: SPACING.sm,
    marginTop: SPACING.xs,
  },
  headerContent: {
    flex: 1,
  },
  title: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  subtitle: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    marginBottom: SPACING.xs,
  },
  weekDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    fontStyle: 'italic',
  },
  listContainer: {
    padding: SPACING.md,
  },
  sessionCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    ...SHADOWS.small,
  },
  sessionHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
  },
  sessionNumberContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: COLORS.secondary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  sessionNumber: {
    fontSize: FONT_SIZE.md,
    fontWeight: 'bold',
    color: COLORS.background,
  },
  sessionInfo: {
    flex: 1,
    marginRight: SPACING.sm,
  },
  sessionName: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  sessionDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    lineHeight: 18,
    marginBottom: SPACING.xs,
  },
  sessionDay: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.primary,
    fontWeight: '500',
  },
  sessionStats: {
    alignItems: 'center',
    gap: SPACING.sm,
  },
  statItem: {
    alignItems: 'center',
  },
  statNumber: {
    fontSize: FONT_SIZE.lg,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  statLabel: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
  },
  sessionFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: SPACING.sm,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  sessionFooterText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    flex: 1,
    marginLeft: SPACING.xs,
  },
  separator: {
    height: SPACING.md,
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
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: SPACING.xl,
  },
  emptyText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    textAlign: 'center',
    marginTop: SPACING.md,
  },
});

export default WeekSessionsScreen;
