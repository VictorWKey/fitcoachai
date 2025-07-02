import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { Platform } from 'react-native';
import { COLORS } from '../constants/theme';

/**
 * Componente para gestionar la StatusBar en toda la aplicación
 * Se debe incluir en el layout principal
 */
const StatusBarManager = () => {
  return (
    <StatusBar
      style="light"
      backgroundColor={Platform.OS === 'android' ? COLORS.background : 'transparent'}
      translucent={true}
    />
  );
};

export default StatusBarManager; 