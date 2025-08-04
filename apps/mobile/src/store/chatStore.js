import { create } from 'zustand';
import { chatService } from '../services/apiService';
import { registerReset } from './storeRegistry';

export const useChatStore = create((set, get) => ({
  // Estado
  messages: [],
  lastId: 0,
  tempIdCounter: 0, // Contador para IDs temporales
  isLoading: false,
  error: null,

  // Acciones
  setMessages: (messages) => set({ messages }),
  appendMessages: (newMessages) => set(state => ({
    messages: [...state.messages, ...newMessages]
  })),

  clearMessages: () => set({ messages: [], lastId: 0, tempIdCounter: 0 }),

  clearError: () => set({ error: null }),

  // Generar ID temporal único
  generateTempId: () => {
    const state = get();
    const tempId = `temp_${Date.now()}_${state.tempIdCounter}`;
    set({ tempIdCounter: state.tempIdCounter + 1 });
    return tempId;
  },

  // Enviar un mensaje al chat
  sendMessage: async (content) => {
    // No hacer nada si está cargando
    if (get().isLoading) return;

    // Añadir mensaje del usuario a la lista con ID temporal
    const userMessage = {
      id: get().generateTempId(),
      role: 'user',
      content
    };
    set(state => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      error: null
    }));

    try {
      // Enviar mensaje al backend
      const assistantMsg = await chatService.sendMessage(content);
      // Append assistant message
      set(state => ({
        messages: [...state.messages, assistantMsg],
        isLoading: false,
        lastId: assistantMsg.id || state.lastId
      }));

      return assistantMsg;
    } catch (error) {
      console.error('Error al enviar mensaje:', error);

      // Añadir mensaje de error como mensaje del asistente con ID temporal
      const errorMessage = {
        id: get().generateTempId(),
        role: 'assistant',
        content: 'Lo siento, ha ocurrido un error. Por favor, inténtalo de nuevo más tarde.'
      };

      set(state => ({
        messages: [...state.messages, errorMessage],
        isLoading: false,
        error: 'Error al enviar mensaje. Inténtalo de nuevo.'
      }));

      throw error;
    }
  },

  // Cargar historial (inicial o incremental)
  fetchHistory: async () => {
    const afterId = get().lastId || 0;
    try {
      const history = await chatService.getHistory(afterId);
      if (history.length) {
        // ordenar por id asc para mantener cronología
        history.sort((a, b) => a.id - b.id);
        set(state => ({
          messages: afterId === 0 ? history : [...state.messages, ...history],
          lastId: history[history.length - 1].id
        }));
      }
    } catch (e) {
      console.error('Error fetching history', e);
    }
  },

  // Reset internal similar to authStore
  reset: () => set({
    messages: [],
    lastId: 0,
    tempIdCounter: 0,
    isLoading: false,
    error: null,
  })
}));

// Registrar reset de forma uniforme
registerReset(useChatStore.getState().reset);

export const { fetchHistory } = useChatStore;