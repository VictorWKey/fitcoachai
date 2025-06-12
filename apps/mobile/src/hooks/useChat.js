import { useEffect, useRef } from 'react';
import { Alert } from 'react-native';
import { useChatStore } from '../store/chatStore';
import { useAuthStore } from '../store/authStore';

/**
 * Hook personalizado para manejar el chat
 * @returns {Object} Funciones y estado del chat
 */
export const useChat = () => {
  const { 
    messages, 
    isLoading, 
    error, 
    sendMessage: storeSendMessage, 
    clearError,
    fetchHistory
  } = useChatStore();
  
  const { logout } = useAuthStore();
  const flatListRef = useRef(null);

  useEffect(() => {
    fetchHistory();          // carga inicial
  }, []);                    // ← sin intervalo

  // Limpiar errores cuando el componente se desmonta
  useEffect(() => {
    return () => {
      if (error) clearError();
    };
  }, [error, clearError]);

  // Efecto para errores de autenticación
  useEffect(() => {
    if (String(error).includes('401')) {
      Alert.alert(
        'Sesión expirada',
        'Tu sesión ha expirado. Por favor, inicia sesión de nuevo.',
        [
          { text: 'OK', onPress: async () => {
            await logout();
          }}
        ]
      );
    }
  }, [error, logout]);

  // Scroll al final cuando se envía un nuevo mensaje
  useEffect(() => {
    if (messages.length > 0 && flatListRef.current) {
      setTimeout(() => {
        flatListRef.current.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  /**
   * Enviar mensaje al chat
   * @param {string} content - Contenido del mensaje
   * @returns {Promise<void>}
   */
  const handleSendMessage = async (content) => {
    if (!content.trim() || isLoading) return;
    
    try {
      await storeSendMessage(content);
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      // El error ya se maneja en el store
    }
  };

  return {
    messages,
    isLoading,
    error,
    handleSendMessage,
    clearError,
    flatListRef
  };
}; 