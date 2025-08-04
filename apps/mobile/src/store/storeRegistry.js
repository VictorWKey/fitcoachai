// Central registry to reset all Zustand stores in one call
// Each store that wants to be resettable should register its reset function here

import { useSessionStore } from './sessionStore';

const resetters = [];

export const registerReset = (resetFn) => {
  if (typeof resetFn === 'function') {
    resetters.push(resetFn);
  }
};

export const resetAllStores = () => {
  // Reset session store
  useSessionStore.getState().clearActiveSession();
  useSessionStore.getState().clearError();
  
  // Reset other registered stores
  resetters.forEach((reset) => {
    try {
      reset();
    } catch (e) {
      console.error('Error resetting store', e);
    }
  });
};
