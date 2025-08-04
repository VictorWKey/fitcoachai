import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Pressable } from 'react-native';
import { FontAwesome5, Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS } from '../constants/theme';
import { formatDate } from '../utils/dateUtils';

const ProgramCard = ({ program, onPress, onOptionsPress, onViewSessions }) => {
  // Función para obtener el color según el tipo de programa
  const getProgramTypeColor = (type) => {
    const colors = {
      'strength': COLORS.error,
      'hypertrophy': COLORS.primary,
      'peaking': COLORS.secondary,
    };
    return colors[type?.toLowerCase()] || COLORS.textMedium;
  };

  // Función para obtener el nombre del tipo de programa
  const getProgramTypeName = (type) => {
    const names = {
      'strength': 'Fuerza',
      'hypertrophy': 'Hipertrofia',
      'peaking': 'Picos/Competición',
    };
    return names[type?.toLowerCase()] || (type || 'General');
  };

  // Función para formatear la fecha
  const formatProgramDate = (dateString) => {
    try {
      return formatDate(dateString);
    } catch (error) {
      return 'Fecha desconocida';
    }
  };

  return (
    <TouchableOpacity style={styles.container} onPress={onPress}>
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Text style={styles.title} numberOfLines={1}>
            {program.name}
          </Text>
          <View style={styles.statusContainer}>
            {program.is_active && (
              <View style={styles.activeIndicator}>
                <Text style={styles.activeText}>ACTIVO</Text>
              </View>
            )}
            {program.is_ai_generated && (
              <View style={styles.aiIndicator}>
                <FontAwesome5 name="robot" size={12} color={COLORS.textDark} />
              </View>
            )}
          </View>
        </View>
        
        <Pressable 
          style={styles.optionsButton}
          onPress={onOptionsPress}
          android_ripple={{ color: 'rgba(255,255,255,0.2)', radius: 20 }}
        >
          <Ionicons name="ellipsis-vertical" size={20} color={COLORS.textMedium} />
        </Pressable>
      </View>

      <View style={styles.content}>
        <Text style={styles.description} numberOfLines={2}>
          {program.description || 'Sin descripción'}
        </Text>

        <View style={styles.infoContainer}>
          <View style={styles.infoItem}>
            <FontAwesome5 name="calendar-alt" size={14} color={COLORS.textMedium} />
            <Text style={styles.infoText}>
              {program.duration_weeks} semana{program.duration_weeks !== 1 ? 's' : ''}
            </Text>
          </View>

          <View style={[styles.infoItem, styles.programType]}>
            <View 
              style={[
                styles.typeIndicator, 
                { backgroundColor: getProgramTypeColor(program.program_type) }
              ]} 
            />
            <Text style={styles.infoText}>
              {getProgramTypeName(program.program_type)}
            </Text>
          </View>
        </View>

        <View style={styles.footer}>
          <Text style={styles.dateText}>
            Creado: {formatProgramDate(program.created_at)}
          </Text>
          <Text style={styles.dateText}>
            Actualizado: {formatProgramDate(program.updated_at)}
          </Text>
        </View>

        {/* Botones de acción */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity 
            style={styles.actionButton} 
            onPress={onViewSessions}
          >
            <FontAwesome5 name="list" size={16} color={COLORS.primary} />
            <Text style={styles.actionButtonText}>Ver Sesiones</Text>
          </TouchableOpacity>
        </View>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.md,
    ...SHADOWS.small,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingHorizontal: SPACING.md,
    paddingVertical: SPACING.sm,
    backgroundColor: COLORS.input,
  },
  titleContainer: {
    flex: 1,
    marginRight: SPACING.sm,
  },
  title: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textDark,
    marginBottom: SPACING.xs,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.sm,
  },
  activeIndicator: {
    backgroundColor: COLORS.success,
    paddingHorizontal: SPACING.sm,
    paddingVertical: 2,
    borderRadius: BORDER_RADIUS.sm,
  },
  activeText: {
    fontSize: FONT_SIZE.xs,
    fontWeight: '600',
    color: COLORS.background,
  },
  aiIndicator: {
    backgroundColor: COLORS.secondary,
    width: 20,
    height: 20,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  optionsButton: {
    padding: SPACING.xs,
    borderRadius: BORDER_RADIUS.sm,
  },
  content: {
    padding: SPACING.md,
  },
  description: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    lineHeight: 20,
    marginBottom: SPACING.md,
  },
  infoContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: SPACING.md,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  programType: {
    backgroundColor: COLORS.input,
    paddingHorizontal: SPACING.sm,
    paddingVertical: SPACING.xs,
    borderRadius: BORDER_RADIUS.sm,
  },
  typeIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  infoText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: SPACING.sm,
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    marginBottom: SPACING.sm,
  },
  actionsContainer: {
    flexDirection: 'row',
    gap: SPACING.sm,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.sm,
    paddingHorizontal: SPACING.md,
    backgroundColor: COLORS.input,
    borderRadius: BORDER_RADIUS.sm,
    gap: SPACING.xs,
  },
  actionButtonText: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.primary,
    fontWeight: '600',
  },
  dateText: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textLight,
  },
});

export default ProgramCard;
