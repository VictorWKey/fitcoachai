import React from 'react';
import { Pressable, View } from 'react-native';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { authService } from '../../src/services/apiService';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../src/store/authStore';
import { resetAllStores } from '../../src/store/storeRegistry';
import { COLORS, SHADOWS } from '../../src/constants/theme';
import { ActiveSessionIndicator } from '../../src/components';

// Componente para el header derecho que incluye indicador de sesión y botón de cierre de sesión
const HeaderRight = () => {
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center' }}>
      <ActiveSessionIndicator />
      <LogoutButton />
    </View>
  );
};

// Componente para el botón de cierre de sesión
const LogoutButton = () => {
  const router = useRouter();
  const { setIsAuthenticated } = useAuthStore();

  const handleLogout = async () => {
    try {
      await authService.logout();
      resetAllStores(); // Limpiar todos los stores incluyendo sessionStore
      setIsAuthenticated(false);
      router.replace('/');
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    }
  };

  return (
    <Pressable
      style={({ pressed }) => [
        {
          marginRight: 15,
          opacity: pressed ? 0.7 : 1
        }
      ]}
      onPress={handleLogout}
      android_ripple={{ color: 'rgba(255,255,255,0.3)', radius: 20 }}
    >
      <Ionicons name="log-out-outline" size={24} color={COLORS.background} />
    </Pressable>
  );
};

export default function AppLayout() {
  const insets = useSafeAreaInsets();

  return (
    <View style={{ flex: 1 }}>
      <Tabs
        screenOptions={({ route }) => ({
          tabBarIcon: ({ focused, color, size }) => {
            let iconName;

          if (route.name === 'index') {
            iconName = focused ? 'chatbubble' : 'chatbubble-outline';
          } else if (route.name === 'training-programs') {
            iconName = focused ? 'calendar' : 'calendar-outline';
          } else if (route.name === 'profile') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.textMedium,
        tabBarStyle: {
          paddingBottom: insets.bottom,
          height: 60 + insets.bottom,
          backgroundColor: COLORS.card,
          borderTopColor: COLORS.card,
          ...SHADOWS.medium,
        },
        headerStyle: {
          backgroundColor: COLORS.primary,
          elevation: 4,
          shadowOpacity: 0.2,
          ...SHADOWS.medium,
        },
        headerTintColor: COLORS.background,
        headerTitleStyle: {
          fontWeight: 'bold',
        },
        headerTitleAlign: 'center',
      })}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'FitCoach AI',
          headerRight: () => <HeaderRight />
        }}
      />
      <Tabs.Screen
        name="training-programs"
        options={{
          title: 'Programas',
          headerRight: () => <HeaderRight />
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Perfil',
          headerRight: () => <HeaderRight />
        }}
      />
      <Tabs.Screen
        name="program-detail"
        options={{
          title: 'Detalles del Programa',
          href: null, // Oculta esta pantalla del tab bar
          headerShown: true, // Ahora mostramos el header para ver el indicador
          headerRight: () => <HeaderRight />
        }}
      />
      <Tabs.Screen
        name="program-sessions"
        options={{
          title: 'Sesiones del Programa',
          href: null, // Oculta esta pantalla del tab bar
          headerShown: true,
          headerRight: () => <HeaderRight />
        }}
      />
      <Tabs.Screen
        name="week-sessions"
        options={{
          title: 'Sesiones de la Semana',
          href: null, // Oculta esta pantalla del tab bar
          headerShown: true,
          headerRight: () => <HeaderRight />
        }}
      />
      <Tabs.Screen
        name="session-exercises"
        options={{
          title: 'Ejercicios de la Sesión',
          href: null, // Oculta esta pantalla del tab bar
          headerShown: true,
          headerRight: () => <HeaderRight />
        }}
      />
    </Tabs>
  </View>
  );
} 