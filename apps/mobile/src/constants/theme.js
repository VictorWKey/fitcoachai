/**
 * Tema y constantes de estilo para la aplicación
 */

// Colores
export const COLORS = {
  // Colores primarios
  primary: '#007AFF',
  primaryDark: '#0062cc',
  primaryLight: '#e6f2ff',
  
  // Colores secundarios
  secondary: '#FF9500',
  secondaryDark: '#cc7700',
  secondaryLight: '#fff5e6',
  
  // Colores de texto
  textDark: '#333',
  textMedium: '#666',
  textLight: '#999',
  
  // Colores de fondo
  background: '#f8f9fa',
  card: '#fff',
  input: '#f5f7fa',
  
  // Colores de estado
  success: '#34C759',
  error: '#FF3B30',
  warning: '#FFCC00',
  info: '#5AC8FA',
  
  // Colores para chat
  userBubble: '#007AFF',
  userText: '#fff',
  aiBubble: '#e6e6e6',
  aiText: '#333',
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
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  medium: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 5,
  },
  dark: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 15,
    elevation: 8,
  },
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
}; 