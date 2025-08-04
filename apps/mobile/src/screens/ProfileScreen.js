import React from 'react';
import { View, Text, StyleSheet, SafeAreaView } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { TouchableOpacity } from 'react-native-gesture-handler';
import { useAuth } from '../hooks/useAuth';
import { useRouter } from 'expo-router';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS, COMMON_STYLES } from '../constants/theme';
import { FontAwesome5 } from '@expo/vector-icons';

const ProfileScreen = () => {
  const router = useRouter();
  const insets = useSafeAreaInsets();
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
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mi Perfil</Text>
      </View>

      <View style={styles.profileContainer}>
        <View style={styles.avatarContainer}>
          <FontAwesome5 name="user-circle" size={80} color={COLORS.primary} />
        </View>
        <Text style={styles.userName}>Usuario FitCoach</Text>
        <Text style={styles.userEmail}>usuario@example.com</Text>
      </View>

      <View style={styles.optionsContainer}>
        <TouchableOpacity style={styles.optionItem}>
          <FontAwesome5 name="cog" size={20} color={COLORS.primary} />
          <Text style={styles.optionText}>Configuración</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.optionItem}>
          <FontAwesome5 name="bell" size={20} color={COLORS.primary} />
          <Text style={styles.optionText}>Notificaciones</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.optionItem}>
          <FontAwesome5 name="question-circle" size={20} color={COLORS.primary} />
          <Text style={styles.optionText}>Ayuda</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity 
        style={[styles.logoutButton, { marginBottom: insets.bottom + SPACING.lg }]} 
        onPress={handleSubmit}
      >
        <FontAwesome5 name="sign-out-alt" size={20} color={COLORS.background} />
        <Text style={styles.logoutText}>Cerrar Sesión</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  header: {
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.lg,
    paddingHorizontal: SPACING.xl,
    borderBottomLeftRadius: BORDER_RADIUS.lg,
    borderBottomRightRadius: BORDER_RADIUS.lg,
    ...SHADOWS.medium,
  },
  headerTitle: {
    fontSize: FONT_SIZE.xl,
    fontWeight: 'bold',
    color: COLORS.background,
    textAlign: 'center',
  },
  profileContainer: {
    alignItems: 'center',
    paddingVertical: SPACING.xl,
  },
  avatarContainer: {
    marginBottom: SPACING.md,
  },
  userName: {
    fontSize: FONT_SIZE.lg,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginTop: SPACING.sm,
  },
  userEmail: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textMedium,
    marginTop: SPACING.xs,
  },
  optionsContainer: {
    paddingHorizontal: SPACING.xl,
    marginTop: SPACING.xl,
  },
  optionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: SPACING.md,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.card,
  },
  optionText: {
    fontSize: FONT_SIZE.md,
    color: COLORS.textDark,
    marginLeft: SPACING.md,
  },
  logoutButton: {
    ...COMMON_STYLES.buttonPrimary,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: SPACING.xl,
    marginTop: SPACING.xxl,
  },
  logoutText: {
    color: COLORS.background,
    fontWeight: 'bold',
    fontSize: FONT_SIZE.md,
    marginLeft: SPACING.sm,
  },
});

export default ProfileScreen;
