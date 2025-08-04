import React, { createContext, useContext, useState, useEffect } from 'react';
import { useSessions } from '../hooks/useSessions';
import { useSessionStore } from '../store/sessionStore';
import { AppState, Alert } from 'react-native';

const ActiveSessionContext = createContext();

export const ActiveSessionProvider = ({ children }) => {
  const { getActiveSession, resumeSession, finishSession, abandonSession, checkSessionStatus: checkSessionStatusFromHook } = useSessions();
  
  // USAR SOLO EL STORE - NO DUPLICAR ESTADO
  const { activeSession, setActiveSession, clearActiveSession } = useSessionStore();
  
  // Estados locales del contexto (NO relacionados con la sesión activa)
  const [programId, setProgramId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastChecked, setLastChecked] = useState(null);
  const [appState, setAppState] = useState(AppState.currentState);
  const [lastActiveTime, setLastActiveTime] = useState(Date.now());
  const [viewingActiveSession, setViewingActiveSession] = useState(false);
  
  useEffect(() => {
    // Verificar inmediatamente al inicializar
    checkActiveSession();
    
    // Configurar listeners para el estado de la app
    const handleAppStateChange = (nextAppState) => {
      if (appState === 'active' && nextAppState.match(/inactive|background/)) {
        // App va a background
        setLastActiveTime(Date.now());
      } else if (appState.match(/inactive|background/) && nextAppState === 'active') {
        // App vuelve a foreground
        const timeSinceLastActive = Date.now() - lastActiveTime;
        
        // Si pasaron más de 2 minutos, verificar estado
        if (timeSinceLastActive > 2 * 60 * 1000) {
          checkSessionStatusFromHook();
        }
      }
      
      setAppState(nextAppState);
    };
    
    const appStateSubscription = AppState.addEventListener('change', handleAppStateChange);
    
    return () => {
      appStateSubscription.remove();
    };
  }, [appState, lastActiveTime]);

  const checkActiveSession = async () => {
    try {
      console.log('🔄 Verificando sesión activa global...');
      setIsLoading(true);
      const session = await getActiveSession();
      // getActiveSession ya actualiza el store automáticamente, no necesitamos hacerlo aquí
      setLastChecked(new Date());
      
      console.log(`✅ Sesión activa global: ${session ? `ID ${session.id} - ${session.name}` : 'ninguna'}`);
    } catch (error) {
      console.error('❌ Error al obtener sesión activa:', error);
      
      // No cambiar el estado si es un error de token para evitar pérdida de sesión
      if (error.message && (error.message.includes('Token expirado') || error.message.includes('No refresh token'))) {
        console.log('Error temporal al obtener sesión activa, manteniendo estado actual');
      } else {
        // Para otros errores, sí limpiar el estado
        clearActiveSession();
      }
    } finally {
      setIsLoading(false);
    }
  };

  const updateSessionInfo = (sessionData, programIdValue = null) => {
    console.log(`🔄 Actualizando info de sesión: ${sessionData ? `ID ${sessionData.id}` : 'null'}`);
    setActiveSession(sessionData); // Usar directamente el store
    if (programIdValue) {
      setProgramId(programIdValue);
    }
    setLastChecked(new Date());
  };

  const clearSession = () => {
    console.log('🧹 Limpiando sesión activa global');
    clearActiveSession(); // Usar directamente el store
    setProgramId(null);
    setLastChecked(new Date());
    setViewingActiveSession(false);
  };

  const setViewingActiveSessionState = (isViewing) => {
    console.log(`👁️ Estableciendo viewingActiveSession: ${isViewing}`);
    setViewingActiveSession(isViewing);
  };
  
  // Diálogo para sesiones auto-pausadas
  const showResumeDialog = (session) => {
    Alert.alert(
      "Sesión Pausada",
      "Tu entrenamiento fue pausado automáticamente por inactividad",
      [
        {
          text: "Continuar",
          onPress: async () => {
            try {
              await resumeSession();
              checkSessionStatusFromHook(); // Actualizar estado después de reanudar
            } catch (error) {
              console.error('Error resuming session:', error);
            }
          }
        },
        {
          text: "Finalizar",
          onPress: async () => {
            try {
              await finishSession();
              clearSession();
            } catch (error) {
              console.error('Error finishing session:', error);
            }
          }
        },
        {
          text: "Abandonar",
          onPress: async () => {
            try {
              await abandonSession();
              clearSession();
            } catch (error) {
              console.error('Error abandoning session:', error);
            }
          }
        }
      ]
    );
  };

  const value = {
    activeSession,
    programId,
    isLoading,
    lastChecked,
    viewingActiveSession,
    updateSessionInfo,
    clearSession,
    setViewingActiveSessionState,
    refreshActiveSession: checkActiveSession,
    checkSessionStatus: checkSessionStatusFromHook,
    hasActiveSession: !!activeSession, // Calculado dinámicamente del store
  };

  return (
    <ActiveSessionContext.Provider value={value}>
      {children}
    </ActiveSessionContext.Provider>
  );
};

export const useActiveSession = () => {
  const context = useContext(ActiveSessionContext);
  if (!context) {
    throw new Error('useActiveSession must be used within an ActiveSessionProvider');
  }
  return context;
};

export default ActiveSessionContext;
