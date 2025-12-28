import { useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import apiService from '../services/api';

// Hook for integrating API service with authentication
export const useApi = () => {
  const { getIdToken, currentUser, isOnline } = useAuth();

  // Set up API service with authentication
  useEffect(() => {
    if (currentUser) {
      // Set up token refresh callback
      apiService.setTokenRefreshCallback(getIdToken);
      
      // Get initial token
      getIdToken().then(token => {
        if (token) {
          apiService.setToken(token);
        }
      }).catch(console.error);
    } else {
      // Clear token when user logs out
      apiService.clearToken();
      apiService.setTokenRefreshCallback(null);
    }
  }, [currentUser, getIdToken]);

  // Authenticated API methods
  const authenticatedRequest = useCallback(async (endpoint, options = {}) => {
    if (!currentUser) {
      throw new Error('User not authenticated');
    }

    try {
      // Ensure we have a valid token
      const token = await getIdToken();
      if (token) {
        apiService.setToken(token);
      }

      return await apiService.request(endpoint, options);
    } catch (error) {
      throw error;
    }
  }, [currentUser, getIdToken]);

  // API methods with authentication
  const api = {
    // Health check
    healthCheck: () => apiService.healthCheck(),
    
    // Authenticated requests
    get: (endpoint) => authenticatedRequest(endpoint, { method: 'GET' }),
    post: (endpoint, data) => authenticatedRequest(endpoint, { 
      method: 'POST', 
      body: JSON.stringify(data) 
    }),
    put: (endpoint, data) => authenticatedRequest(endpoint, { 
      method: 'PUT', 
      body: JSON.stringify(data) 
    }),
    delete: (endpoint) => authenticatedRequest(endpoint, { method: 'DELETE' }),

    // Specific API endpoints
    sendMessage: (message) => authenticatedRequest('/chat', { 
      method: 'POST', 
      body: JSON.stringify({ message }) 
    }),
    getUserProfile: () => authenticatedRequest('/user/profile'),
    authenticateWithFirebase: (idToken) => apiService.post('/auth/firebase', { idToken }),
    
    // Offline-supported requests
    getWithOfflineSupport: async (endpoint) => {
      if (!currentUser) {
        throw new Error('User not authenticated');
      }
      
      const token = await getIdToken();
      if (token) {
        apiService.setToken(token);
      }
      
      return apiService.requestWithOfflineSupport(endpoint, { method: 'GET' });
    }
  };

  return {
    api,
    isOnline,
    isAuthenticated: !!currentUser
  };
};

// Hook for API error handling
export const useApiError = () => {
  const handleApiError = useCallback((error) => {
    console.error('API Error:', error);

    // Categorize errors
    if (error.message.includes('Rate limit exceeded')) {
      return {
        type: 'rate_limit',
        message: 'Too many requests. Please wait a moment and try again.',
        retryable: true
      };
    }

    if (error.message.includes('Authentication required')) {
      return {
        type: 'auth_error',
        message: 'Please sign in to continue.',
        retryable: false
      };
    }

    if (error.message.includes('offline')) {
      return {
        type: 'offline_error',
        message: 'You are currently offline. Some features may not be available.',
        retryable: true
      };
    }

    if (error.message.includes('Network')) {
      return {
        type: 'network_error',
        message: 'Network connection problem. Please check your internet connection.',
        retryable: true
      };
    }

    return {
      type: 'unknown_error',
      message: 'Something went wrong. Please try again.',
      retryable: true
    };
  }, []);

  return { handleApiError };
};