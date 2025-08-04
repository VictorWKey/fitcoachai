import React from 'react';
import { View, Text, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

/**
 * Componente que renderiza la interfaz según el estado de la sesión
 * Basado en el session_workflow_guide.md
 */
const SessionStateInterface = ({ 
  sessionState, 
  sessionData, 
  sessionName, 
  onStartSession, 
  onFinishSession,
  onResumeSession,
  onAbandonSession,
  styles,
  COLORS 
}) => {
  
  const renderInterface = () => {
    switch (sessionState) {
      case 'never_started':
        return (
          <View style={styles.stateContainer}>
            <View style={styles.stateIcon}>
              <Ionicons name="play-circle-outline" size={48} color={COLORS.primary} />
            </View>
            <Text style={styles.stateTitle}>Sesión Lista para Iniciar</Text>
            <Text style={styles.stateDescription}>
              Esta sesión aún no ha sido iniciada. Una vez que la inicies, podrás registrar todos tus ejercicios y sets.
            </Text>
            <TouchableOpacity style={styles.primaryActionButton} onPress={onStartSession}>
              <Ionicons name="play" size={20} color={COLORS.background} />
              <Text style={styles.primaryActionText}>Iniciar Entrenamiento</Text>
            </TouchableOpacity>
          </View>
        );
        
      case 'active':
        return (
          <View style={styles.stateContainer}>
            <View style={[styles.stateIcon, { backgroundColor: COLORS.successLight }]}>
              <Ionicons name="fitness" size={48} color={COLORS.success} />
            </View>
            <Text style={[styles.stateTitle, { color: COLORS.success }]}>Sesión Activa</Text>
            <Text style={styles.stateDescription}>
              ¡Perfecto! Tu sesión está activa. Registra tus ejercicios tocando cada uno y completa todos los sets programados.
            </Text>
            <TouchableOpacity style={styles.secondaryActionButton} onPress={onFinishSession}>
              <Ionicons name="checkmark-circle" size={20} color={COLORS.error} />
              <Text style={[styles.secondaryActionText, { color: COLORS.error }]}>Finalizar Sesión</Text>
            </TouchableOpacity>
          </View>
        );
        
      case 'auto_paused':
        return (
          <View style={styles.stateContainer}>
            <View style={[styles.stateIcon, { backgroundColor: COLORS.warningLight }]}>
              <Ionicons name="pause-circle" size={48} color={COLORS.warning} />
            </View>
            <Text style={[styles.stateTitle, { color: COLORS.warning }]}>Sesión Auto-Pausada</Text>
            <Text style={styles.stateDescription}>
              Tu entrenamiento fue pausado automáticamente por inactividad. ¿Qué deseas hacer?
            </Text>
            <View style={styles.actionButtonsRow}>
              <TouchableOpacity style={styles.primaryActionButton} onPress={onResumeSession}>
                <Text style={styles.primaryActionText}>Continuar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.secondaryActionButton} onPress={onFinishSession}>
                <Text style={styles.secondaryActionText}>Finalizar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.dangerActionButton} onPress={onAbandonSession}>
                <Text style={styles.dangerActionText}>Abandonar</Text>
              </TouchableOpacity>
            </View>
          </View>
        );
        
      case 'completed':
        return (
          <View style={styles.stateContainer}>
            <View style={[styles.stateIcon, { backgroundColor: COLORS.primaryLight }]}>
              <Ionicons name="checkmark-circle" size={48} color={COLORS.primary} />
            </View>
            <Text style={[styles.stateTitle, { color: COLORS.primary }]}>Sesión Completada</Text>
            <Text style={styles.stateDescription}>
              ¡Excelente trabajo! Esta sesión ya fue finalizada. Puedes revisar tus logs, hacer correcciones o agregar ejercicios adicionales.
            </Text>
            <Text style={styles.stateNote}>
              💡 Tip: Puedes tocar cualquier ejercicio para ver, editar o agregar nuevos sets.
            </Text>
          </View>
        );
        
      default:
        return null;
    }
  };

  return renderInterface();
};

export default SessionStateInterface;
