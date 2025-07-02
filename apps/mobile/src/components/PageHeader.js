import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS } from '../constants/theme';

/**
 * Componente de header reutilizable para todas las pantallas
 * @param {string} title - Título del header
 */
const PageHeader = ({ title }) => {
  return (
    <View style={styles.header}>
      <Text style={styles.headerTitle}>{title}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  header: {
    backgroundColor: COLORS.primary,
    borderBottomLeftRadius: BORDER_RADIUS.lg,
    borderBottomRightRadius: BORDER_RADIUS.lg,
    paddingVertical: SPACING.md,
    marginTop: -1, // Elimina el espacio negro superior
  },
  headerTitle: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.userText,
    textAlign: 'center',
  },
});

export default PageHeader; 