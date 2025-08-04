import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Modal, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';
import { validateTempo, validateRPE, formatTempo, getRPEDescription, getTempoExamples } from '../utils/validationUtils';

const ValidationHelper = ({ type, value, onHelp }) => {
  const [showModal, setShowModal] = useState(false);

  const renderTempoHelp = () => (
    <ScrollView style={styles.helpContent}>
      <Text style={styles.helpTitle}>Formato de Tempo</Text>
      <Text style={styles.helpDescription}>
        El tempo se representa como "E-B-C-T" donde:
      </Text>
      
      <View style={styles.tempoExplanation}>
        <Text style={styles.tempoItem}>• <Text style={styles.bold}>E</Text> = Fase excéntrica (bajada) en segundos</Text>
        <Text style={styles.tempoItem}>• <Text style={styles.bold}>B</Text> = Pausa en posición inferior en segundos</Text>
        <Text style={styles.tempoItem}>• <Text style={styles.bold}>C</Text> = Fase concéntrica (subida) en segundos</Text>
        <Text style={styles.tempoItem}>• <Text style={styles.bold}>T</Text> = Pausa en posición superior en segundos</Text>
      </View>

      <Text style={styles.helpSubtitle}>Ejemplos válidos:</Text>
      {getTempoExamples().map((example, index) => (
        <View key={index} style={styles.exampleItem}>
          <Text style={styles.exampleTempo}>{example}</Text>
          <Text style={styles.exampleDescription}>{formatTempo(example)}</Text>
        </View>
      ))}

      <Text style={styles.helpNote}>
        <Text style={styles.bold}>X</Text> = Explosivo (máxima velocidad)
      </Text>
      <Text style={styles.helpNote}>
        También puedes usar formato de 3 partes: "E-B-C" (sin pausa superior)
      </Text>
    </ScrollView>
  );

  const renderRPEHelp = () => (
    <ScrollView style={styles.helpContent}>
      <Text style={styles.helpTitle}>Escala RPE</Text>
      <Text style={styles.helpDescription}>
        RPE (Rate of Perceived Exertion) - Esfuerzo percibido del 1 al 10
      </Text>
      
      <View style={styles.rpeScale}>
        <View style={styles.rpeItem}>
          <Text style={styles.rpeValue}>1-3</Text>
          <Text style={styles.rpeDescription}>Muy fácil</Text>
        </View>
        <View style={styles.rpeItem}>
          <Text style={styles.rpeValue}>4-6</Text>
          <Text style={styles.rpeDescription}>Moderado</Text>
        </View>
        <View style={styles.rpeItem}>
          <Text style={styles.rpeValue}>7-8</Text>
          <Text style={styles.rpeDescription}>Difícil</Text>
        </View>
        <View style={styles.rpeItem}>
          <Text style={styles.rpeValue}>9-10</Text>
          <Text style={styles.rpeDescription}>Máximo esfuerzo</Text>
        </View>
      </View>

      <Text style={styles.helpSubtitle}>Ejemplos de uso:</Text>
      <Text style={styles.helpNote}>• RPE 8 = Podrías hacer 2-3 reps más</Text>
      <Text style={styles.helpNote}>• RPE 9 = Podrías hacer 1 rep más</Text>
      <Text style={styles.helpNote}>• RPE 10 = Máximo esfuerzo, fallo muscular</Text>
      
      <Text style={styles.helpNote}>
        <Text style={styles.bold}>Tip:</Text> Puedes usar decimales como 7.5, 8.5, etc.
      </Text>
    </ScrollView>
  );

  const isValid = type === 'tempo' ? validateTempo(value) : validateRPE(value);
  const icon = isValid ? 'checkmark-circle' : 'alert-circle';
  const iconColor = isValid ? COLORS.success : COLORS.error;

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.helpButton}
        onPress={() => setShowModal(true)}
      >
        <Ionicons name="help-circle-outline" size={16} color={COLORS.textMedium} />
      </TouchableOpacity>
      
      <Ionicons name={icon} size={16} color={iconColor} style={styles.validationIcon} />
      
      {value && (
        <Text style={styles.validationText}>
          {type === 'tempo' ? formatTempo(value) : getRPEDescription(value)}
        </Text>
      )}

      <Modal
        visible={showModal}
        animationType="slide"
        transparent
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContainer}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {type === 'tempo' ? 'Ayuda - Tempo' : 'Ayuda - RPE'}
              </Text>
              <TouchableOpacity onPress={() => setShowModal(false)}>
                <Ionicons name="close" size={24} color={COLORS.textMedium} />
              </TouchableOpacity>
            </View>
            
            {type === 'tempo' ? renderTempoHelp() : renderRPEHelp()}
            
            <TouchableOpacity
              style={styles.closeButton}
              onPress={() => setShowModal(false)}
            >
              <Text style={styles.closeButtonText}>Cerrar</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: SPACING.xs,
  },
  helpButton: {
    padding: SPACING.xs,
  },
  validationIcon: {
    marginLeft: SPACING.xs,
  },
  validationText: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
    marginLeft: SPACING.xs,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    backgroundColor: COLORS.background,
    borderRadius: BORDER_RADIUS.lg,
    margin: SPACING.lg,
    maxHeight: '80%',
    width: '90%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
  },
  modalTitle: {
    fontSize: FONT_SIZE.lg,
    fontWeight: '600',
    color: COLORS.textPrimary,
  },
  helpContent: {
    padding: SPACING.md,
  },
  helpTitle: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: SPACING.sm,
  },
  helpSubtitle: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginTop: SPACING.md,
    marginBottom: SPACING.sm,
  },
  helpDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    marginBottom: SPACING.md,
    lineHeight: 20,
  },
  helpNote: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
    marginBottom: SPACING.xs,
    lineHeight: 16,
  },
  bold: {
    fontWeight: '600',
    color: COLORS.textPrimary,
  },
  tempoExplanation: {
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    marginBottom: SPACING.md,
  },
  tempoItem: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    marginBottom: SPACING.xs,
    lineHeight: 18,
  },
  exampleItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.xs,
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.sm,
    borderRadius: BORDER_RADIUS.sm,
  },
  exampleTempo: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.primary,
    width: 60,
  },
  exampleDescription: {
    fontSize: FONT_SIZE.xs,
    color: COLORS.textMedium,
    flex: 1,
  },
  rpeScale: {
    backgroundColor: COLORS.backgroundSecondary,
    padding: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    marginBottom: SPACING.md,
  },
  rpeItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: SPACING.xs,
  },
  rpeValue: {
    fontSize: FONT_SIZE.sm,
    fontWeight: '600',
    color: COLORS.primary,
    width: 40,
  },
  rpeDescription: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    flex: 1,
  },
  closeButton: {
    backgroundColor: COLORS.primary,
    padding: SPACING.md,
    margin: SPACING.md,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
  },
  closeButtonText: {
    color: COLORS.white,
    fontSize: FONT_SIZE.md,
    fontWeight: '500',
  },
});

export default ValidationHelper;
