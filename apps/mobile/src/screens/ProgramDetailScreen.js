import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  Alert,
  FlatList,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons, FontAwesome5 } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS } from '../constants/theme';
import { useTrainingPrograms } from '../hooks/useTrainingPrograms';
import { LoadingIndicator } from '../components';

const ProgramDetailScreen = () => {
  const router = useRouter();
  const { programId } = useLocalSearchParams();
  const [program, setProgram] = React.useState(null);
  const [weeks, setWeeks] = React.useState([]);
  const [loading, setLoading] = React.useState(true);

  const {
    getProgram,
    getProgramWithProgress,
    getProgramProgress,
    checkSessionStatus,
    startSession,
    isLoading,
  } = useTrainingPrograms();

  React.useEffect(() => {
    loadProgramData();
  }, [programId]);

  const loadProgramData = async () => {
    setLoading(true);
    try {
      // Obtener programa con información de progreso incluida
      const programData = await getProgramWithProgress(programId);
      setProgram(programData);
      
      // Establecer las semanas directamente
      if (programData.training_weeks) {
        setWeeks(programData.training_weeks);
      }
    } catch (error) {
      console.error('Error loading program:', error);
      Alert.alert('Error', 'No se pudo cargar el programa');
      router.back();
    } finally {
      setLoading(false);
    }
  };

  const handleWeekPress = (week) => {
    // Navegar a la pantalla de sesiones de la semana
    router.push(`/_week-detail?weekId=${week.id}&programId=${programId}&weekNumber=${week.week_number}`);
  };

  const calculateWeekProgress = (week) => {
    if (!week.training_sessions || week.training_sessions.length === 0) return 0;
    
    // Calcular el progreso real basado en sesiones completadas
    const completedSessions = week.training_sessions.filter(session => session.is_completed).length;
    const totalSessions = week.training_sessions.length;
    
    return Math.round((completedSessions / totalSessions) * 100);
  };

  const renderWeek = ({ item }) => {
    const progress = calculateWeekProgress(item);
    const totalSessions = item.training_sessions?.length || 0;
    const completedSessions = item.training_sessions?.filter(session => session.is_completed).length || 0;

    return (
      <TouchableOpacity
        style={styles.weekCard}
        onPress={() => handleWeekPress(item)}
      >
        <View style={styles.weekHeader}>
          <View style={styles.weekInfo}>
            <Text style={styles.weekTitle}>Semana {item.week_number}</Text>
            <Text style={styles.weekSessions}>
              {totalSessions} sesión{totalSessions !== 1 ? 'es' : ''}
            </Text>
          </View>
          <View style={styles.weekStatus}>
            <View style={styles.progressContainer}>
              <Text style={styles.progressText}>{progress}%</Text>
              <View style={styles.progressBar}>
                <View 
                  style={[
                    styles.progressFill, 
                    { width: `${progress}%` }
                  ]} 
                />
              </View>
            </View>
            <Ionicons name="chevron-forward" size={20} color={COLORS.textMedium} />
          </View>
        </View>
        
        <Text style={styles.weekDescription} numberOfLines={2}>
          {item.description || `Semana ${item.week_number} del programa de entrenamiento`}
        </Text>
        
        <View style={styles.weekStats}>
          <View style={styles.statItem}>
            <FontAwesome5 name="check-circle" size={14} color={COLORS.success} />
            <Text style={styles.statText}>
              {completedSessions}/{totalSessions} completadas
            </Text>
          </View>
          <View style={styles.statItem}>
            <FontAwesome5 name="calendar" size={14} color={COLORS.primary} />
            <Text style={styles.statText}>
              {totalSessions} días
            </Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

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

  const getProgramTypeName = (type) => {
    const names = {
      'strength': 'Fuerza',
      'hypertrophy': 'Hipertrofia',
      'peaking': 'Picos/Competición',
    };
    return names[type?.toLowerCase()] || (type || 'General');
  };

  if (loading) {
    return <LoadingIndicator />;
  }

  if (!program) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Programa no encontrado</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()}>
          <Ionicons name="arrow-back" size={24} color={COLORS.textDark} />
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>{program.name}</Text>
          <Text style={styles.headerSubtitle}>
            {weeks.length} semanas • {program.duration_weeks} sem de duración
          </Text>
        </View>
        <TouchableOpacity onPress={() => {}}>
          <Ionicons name="ellipsis-horizontal" size={24} color={COLORS.textDark} />
        </TouchableOpacity>
      </View>

      {/* Program Quick Info */}
      <View style={styles.quickInfo}>
        <Text style={styles.programDescription} numberOfLines={2}>
          {program.description || 'Sin descripción disponible'}
        </Text>
        <View style={styles.programStats}>
          <View style={styles.statBadge}>
            <Text style={styles.statLabel}>Tipo</Text>
            <Text style={styles.statValue}>{getProgramTypeName(program.program_type)}</Text>
          </View>
          <View style={styles.statBadge}>
            <Text style={styles.statLabel}>Duración</Text>
            <Text style={styles.statValue}>{program.duration_weeks} sem</Text>
          </View>
          <View style={styles.statBadge}>
            <Text style={styles.statLabel}>Semanas</Text>
            <Text style={styles.statValue}>{weeks.length}</Text>
          </View>
        </View>
      </View>

      {/* Weeks List */}
      <View style={styles.weeksContainer}>
        <Text style={styles.sectionTitle}>Semanas del Programa</Text>
        <FlatList
          data={weeks}
          renderItem={renderWeek}
          keyExtractor={(item) => item.id.toString()}
          showsVerticalScrollIndicator={false}
          contentContainerStyle={styles.weeksList}
          ItemSeparatorComponent={() => <View style={styles.weekSeparator} />}
          ListEmptyComponent={() => (
            <View style={styles.emptyContainer}>
              <FontAwesome5 name="calendar-times" size={48} color={COLORS.textLight} />
              <Text style={styles.emptyText}>
                No hay semanas configuradas en este programa
              </Text>
            </View>
          )}
        />
      </View>
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
    justifyContent: 'space-between',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.md,
    backgroundColor: COLORS.card,
    ...SHADOWS.light,
  },
  headerCenter: {
    flex: 1,
    marginHorizontal: SPACING.md,
  },
  headerTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: 'bold',
    color: COLORS.textDark,
    textAlign: 'center',
  },
  headerSubtitle: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    textAlign: 'center',
    marginTop: SPACING.xs,
  },
  quickInfo: {
    backgroundColor: COLORS.card,
    padding: SPACING.md,
    marginVertical: SPACING.sm,
    marginHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    ...SHADOWS.light,
  },
  programDescription: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    lineHeight: 20,
    marginBottom: SPACING.md,
  },
  programStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  statBadge: {
    alignItems: 'center',
    backgroundColor: COLORS.input,
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    borderRadius: BORDER_RADIUS.sm,
    minWidth: 80,
  },
  statLabel: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
    marginBottom: SPACING.xs,
  },
  statValue: {
    fontSize: FONT_SIZE.sm,
    fontWeight: 'bold',
    color: COLORS.textDark,
  },
  sessionsContainer: {
    flex: 1,
    paddingHorizontal: SPACING.md,
  },
  sectionTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.md,
  },
  sessionsList: {
    paddingBottom: SPACING.xl,
  },
  sessionCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    ...SHADOWS.light,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
  },
  sessionInfo: {
    flex: 1,
  },
  sessionTitle: {
    fontSize: FONT_SIZE.md,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  sessionWeek: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.primary,
    fontWeight: '600',
  },
  sessionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  activeSessionBadge: {
    backgroundColor: COLORS.success,
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    borderRadius: BORDER_RADIUS.sm,
  },
  activeSessionText: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.background,
    fontWeight: 'bold',
  },
  sessionDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    lineHeight: 18,
    marginBottom: SPACING.sm,
  },
  sessionStats: {
    flexDirection: 'row',
    gap: SPACING.lg,
  },
  statItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  statText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  sessionSeparator: {
    height: SPACING.md,
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
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: FONT_SIZE.lg,
    color: COLORS.error,
  },
  // Estilos para semanas
  weeksContainer: {
    flex: 1,
    paddingHorizontal: SPACING.md,
  },
  weeksList: {
    paddingBottom: SPACING.xl,
  },
  weekCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    ...SHADOWS.light,
  },
  weekHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
  },
  weekInfo: {
    flex: 1,
  },
  weekTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  weekSessions: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.primary,
    fontWeight: '600',
  },
  weekStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  progressContainer: {
    alignItems: 'center',
    minWidth: 60,
  },
  progressText: {
    fontSize: FONT_SIZE.sm,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  progressBar: {
    width: 50,
    height: 6,
    backgroundColor: COLORS.border,
    borderRadius: 3,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: COLORS.success,
    borderRadius: 3,
  },
  weekDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    lineHeight: 18,
    marginBottom: SPACING.sm,
  },
  weekStats: {
    flexDirection: 'row',
    gap: SPACING.lg,
  },
  weekSeparator: {
    height: SPACING.md,
  },
});

export default ProgramDetailScreen;
