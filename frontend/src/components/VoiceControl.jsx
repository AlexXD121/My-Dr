import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiMic, FiMicOff, FiCommand, FiEye, FiSettings, FiHeart } from 'react-icons/fi';
import useSpeechRecognition from '../hooks/useSpeechRecognition';
import useTextToSpeech from '../hooks/useTextToSpeech';
import VoiceSettings from './VoiceSettings';
import VoiceAccessibility from './VoiceAccessibility';
import FemaleVoiceSettings from './FemaleVoiceSettings';
import voiceNotificationService from '../services/voiceNotificationService';

/**
 * Voice Control Component
 * Provides comprehensive voice control interface with accessibility features
 */
const VoiceControl = ({ 
  className = '',
  showLabels = true,
  compact = false,
  onVoiceInput,
  onVoiceCommand,
  closeModalsOnChatSettings = false
}) => {
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [accessibilityOpen, setAccessibilityOpen] = useState(false);
  const [femaleVoiceOpen, setFemaleVoiceOpen] = useState(false);

  // Close voice modals when ChatSettings opens
  useEffect(() => {
    if (closeModalsOnChatSettings) {
      setSettingsOpen(false);
      setAccessibilityOpen(false);
      setFemaleVoiceOpen(false);
    }
  }, [closeModalsOnChatSettings]);
  const [voiceControlEnabled, setVoiceControlEnabled] = useState(true);
  const [continuousMode, setContinuousMode] = useState(false);
  const [showVisualFeedback, setShowVisualFeedback] = useState(true);

  // Speech recognition hook
  const {
    isListening,
    transcript,
    interimTranscript,
    startListening,
    stopListening,
    error: speechError,
    isSupported: speechSupported,
    getVoiceCommands
  } = useSpeechRecognition({
    continuous: continuousMode,
    interimResults: true,
    medicalTermsEnabled: true,
    commandsEnabled: true,
    onResult: (text) => {
      onVoiceInput?.(text);
      // Announce successful recognition
      voiceNotificationService.queueNotification({
        message: 'Voice input received',
        priority: 4,
        type: 'success',
        settings: { rate: 1.2, pitch: 1.0, volume: 0.8 }
      });
    },
    onError: (error, message) => {
      console.error('Speech recognition error:', error, message);
      // Announce error
      voiceNotificationService.queueNotification({
        message: `Voice recognition error: ${message}`,
        priority: 2,
        type: 'error'
      });
    },
    onCommand: (command, originalText) => {
      onVoiceCommand?.(command, originalText);
      // Announce command execution
      voiceNotificationService.queueNotification({
        message: `Executing command: ${command}`,
        priority: 3,
        type: 'command'
      });
    }
  });

  // Text-to-speech hook
  const {
    speak,
    isSpeaking,
    stopSpeaking,
    isSupported: speechSynthesisSupported,
    speakDisclaimer
  } = useTextToSpeech({
    rate: 0.9,
    pitch: 1.0,
    volume: 1.0,
    medicalPronunciation: true,
    emphasizeImportant: true
  });

  // Load settings
  useEffect(() => {
    const savedSettings = localStorage.getItem('mydoc-voice-control');
    if (savedSettings) {
      const settings = JSON.parse(savedSettings);
      setVoiceControlEnabled(settings.enabled ?? true);
      setContinuousMode(settings.continuous ?? false);
      setShowVisualFeedback(settings.visualFeedback ?? true);
    }
  }, []);

  // Save settings
  const saveSettings = useCallback(() => {
    const settings = {
      enabled: voiceControlEnabled,
      continuous: continuousMode,
      visualFeedback: showVisualFeedback
    };
    localStorage.setItem('mydoc-voice-control', JSON.stringify(settings));
  }, [voiceControlEnabled, continuousMode, showVisualFeedback]);

  useEffect(() => {
    saveSettings();
  }, [saveSettings]);

  // Handle voice control toggle
  const toggleVoiceControl = useCallback(() => {
    if (isListening) {
      stopListening();
    }
    setVoiceControlEnabled(!voiceControlEnabled);
    
    const message = voiceControlEnabled ? 'Voice control disabled' : 'Voice control enabled';
    voiceNotificationService.queueNotification({
      message,
      priority: 3,
      type: 'info'
    });
  }, [voiceControlEnabled, isListening, stopListening]);

  // Handle listening toggle
  const toggleListening = useCallback(() => {
    if (!voiceControlEnabled || !speechSupported) return;

    if (isListening) {
      stopListening();
    } else {
      const success = startListening();
      if (!success) {
        voiceNotificationService.queueNotification({
          message: 'Failed to start voice recognition. Please check microphone permissions.',
          priority: 2,
          type: 'error'
        });
      }
    }
  }, [voiceControlEnabled, speechSupported, isListening, startListening, stopListening]);

  // Handle continuous mode toggle
  const toggleContinuousMode = useCallback(() => {
    setContinuousMode(!continuousMode);
    
    const message = continuousMode 
      ? 'Continuous listening disabled' 
      : 'Continuous listening enabled';
    
    voiceNotificationService.queueNotification({
      message,
      priority: 3,
      type: 'info'
    });
  }, [continuousMode]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Ctrl + Shift + V: Toggle voice control
      if (e.ctrlKey && e.shiftKey && e.key === 'V') {
        e.preventDefault();
        toggleVoiceControl();
      }
      
      // Ctrl + Shift + L: Toggle listening
      if (e.ctrlKey && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        toggleListening();
      }
      
      // Ctrl + Shift + S: Stop all speech
      if (e.ctrlKey && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        stopSpeaking();
        voiceNotificationService.clearQueue();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [toggleVoiceControl, toggleListening, stopSpeaking]);

  // Get voice commands for display
  const voiceCommands = getVoiceCommands();

  const buttonSize = compact ? 'w-8 h-8' : 'w-10 h-10 sm:w-12 sm:h-12';
  const iconSize = compact ? 16 : 20;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Voice Recognition Button */}
      <motion.button
        onClick={toggleListening}
        disabled={!voiceControlEnabled || !speechSupported}
        className={`${buttonSize} rounded-xl transition-all duration-300 relative ${
          isListening
            ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg'
            : voiceControlEnabled && speechSupported
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 shadow-md hover:shadow-lg'
            : 'bg-gray-300 dark:bg-gray-600 text-gray-500 cursor-not-allowed'
        }`}
        whileHover={{ 
          scale: voiceControlEnabled && speechSupported ? 1.05 : 1,
          rotate: isListening ? [0, -5, 5, 0] : 0
        }}
        whileTap={{ scale: voiceControlEnabled && speechSupported ? 0.95 : 1 }}
        title={
          !speechSupported
            ? 'Speech recognition not supported'
            : !voiceControlEnabled
            ? 'Voice control disabled'
            : isListening
            ? 'Stop listening'
            : 'Start voice input'
        }
        aria-label={
          !speechSupported
            ? 'Speech recognition not supported'
            : !voiceControlEnabled
            ? 'Voice control disabled'
            : isListening
            ? 'Stop listening'
            : 'Start voice input'
        }
      >
        {isListening ? (
          <FiMicOff size={iconSize} />
        ) : (
          <FiMic size={iconSize} />
        )}
        
        {/* Listening indicator */}
        {isListening && showVisualFeedback && (
          <motion.div
            className="absolute -top-1 -right-1 w-3 h-3 bg-red-400 rounded-full"
            animate={{ scale: [1, 1.3, 1], opacity: [1, 0.7, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
        
        {/* Error indicator */}
        {speechError && showVisualFeedback && (
          <motion.div
            className="absolute -bottom-1 -right-1 w-3 h-3 bg-yellow-400 rounded-full"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 0.5, repeat: 3 }}
          />
        )}
      </motion.button>

      {/* Voice Control Toggle */}
      <motion.button
        onClick={toggleVoiceControl}
        className={`${buttonSize} rounded-xl transition-all duration-300 ${
          voiceControlEnabled
            ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-md hover:shadow-lg'
            : 'bg-gray-300 dark:bg-gray-600 text-gray-500 hover:bg-gray-400 dark:hover:bg-gray-500'
        }`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        title={voiceControlEnabled ? 'Disable voice control' : 'Enable voice control'}
        aria-label={voiceControlEnabled ? 'Disable voice control' : 'Enable voice control'}
      >
        <FiCommand size={iconSize} />
      </motion.button>

      {/* Voice Settings */}
      <motion.button
        onClick={() => setSettingsOpen(true)}
        className={`${buttonSize} rounded-xl bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600 transition-all duration-300`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        title="Voice settings"
        aria-label="Open voice settings"
      >
        <FiSettings size={iconSize} />
      </motion.button>

      {/* Female Voice Settings */}
      <motion.button
        onClick={() => setFemaleVoiceOpen(true)}
        className={`${buttonSize} rounded-xl bg-gradient-to-r from-pink-100 to-purple-100 dark:from-pink-900/30 dark:to-purple-900/30 text-pink-600 dark:text-pink-400 hover:from-pink-200 hover:to-purple-200 dark:hover:from-pink-900/50 dark:hover:to-purple-900/50 transition-all duration-300`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        title="Female voice settings"
        aria-label="Open female voice settings"
      >
        <FiHeart size={iconSize} />
      </motion.button>

      {/* Accessibility Settings */}
      <motion.button
        onClick={() => setAccessibilityOpen(true)}
        className={`${buttonSize} rounded-xl bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-all duration-300`}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        title="Voice accessibility settings"
        aria-label="Open voice accessibility settings"
      >
        <FiEye size={iconSize} />
      </motion.button>

      {/* Labels */}
      {showLabels && !compact && (
        <div className="hidden md:flex flex-col text-xs text-gray-600 dark:text-gray-400">
          <span>Voice Control</span>
          {isListening && (
            <span className="text-red-500 animate-pulse">Listening...</span>
          )}
          {isSpeaking && (
            <span className="text-green-500 animate-pulse">Speaking...</span>
          )}
        </div>
      )}

      {/* Visual Feedback */}
      <AnimatePresence>
        {showVisualFeedback && (interimTranscript || transcript) && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute top-full left-0 mt-2 p-3 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 max-w-xs z-[100]"
          >
            <div className="text-sm">
              {interimTranscript && (
                <div className="text-gray-500 dark:text-gray-400 italic">
                  {interimTranscript}
                </div>
              )}
              {transcript && (
                <div className="text-gray-900 dark:text-white font-medium">
                  {transcript}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Voice Settings Modal */}
      <VoiceSettings
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />

      {/* Female Voice Settings Modal */}
      <FemaleVoiceSettings
        isOpen={femaleVoiceOpen}
        onClose={() => setFemaleVoiceOpen(false)}
      />

      {/* Voice Accessibility Modal */}
      <VoiceAccessibility
        isOpen={accessibilityOpen}
        onClose={() => setAccessibilityOpen(false)}
      />

      {/* Keyboard Shortcuts Help */}
      {showLabels && !compact && (
        <div className="hidden lg:block text-xs text-gray-500 dark:text-gray-400 ml-4">
          <div>Ctrl+Shift+V: Toggle voice</div>
          <div>Ctrl+Shift+L: Toggle listening</div>
          <div>Ctrl+Shift+S: Stop speech</div>
        </div>
      )}
    </div>
  );
};

export default VoiceControl;