import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Alert,
  Dimensions,
  Easing,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter, usePathname } from 'expo-router';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useSessions } from '../hooks/useSessions';
import { useSessionStore } from '../store/sessionStore';
import { useActiveSession } from '../contexts/ActiveSessionContext';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS } from '../constants/theme';

const ActiveSessionOverlay = () => {
  const router = useRouter();
  const pathname = usePathname();
  const insets = useSafeAreaInsets();
  const { 
    finishSession, 
    getActiveSession, 
    sendHeartbeat,
    checkSessionStatus, 
    pauseSession, 
    resumeSession, 
    abandonSession 
  } = useSessions();
  
  // Use global session store and active session context
  const { activeSession } = useSessionStore();
  const { viewingActiveSession } = useActiveSession();
  
  // Detectar contexto de pantallas para posicionar el botón correctamente
  const [currentScreen, setCurrentScreen] = useState('default');
  
  // Determinar si necesitamos un posicionamiento especial
  const needsSpecialPosition = currentScreen === 'chat' || currentScreen === 'input-heavy';
  
  // Animation refs
  const toastAnim = useRef(new Animated.Value(-150)).current;
  const fabAnim = useRef(new Animated.Value(100)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  
  // Component state
  const [isToastVisible, setIsToastVisible] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [isFabActive, setIsFabActive] = useState(false); // Para control de opacidad
  const timeoutRef = useRef(null);
  const fadeTimeoutRef = useRef(null);
  
  // Check for active session on mount
  useEffect(() => {
    checkActiveSession();
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (fadeTimeoutRef.current) clearTimeout(fadeTimeoutRef.current);
    };
  }, []);
  
  // Detectar la pantalla actual para ajustar la posición
  useEffect(() => {
    try {
      // Obtener información de la ruta actual
      const currentPath = pathname || '';
      
      // Identificar pantallas específicas
      if (currentPath.includes('chat')) {
        setCurrentScreen('chat');
      } else if (currentPath.includes('profile')) {
        setCurrentScreen('profile');
      } else {
        setCurrentScreen('default');
      }
      
      console.log('OVERLAY: Current screen detected:', currentPath);
    } catch (err) {
      console.log('OVERLAY: Error detecting screen', err);
      setCurrentScreen('default');
    }
  }, [pathname]);
  
  // Watch for active session changes
  useEffect(() => {
    console.log('OVERLAY: useEffect triggered', {
      hasActiveSession: !!activeSession,
      activeSessionId: activeSession?.id,
      viewingActiveSession,
      isToastVisible,
      isMinimized,
      pathname
    });

    if (activeSession && !viewingActiveSession) {
      // Solo mostrar el overlay si hay sesión activa Y NO estamos viéndola
      setCurrentSession(activeSession);
      
      if (!isToastVisible && !isMinimized) {
        console.log('OVERLAY: Showing toast notification for active session');
        showToast();
      }
    } else {
      // Ocultar overlay si no hay sesión activa O si estamos viendo la sesión activa
      if (isToastVisible || isMinimized) {
        console.log('OVERLAY: Hiding overlay - no session OR viewing active session');
        hideAll();
      }
    }
  }, [activeSession, viewingActiveSession]);
  
  // Initial active session check
  const checkActiveSession = async () => {
    try {
      // Usar el nuevo endpoint de status en lugar de active
      const statusResponse = await checkSessionStatus();
      console.log('Initial check session status:', statusResponse ? 'RECEIVED' : 'FAILED');
      
      if (statusResponse && statusResponse.has_active_session) {
        const session = statusResponse.session;
        
        // Verificar si la sesión está auto-pausada
        if (session.status === 'auto_paused') {
          showResumeDialog(session);
        }
        
        if (!isToastVisible && !isMinimized) {
          // If we already have a session on mount, show minimized FAB directly
          setCurrentSession(session);
          showMinimizedFab();
        }
      }
    } catch (error) {
      console.log('Error checking session status on mount:', error);
    }
  };
  
  // Mostrar diálogo cuando la sesión está auto-pausada
  const showResumeDialog = (session) => {
    Alert.alert(
      "Sesión Pausada",
      "Tu entrenamiento fue pausado automáticamente por inactividad",
      [
        {
          text: "Continuar",
          onPress: async () => {
            try {
              await resumeSession();
              // Actualizar la UI después de reanudar
              setCurrentSession({...session, status: 'active'});
            } catch (error) {
              console.error('Error resuming session:', error);
            }
          }
        },
        {
          text: "Finalizar",
          onPress: async () => {
            try {
              await finishSession();
              hideAll();
            } catch (error) {
              console.error('Error finishing session:', error);
            }
          }
        },
        {
          text: "Abandonar",
          onPress: async () => {
            try {
              await abandonSession();
              hideAll();
            } catch (error) {
              console.error('Error abandoning session:', error);
            }
          }
        }
      ]
    );
  };
  
  // Animation to show toast notification
  const showToast = () => {
    setIsToastVisible(true);
    setIsMinimized(false);
    
    // Show toast
    Animated.spring(toastAnim, {
      toValue: 0,
      useNativeDriver: true,
      tension: 80,
      friction: 7,
    }).start();
    
    // Fade in
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
    
    // Start pulse animation for active indicator
    startPulseAnimation();
    
    // Auto-minimize after delay
    timeoutRef.current = setTimeout(() => {
      minimizeToFab();
    }, 5000);
  };
  
  // Start pulsing animation for activity indicator
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
  
  // Minimize toast to FAB
  const minimizeToFab = () => {
    // Hide toast
    Animated.spring(toastAnim, {
      toValue: -150,
      useNativeDriver: true,
      tension: 80,
      friction: 7,
    }).start(() => {
      setIsToastVisible(false);
    });
    
    // Show FAB
    showMinimizedFab();
  };
  
  // Show minimized FAB
  const showMinimizedFab = () => {
    setIsMinimized(true);
    setIsFabActive(true); // Mostrar completamente visible al inicio
    
    // Show FAB
    Animated.spring(fabAnim, {
      toValue: 0,
      useNativeDriver: true,
      tension: 80,
      friction: 7,
    }).start();
    
    // Fade in
    Animated.timing(fadeAnim, {
      toValue: 1,
      duration: 300,
      useNativeDriver: true,
    }).start();
    
    // Start pulse for FAB indicator
    startPulseAnimation();
    
    // Después de 3 segundos, reducir la opacidad
    clearTimeout(fadeTimeoutRef.current);
    fadeTimeoutRef.current = setTimeout(() => {
      setIsFabActive(false);
    }, 3000);
  };
  
  // Expand FAB to toast
  const expandToToast = () => {
    // Set active and clear timeout
    setIsFabActive(true);
    clearTimeout(fadeTimeoutRef.current);
    
    // Hide FAB
    Animated.spring(fabAnim, {
      toValue: 100,
      useNativeDriver: true,
      tension: 80,
      friction: 7,
    }).start(() => {
      setIsMinimized(false);
    });
    
    // Show toast
    showToast();
  };
  
  // Hide all UI elements
  const hideAll = () => {
    // Clear auto-minimize timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    
    if (fadeTimeoutRef.current) {
      clearTimeout(fadeTimeoutRef.current);
      fadeTimeoutRef.current = null;
    }
    
    // Fade out everything
    Animated.timing(fadeAnim, {
      toValue: 0,
      duration: 200,
      useNativeDriver: true,
    }).start();
    
    // Hide toast if visible
    if (isToastVisible) {
      Animated.spring(toastAnim, {
        toValue: -150,
        useNativeDriver: true,
        tension: 80,
        friction: 7,
      }).start();
    }
    
    // Hide FAB if visible
    if (isMinimized) {
      Animated.spring(fabAnim, {
        toValue: 100,
        useNativeDriver: true,
        tension: 80,
        friction: 7,
      }).start();
    }
    
    // Reset state after animations
    setTimeout(() => {
      setIsToastVisible(false);
      setIsMinimized(false);
      setCurrentSession(null);
    }, 300);
  };
  
  // Navigate to session details
  const handleGoToSession = async () => {
    // Clear auto-minimize timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    
    if (currentSession) {
      // Enviar heartbeat para actualizar actividad
      try {
        await sendHeartbeat();
        console.log('Heartbeat sent before navigation');
      } catch (err) {
        console.error('Error sending heartbeat:', err);
      }
      
      router.push({
        pathname: '/session-exercises',
        params: { 
          programId: currentSession.programId || '1',
          sessionId: currentSession.id.toString(),
          sessionName: currentSession.name
        }
      });
      
      // Auto-minimize after navigation
      if (isToastVisible) {
        minimizeToFab();
      }
    }
  };
  
  // Show confirmation dialog to finish session
  const handleFinishSession = () => {
    Alert.alert(
      'Finalizar Entrenamiento',
      '¿Estás seguro de que quieres finalizar tu entrenamiento actual?',
      [
        { text: 'Cancelar', style: 'cancel' },
        {
          text: 'Finalizar',
          style: 'destructive',
          onPress: async () => {
            try {
              // Usando el endpoint actualizado de finalización
              await finishSession();
              
              // Verification will happen through global state changes
              Alert.alert('¡Entrenamiento finalizado!', 'Tu sesión ha sido completada.');
            } catch (error) {
              Alert.alert('Error', 'No se pudo finalizar el entrenamiento');
            }
          },
        },
      ]
    );
  };
  
  // Format duration for display
  const formatDuration = (startTime) => {
    if (!startTime) return '00:00';
    
    const start = new Date(startTime);
    const now = new Date();
    const diff = Math.floor((now - start) / 1000); // seconds
    
    const hours = Math.floor(diff / 3600);
    const minutes = Math.floor((diff % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}h`;
    }
    return `${minutes}:${(diff % 60).toString().padStart(2, '0')}`;
  };
  
  // Don't render anything if no active session
  if (!currentSession) {
    return null;
  }
  
  // Calcular posición según la pantalla actual
  const getFabPosition = () => {
    // Posiciones base según tipo de pantalla
    if (currentScreen === 'chat') {
      return insets.bottom + 160; // Mucho más alto en pantalla de chat
    } else if (needsSpecialPosition) {
      return insets.bottom + 130; // Alto en pantallas con inputs
    } else {
      return insets.bottom + 80; // Posición estándar
    }
  };
  
  return (
    <>
      {/* Toast notification */}
      {currentSession && (
        <Animated.View 
          style={[
            styles.toastContainer,
            {
              transform: [{ translateY: toastAnim }],
              opacity: fadeAnim,
              top: insets.top + 10,
            }
          ]}
        >
          <TouchableOpacity 
            style={styles.toastContent}
            onPress={handleGoToSession}
            activeOpacity={0.8}
          >
            <View style={styles.indicatorContainer}>
              <Animated.View 
                style={[
                  styles.pulsingDot,
                  { transform: [{ scale: pulseAnim }] }
                ]} 
              />
            </View>
            
            <View style={styles.sessionDetails}>
              <Text style={styles.sessionTitle} numberOfLines={1}>
                {currentSession.name}
              </Text>
              <Text style={styles.sessionTime}>
                {formatDuration(currentSession.startTime)}
              </Text>
            </View>
            
            <View style={styles.sessionActions}>
              <TouchableOpacity 
                style={styles.actionButton}
                onPress={minimizeToFab}
              >
                <Ionicons name="chevron-up" size={16} color={COLORS.background} />
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.actionButton, styles.finishButton]}
                onPress={handleFinishSession}
              >
                <Ionicons name="checkmark" size={16} color={COLORS.background} />
              </TouchableOpacity>
            </View>
          </TouchableOpacity>
        </Animated.View>
      )}
      
      {/* Minimized FAB - Ajusta su posición según el contexto */}
      {currentSession && (
        <Animated.View 
          style={[
            styles.fabContainer,
            {
              transform: [{ translateY: fabAnim }],
              opacity: isFabActive ? fadeAnim : fadeAnim.interpolate({
                inputRange: [0, 1],
                outputRange: [0, 0.6], // Opacidad reducida cuando no está activo
              }),
              bottom: getFabPosition(), // Usar función para calcular posición
              right: SPACING.md,
            }
          ]}
        >
          <TouchableOpacity 
            style={styles.fabCompact}
            onPress={expandToToast}
            onPressIn={() => setIsFabActive(true)} // Activar al tocar
            activeOpacity={0.8}
          >
            <Animated.View 
              style={[
                styles.fabIndicator,
                { transform: [{ scale: pulseAnim }] }
              ]} 
            />
          </TouchableOpacity>
        </Animated.View>
      )}
    </>
  );
};

const styles = StyleSheet.create({
  // Toast notification styles
  toastContainer: {
    position: 'absolute',
    left: SPACING.md,
    right: SPACING.md,
    backgroundColor: COLORS.primary,
    borderRadius: BORDER_RADIUS.md,
    ...SHADOWS.medium,
    zIndex: 1000,
    overflow: 'hidden',
  },
  toastContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: SPACING.sm,
  },
  indicatorContainer: {
    marginRight: SPACING.sm,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  pulsingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: COLORS.success,
  },
  sessionDetails: {
    flex: 1,
    marginRight: SPACING.sm,
  },
  sessionTitle: {
    fontSize: FONT_SIZE.md,
    fontWeight: '600',
    color: COLORS.background,
  },
  sessionTime: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.background,
    opacity: 0.8,
  },
  sessionActions: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionButton: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: SPACING.xs,
  },
  finishButton: {
    backgroundColor: COLORS.danger,
  },
  
  // FAB styles
  fabContainer: {
    position: 'absolute',
    backgroundColor: 'transparent',
    zIndex: 1000,
  },
  fabCompact: {
    width: 36, // Más pequeño para ser menos intrusivo
    height: 36, // Más pequeño para ser menos intrusivo
    borderRadius: 18,
    backgroundColor: COLORS.primary,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 0,
    // Agregar sombra más sutil
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 3,
      },
      android: {
        elevation: 4,
      },
    }),
  },
  fabIndicator: {
    width: 12, // Más grande para que sea visible por sí solo
    height: 12,
    borderRadius: 6,
    backgroundColor: COLORS.success,
  },
  fabText: {
    fontSize: FONT_SIZE.xs, // Texto más pequeño
    fontWeight: '600',
    color: COLORS.background,
    maxWidth: 100, // Limitar ancho máximo
  },
});

export default ActiveSessionOverlay;
