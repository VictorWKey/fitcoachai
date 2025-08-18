// Central registry to reset all Zustand stores in one call
// Each store that wants to be resettable should register its reset function here

const resetters = [];

export const registerReset = (resetFn) => {
  if (typeof resetFn === 'function') {
    resetters.push(resetFn);
  }
};

export const resetAllStores = () => {
  
  // Reset other registered stores
  resetters.forEach((reset) => {
    try {
      reset();
    } catch (e) {
      console.error('Error resetting store', e);
    }
  });
};