import { useState, useEffect } from 'react';

// Hook for managing authentication loading states
export const useAuthState = () => {
  const [authState, setAuthState] = useState({
    isAuthenticated: false,
    isVerified: false,
    isLoading: true,
    hasError: false,
    isOnline: navigator.onLine
  });

  // This will be populated by the AuthWrapper component
  return authState;
};

// Hook for managing authentication persistence
export const useAuthPersistence = () => {
  const [persistedAuthData, setPersistedAuthData] = useState(null);

  useEffect(() => {
    const storedAuth = localStorage.getItem('sukh_auth_state');
    if (storedAuth) {
      try {
        const authData = JSON.parse(storedAuth);
        setPersistedAuthData(authData);
      } catch (error) {
        console.error('Error parsing stored auth data:', error);
        localStorage.removeItem('sukh_auth_state');
      }
    }
  }, []);

  const clearPersistedAuth = () => {
    localStorage.removeItem('sukh_auth_state');
    setPersistedAuthData(null);
  };

  return {
    persistedAuthData,
    clearPersistedAuth,
    hasPersistedAuth: !!persistedAuthData
  };
};

// Hook for handling authentication errors with user-friendly messages
export const useAuthError = () => {
  const [error, setError] = useState(null);

  const getErrorMessage = (errorCode) => {
    const errorMessages = {
      'auth/user-not-found': 'No account found with this email address.',
      'auth/wrong-password': 'Incorrect password. Please try again.',
      'auth/email-already-in-use': 'An account with this email already exists.',
      'auth/weak-password': 'Password should be at least 6 characters long.',
      'auth/invalid-email': 'Please enter a valid email address.',
      'auth/user-disabled': 'This account has been disabled.',
      'auth/too-many-requests': 'Too many failed attempts. Please try again later.',
      'auth/network-request-failed': 'Network error. Please check your connection.',
      'auth/popup-closed-by-user': 'Sign-in was cancelled.',
      'auth/cancelled-popup-request': 'Sign-in was cancelled.',
      'auth/popup-blocked': 'Pop-up was blocked. Please allow pop-ups for this site.',
      'auth/user-token-expired': 'Your session has expired. Please sign in again.'
    };

    return errorMessages[errorCode] || 'An unexpected error occurred. Please try again.';
  };

  const clearError = () => setError(null);

  return {
    error,
    errorMessage: error ? getErrorMessage(error.code || error) : null,
    clearError,
    hasError: !!error
  };
};

// Hook for token management
export const useAuthToken = () => {
  const [token, setToken] = useState(null);
  const [tokenLoading, setTokenLoading] = useState(false);

  const refreshToken = async (forceRefresh = false) => {
    // This will be implemented when needed
    return null;
  };

  return {
    token,
    tokenLoading,
    refreshToken,
    hasValidToken: !!token
  };
};