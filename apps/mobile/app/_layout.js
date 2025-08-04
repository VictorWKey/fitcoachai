import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { useAuthStore } from '../src/store/authStore';
import { authService } from '../src/services/apiService';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { ActiveSessionProvider } from '../src/contexts/ActiveSessionContext';
import { COLORS, SHADOWS } from '../src/constants/theme';

export default function RootLayout() {
  const router = useRouter();
  const { isAuthenticated, setIsAuthenticated } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const authenticated = await authService.isAuthenticated();
        setIsAuthenticated(authenticated);
      } catch (error) {
        console.error('Error al verificar autenticación:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [setIsAuthenticated, router]);

  // Redirigir basado en el estado de autenticación
  useEffect(() => {
    if (isLoading) return;

    if (isAuthenticated) {
      router.replace('/(app)');
    } else {
      router.replace('/'); // el index muestra LoginScreen
    }
  }, [isAuthenticated, isLoading, router]);

  // Mostrar pantalla de carga mientras se verifica la autenticación
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={styles.loadingText}>Cargando aplicación...</Text>
      </View>
    );
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <ActiveSessionProvider>
        <Stack screenOptions={{
          headerStyle: {
            backgroundColor: COLORS.primary,
            ...SHADOWS.medium,
          },
          headerTintColor: COLORS.background,
          headerTitleStyle: {
            fontWeight: 'bold',
          },
          headerTitleAlign: 'center',
        }}>
          <Stack.Screen
            name="index"
            redirect={isAuthenticated}
            options={{ headerShown: false }}
          />
          <Stack.Screen
            name="register"
            options={{ headerShown: false }}
          />
          <Stack.Screen
            name="forgot-password"
            options={{ title: 'Recuperar Contraseña' }}
          />
          <Stack.Screen
            name="(app)"
            redirect={!isAuthenticated}
            options={{ headerShown: false }}
          />
        </Stack>
      </ActiveSessionProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: COLORS.background,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: COLORS.textMedium,
  },
}); 