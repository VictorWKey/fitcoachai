import React from 'react';
import { TouchableOpacity, StyleSheet, Animated, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useSessionStore } from '../store/sessionStore';
import { COLORS } from '../constants/theme';

const ActiveSessionIndicator = () => {
  const router = useRouter();
  const { activeSession } = useSessionStore();
  
  // Animación de pulso para el indicador
  const pulseAnim = React.useRef(new Animated.Value(1)).current;
  
  // Iniciar animación de pulso cuando el componente se monta
  React.useEffect(() => {
    if (activeSession) {
      startPulseAnimation();
    }
  }, [activeSession]);
  
  // Iniciar animación de pulso
  const startPulseAnimation = () => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(pulseAnim, {
          toValue: 1.3,
          duration: 1000,
          useNativeDriver: true,
        }),
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        }),
      ])
    ).start();
  };
  
  // Navegar a la sesión activa
  const handlePress = () => {
    if (activeSession) {
      // Navegar a la sesión usando push para preservar el historial de navegación
      router.push({
        pathname: '/session-exercises',
        params: { 
          programId: activeSession.programId || '1',
          sessionId: activeSession.id.toString(),
          sessionName: activeSession.name
        }
      });
    }
  };
  
  // Si no hay sesión activa, no renderizar nada
  if (!activeSession) {
    return null;
  }
  
  return (
    <TouchableOpacity
      style={styles.container}
      onPress={handlePress}
      activeOpacity={0.7}
    >
      <View style={styles.iconWrapper}>
        <Animated.View 
          style={[
            styles.indicator,
            { transform: [{ scale: pulseAnim }] }
          ]} 
        />
        <Ionicons name="fitness-outline" size={20} color={COLORS.background} />
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    marginRight: 10,
    marginLeft: 5,
  },
  iconWrapper: {
    position: 'relative',
    width: 28,
    height: 28,
    justifyContent: 'center',
    alignItems: 'center',
  },
  indicator: {
    position: 'absolute',
    top: 0,
    right: 0,
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: COLORS.success,
    borderWidth: 1,
    borderColor: COLORS.primary,
  }
});

export default ActiveSessionIndicator;
