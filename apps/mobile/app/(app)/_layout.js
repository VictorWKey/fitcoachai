import React from 'react';
import { Pressable } from 'react-native';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { authService } from '../../src/services/apiService';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../src/store/authStore';

// Componente para el botón de cierre de sesión
const LogoutButton = () => {
  const router = useRouter();
  const { setIsAuthenticated } = useAuthStore();

  const handleLogout = async () => {
    try {
      await authService.logout();
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
      <Ionicons name="log-out-outline" size={24} color="#fff" />
    </Pressable>
  );
};

export default function AppLayout() {
  return (
    <Tabs
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'index') {
            iconName = focused ? 'chatbubble' : 'chatbubble-outline';
          } else if (route.name === 'workouts') {
            iconName = focused ? 'barbell' : 'barbell-outline';
          } else if (route.name === 'profile') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          paddingBottom: 5,
          height: 60
        },
        headerStyle: {
          backgroundColor: '#007AFF',
          elevation: 0,
          shadowOpacity: 0,
        },
        headerTintColor: '#fff',
        headerTitleStyle: {
          fontWeight: 'bold',
        },
        headerTitleAlign: 'center',
      })}
    >
      <Tabs.Screen 
        name="index" 
        options={{ 
          title: 'FitCoach AI'
        }}
      />
      <Tabs.Screen 
        name="workouts" 
        options={{ 
          title: 'Entrenamientos'
        }}
      />
      <Tabs.Screen 
        name="profile" 
        options={{ 
          title: 'Perfil'
        }}
      />
    </Tabs>
  );
} 