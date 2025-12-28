// Authentication hooks
export { useAuthState, useAuthPersistence, useAuthError, useAuthToken } from './useAuthState';
export { useApi, useApiError } from './useApi';

// Voice and speech hooks
export { default as useSpeechRecognition } from './useSpeechRecognition';
export { default as useTextToSpeech } from './useTextToSpeech';

// Chat hooks
export { useChat } from './useChat';

// Re-export the main auth hook for convenience
export { useAuth } from '../contexts/AuthContext';