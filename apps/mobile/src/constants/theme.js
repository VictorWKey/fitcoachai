/**
 * Tema y constantes de estilo para la aplicación en modo oscuro
 */

// Colores
export const COLORS = {
  // Colores primarios
  primary: '#fbc736',
  primaryDark: '#e6b01f',
  primaryLight: '#ffd45e',

  // Colores secundarios
  secondary: '#8A2BE2',
  secondaryDark: '#6a1fb0',
  secondaryLight: '#a555e9',

  // Colores de texto
  textDark: '#f0f0f0',
  textMedium: '#c0c0c0',
  textLight: '#909090',

  // Colores de fondo
  background: '#121212',
  card: '#1e1e1e',
  input: '#2a2a2a',

  // Colores de estado
  success: '#4CAF50',
  error: '#FF5252',
  warning: '#FFC107',
  info: '#29B6F6',

  // Colores para chat
  userBubble: '#fbc736',
  userText: '#121212',
  aiBubble: '#2a2a2a',
  aiText: '#f0f0f0',
};

// Tamaños de fuente
export const FONT_SIZE = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  xxl: 24,
  xxxl: 32,
};

// Espaciado
export const SPACING = {
  xs: 5,
  sm: 10,
  md: 15,
  lg: 20,
  xl: 25,
  xxl: 30,
  xxxl: 40,
};

// Bordes
export const BORDER_RADIUS = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  xxl: 25,
  circle: 50,
};

// Sombras
export const SHADOWS = {
  light: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  medium: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
    elevation: 6,
  },
  dark: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.4,
    shadowRadius: 15,
    elevation: 10,
  },
  glow: {
    shadowColor: COLORS.primary,
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
    elevation: 8,
  }
};

// Estilos comunes
export const COMMON_STYLES = {
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: BORDER_RADIUS.lg,
    padding: SPACING.lg,
    ...SHADOWS.medium,
  },
  title: {
    fontSize: FONT_SIZE.xxl,
    fontWeight: 'bold',
    color: COLORS.textDark,
    marginBottom: SPACING.md,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: FONT_SIZE.lg,
    color: COLORS.textMedium,
    marginBottom: SPACING.md,
    textAlign: 'center',
  },
  buttonPrimary: {
    backgroundColor: COLORS.primary,
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.lg,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    justifyContent: 'center',
    ...SHADOWS.glow,
  },
  buttonSecondary: {
    backgroundColor: 'transparent',
    paddingVertical: SPACING.md,
    paddingHorizontal: SPACING.lg,
    borderRadius: BORDER_RADIUS.md,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: COLORS.primary,
  },
  buttonText: {
    color: COLORS.background,
    fontWeight: '700',
    fontSize: FONT_SIZE.md,
  },
  buttonTextSecondary: {
    color: COLORS.primary,
    fontWeight: '600',
    fontSize: FONT_SIZE.md,
  },
}; 