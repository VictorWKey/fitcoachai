import React, { useState } from 'react';
import {
  View,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  Text,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  Dimensions,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useAuth } from '../hooks/useAuth';
import { COLORS, FONT_SIZE, SPACING, BORDER_RADIUS, SHADOWS, COMMON_STYLES } from '../constants/theme';
import { FontAwesome5 } from '@expo/vector-icons';

const screenWidth = Dimensions.get('window').width;

const LoginScreen = () => {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { handleLogin, isLoading, error } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [formError, setFormError] = useState('');

  const handleSubmit = async () => {
    if (!username.trim() || !password.trim()) {
      setFormError('Completa usuario y contraseña');
      return;
    }
    setFormError('');
    try {
      const response = await handleLogin(username, password);
      if (response) {
        router.replace('/');
      }
    } catch (e) {
      console.error(e);
      Alert.alert('Error', 'Credenciales inválidas');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        style={styles.inner}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.logoContainer}>
          <FontAwesome5 name="dumbbell" size={56} color={COLORS.primary} />
          <Text style={styles.logoText}>FitCoach AI</Text>
        </View>

        <Text style={styles.title}>Bienvenido</Text>
        <Text style={styles.subtitle}>Inicia sesión para continuar</Text>

        <View style={styles.form}>
          <Text style={styles.label}>Usuario</Text>
          <TextInput
            style={styles.input}
            placeholder="Ingresa tu usuario"
            placeholderTextColor={COLORS.textLight}
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            keyboardType="email-address"
          />

          <Text style={styles.label}>Contraseña</Text>
          <TextInput
            style={styles.input}
            placeholder="Ingresa tu contraseña"
            placeholderTextColor={COLORS.textLight}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          {formError ? <Text style={styles.error}>{formError}</Text> : null}
          {error ? <Text style={styles.error}>{error}</Text> : null}

          <TouchableOpacity
            style={[styles.button, isLoading && styles.buttonDisabled]}
            onPress={handleSubmit}
            disabled={isLoading}
            activeOpacity={0.9}
          >
            {isLoading ? (
              <ActivityIndicator color={COLORS.background} />
            ) : (
              <Text style={styles.buttonText}>Iniciar sesión</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity onPress={() => router.push('/register')}>
            <Text style={styles.link}>¿No tienes cuenta? Crear una</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={() => router.push('/forgot-password')}>
            <Text style={styles.link}>¿Olvidaste tu contraseña?</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  inner: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: SPACING.xxxl,
    paddingHorizontal: SPACING.md,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: SPACING.lg,
  },
  logoText: {
    marginTop: SPACING.sm,
    fontSize: FONT_SIZE.xl + 2,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  title: {
    fontSize: FONT_SIZE.xxxl + 2,
    fontWeight: '700',
    color: COLORS.textDark,
    textAlign: 'center',
    marginBottom: SPACING.xs,
  },
  subtitle: {
    fontSize: FONT_SIZE.lg,
    color: COLORS.textMedium,
    textAlign: 'center',
    marginBottom: SPACING.xxl,
  },
  form: {
    width: '90%',
    maxWidth: 400,
    alignSelf: 'center',
  },
  label: {
    fontSize: FONT_SIZE.sm,
    color: COLORS.textMedium,
    marginBottom: SPACING.xs,
    marginLeft: SPACING.xs,
  },
  input: {
    backgroundColor: COLORS.input,
    borderRadius: BORDER_RADIUS.lg,
    paddingVertical: SPACING.lg,
    paddingHorizontal: SPACING.xl,
    fontSize: FONT_SIZE.md,
    color: COLORS.textDark,
    marginBottom: SPACING.xl,
    ...SHADOWS.light,
    borderWidth: 1,
    borderColor: COLORS.card,
  },
  button: {
    ...COMMON_STYLES.buttonPrimary,
    paddingVertical: SPACING.lg + 2,
    borderRadius: BORDER_RADIUS.xl,
    marginTop: SPACING.md,
    marginBottom: SPACING.lg,
  },
  buttonDisabled: {
    backgroundColor: COLORS.primaryDark + '80',
  },
  buttonText: {
    color: COLORS.background,
    fontWeight: '700',
    fontSize: FONT_SIZE.md + 1,
  },
  link: {
    color: COLORS.primary,
    textAlign: 'center',
    fontSize: FONT_SIZE.md,
    marginTop: SPACING.md,
    fontWeight: '500',
  },
  error: {
    color: COLORS.error,
    textAlign: 'center',
    fontSize: FONT_SIZE.sm,
    marginBottom: SPACING.sm,
    marginTop: -SPACING.sm,
  },
});

export default LoginScreen;
