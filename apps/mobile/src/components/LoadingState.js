import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';
import { COLORS, FONT_SIZE, SPACING } from '../constants/theme';
import { TRANSLATIONS } from '../types/api';

const LoadingState = ({ 
  message = TRANSLATIONS.es.common.loading,
  size = 'large',
  color = COLORS.primary,
  overlay = false,
  style
}) => {
  const containerStyle = overlay ? styles.overlay : styles.container;

  return (
    <View style={[containerStyle, style]}>
      <ActivityIndicator size={size} color={color} />
      {message && (
        <Text style={styles.message}>{message}</Text>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
    padding: SPACING.lg,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 999,
  },
  message: {
    marginTop: SPACING.md,
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    textAlign: 'center',
  },
});

export default LoadingState;
