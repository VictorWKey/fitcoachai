import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { TouchableOpacity } from 'react-native-gesture-handler';
import { useAuth } from '../hooks/useAuth';
import { useRouter } from 'expo-router';

const ProfileScreen = () => {
  const router = useRouter();
  const { handleLogout } = useAuth();

  const handleSubmit = async () => {
    try {
      await handleLogout();
      // Cerrar todas las pantallas y volver a la ruta raíz de expo-router
      router.replace('/');
    } catch (e) {
      console.error('Error al cerrar sesión', e);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Perfil</Text>
      {/* Aquí puedes mostrar info del usuario */}
      <TouchableOpacity style={styles.button} onPress={handleSubmit}>
        <Text style={styles.buttonText}>Cerrar Sesión</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 20,
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 10,
  },
  buttonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default ProfileScreen;
