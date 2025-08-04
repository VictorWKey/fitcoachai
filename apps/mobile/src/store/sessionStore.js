import { create } from 'zustand';

/**
 * Store global para manejar el estado de sesiones activas
 */
export const useSessionStore = create((set, get) => ({
  // Estado
  activeSession: null,
  isLoading: false,
  error: null,

  // Acciones
  setActiveSession: (session) => {
    console.log('=== STORE: Setting active session ===', session ? `ID: ${session.id}` : 'NULL');
    set({ activeSession: session, error: null });
  },

  clearActiveSession: () => {
    console.log('=== STORE: Clearing active session ===');
    set({ activeSession: null, error: null });
  },

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  clearError: () => set({ error: null }),
}));
