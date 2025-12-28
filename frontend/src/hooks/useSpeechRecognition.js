import { useState, useEffect, useCallback, useRef } from 'react';
import speechService from '../services/speechService';

/**
 * Enhanced Speech Recognition Hook with Medical Terminology Support
 * Provides advanced speech-to-text functionality with voice commands
 */
export const useSpeechRecognition = (options = {}) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(false);
  const [confidence, setConfidence] = useState(0);
  const [lastCommand, setLastCommand] = useState(null);

  const {
    continuous = false,
    interimResults = true,
    language = 'en-US',
    onResult,
    onError,
    onCommand,
    onStart,
    onEnd,
    autoStart = false,
    medicalTermsEnabled = true,
    commandsEnabled = true
  } = options;

  const timeoutRef = useRef(null);
  const restartTimeoutRef = useRef(null);

  // Initialize speech service
  useEffect(() => {
    const support = speechService.getSupport();
    setIsSupported(support.recognition);

    // Update speech service settings
    speechService.updateSettings({
      continuous,
      interimResults,
      language,
      medicalTermsEnabled,
      commandsEnabled
    });

    // Set up callbacks
    speechService.setCallbacks({
      onStart: () => {
        setIsListening(true);
        setError(null);
        onStart?.();
      },
      onEnd: () => {
        setIsListening(false);
        onEnd?.();
        
        // Auto-restart if continuous mode and no error
        if (continuous && !error) {
          restartTimeoutRef.current = setTimeout(() => {
            startListening();
          }, 100);
        }
      },
      onResult: (text) => {
        setTranscript(text);
        setInterimTranscript('');
        onResult?.(text);
        
        // Clear any restart timeout since we got a result
        if (restartTimeoutRef.current) {
          clearTimeout(restartTimeoutRef.current);
          restartTimeoutRef.current = null;
        }
      },
      onInterimResult: (text) => {
        setInterimTranscript(text);
      },
      onError: (errorCode, errorMessage) => {
        setError({ code: errorCode, message: errorMessage });
        setIsListening(false);
        onError?.(errorCode, errorMessage);
        
        // Clear any restart timeout on error
        if (restartTimeoutRef.current) {
          clearTimeout(restartTimeoutRef.current);
          restartTimeoutRef.current = null;
        }
      },
      onCommand: (command, originalText) => {
        setLastCommand({ command, originalText, timestamp: Date.now() });
        onCommand?.(command, originalText);
      }
    });

    // Auto-start if requested
    if (autoStart && support.recognition) {
      startListening();
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
      speechService.stopListening();
    };
  }, [continuous, interimResults, language, medicalTermsEnabled, commandsEnabled, autoStart]);

  // Start listening function
  const startListening = useCallback(() => {
    if (!isSupported) {
      setError({ 
        code: 'not-supported', 
        message: 'Speech recognition is not supported in this browser' 
      });
      return false;
    }

    if (isListening) {
      return false;
    }

    setError(null);
    setTranscript('');
    setInterimTranscript('');
    
    const success = speechService.startListening();
    
    if (!success) {
      setError({ 
        code: 'start-failed', 
        message: 'Failed to start speech recognition' 
      });
    }

    // Set timeout for automatic stop (prevent infinite listening)
    if (!continuous) {
      timeoutRef.current = setTimeout(() => {
        stopListening();
      }, 30000); // 30 seconds max
    }

    return success;
  }, [isSupported, isListening, continuous]);

  // Stop listening function
  const stopListening = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }

    speechService.stopListening();
  }, []);

  // Toggle listening
  const toggleListening = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  }, [isListening, startListening, stopListening]);

  // Reset transcript
  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  // Test recognition
  const testRecognition = useCallback(async () => {
    try {
      const result = await speechService.testRecognition();
      return { success: true, result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  // Get voice commands help
  const getVoiceCommands = useCallback(() => {
    return speechService.getVoiceCommandHelp();
  }, []);

  // Update settings
  const updateSettings = useCallback((newSettings) => {
    speechService.updateSettings(newSettings);
  }, []);

  // Get current settings
  const getSettings = useCallback(() => {
    return speechService.getSettings();
  }, []);

  return {
    // State
    isListening,
    transcript,
    interimTranscript,
    error,
    isSupported,
    confidence,
    lastCommand,
    
    // Actions
    startListening,
    stopListening,
    toggleListening,
    resetTranscript,
    testRecognition,
    
    // Utilities
    getVoiceCommands,
    updateSettings,
    getSettings
  };
};

export default useSpeechRecognition;