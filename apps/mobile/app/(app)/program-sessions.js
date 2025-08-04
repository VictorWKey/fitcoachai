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

const ProgramSessionsScreen = () => {
  const router = useRouter();
  const { programId } = useLocalSearchParams();
  const insets = useSafeAreaInsets();
  const [program, setProgram] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const { getProgram } = useTrainingPrograms();


  useEffect(() => {
    // Validar que tenemos el parámetro necesario
    if (!programId) {
      setError('Falta el identificador del programa');
      setIsLoading(false);
      return;
    }
    
    // Validar que el ID es un número válido
    const programIdNum = parseInt(programId);
    
    if (isNaN(programIdNum)) {
      setError('El identificador del programa debe ser un número válido');
      setIsLoading(false);
      return;
    }
    
    loadProgram();
  }, [programId]);

  const loadProgram = async () => {
    setIsLoading(true);
    setError(null);
    try {
      console.log(`Cargando programa: programId=${programId}`);
      const programData = await getProgram(programId);
      setProgram(programData);
    } catch (err) {
      console.error(`Error al cargar programa ${programId}:`, err);
      if (err.message && err.message.includes('Recurso no encontrado')) {
        setError('El programa solicitado no existe o ha sido eliminado');
      } else {
        setError('No se pudo cargar el programa');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleWeekPress = (weekNumber) => {
    router.push({
      pathname: '/week-sessions',
      params: { 
        programId: programId.toString(),
        weekNumber: weekNumber.toString()
      }
    });
  };

  const renderWeek = ({ item, index }) => {
    const sessionsCount = item.training_sessions?.length || 0;
    
    return (
      <TouchableOpacity
        style={styles.weekCard}
        onPress={() => handleWeekPress(item.week_number)}
      >
        <View style={styles.weekHeader}>
          <View style={styles.weekNumberContainer}>
            <Text style={styles.weekNumber}>{item.week_number}</Text>
          </View>
          <View style={styles.weekInfo}>
            <Text style={styles.weekTitle}>Semana {item.week_number}</Text>
            <Text style={styles.weekDescription} numberOfLines={2}>
              {item.description || 'Sin descripción'}
            </Text>
          </View>
          <View style={styles.weekStats}>
            <Text style={styles.sessionsCount}>{sessionsCount}</Text>
            <Text style={styles.sessionsLabel}>sesiones</Text>
          </View>
        </View>
        
        <View style={styles.weekFooter}>
          <FontAwesome5 name="calendar-alt" size={14} color={COLORS.textMedium} />
          <Text style={styles.weekFooterText}>
            {sessionsCount} sesión{sessionsCount !== 1 ? 'es' : ''} programada{sessionsCount !== 1 ? 's' : ''}
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
          <Text style={styles.loadingText}>Cargando programa...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error || !program) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <FontAwesome5 name="exclamation-triangle" size={48} color={COLORS.error} />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadProgram}>
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
          // Padding que queria quitar
          // paddingTop: insets.top + SPACING.sm, 
          // paddingBottom: sessionPadding > 0 ? SPACING.lg : SPACING.sm
        }
      ]}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color={COLORS.textDark} />
        </TouchableOpacity>
        <View style={styles.headerContent}>
          <Text style={styles.title} numberOfLines={1}>
            {program.name}
          </Text>
        </View>
      </View>

      <FlatList
        data={program.training_weeks}
        renderItem={renderWeek}
        keyExtractor={(item) => item.week_number.toString()}
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
              No hay semanas configuradas en este programa
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
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  subtitle: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  listContainer: {
    padding: SPACING.md,
  },
  weekCard: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    padding: SPACING.md,
    ...SHADOWS.small,
  },
  weekHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: SPACING.sm,
  },
  weekNumberContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: COLORS.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: SPACING.md,
  },
  weekNumber: {
    fontSize: FONT_SIZE.md,
    fontWeight: 'bold',
    color: COLORS.background,
  },
  weekInfo: {
    flex: 1,
    marginRight: SPACING.sm,
  },
  weekTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  weekDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    lineHeight: 18,
  },
  weekStats: {
    alignItems: 'center',
  },
  sessionsCount: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  sessionsLabel: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
  },
  weekFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: SPACING.sm,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
  },
  weekFooterText: {
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

export default ProgramSessionsScreen;
