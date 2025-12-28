import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiEye, FiEyeOff, FiVolume2, FiSettings, FiPlay, FiPause } from 'react-icons/fi';
import useTextToSpeech from '../hooks/useTextToSpeech';
import accessibilityService from '../services/accessibilityService';

/**
 * Voice Accessibility Component
 * Provides enhanced voice features for visually impaired users
 */
const VoiceAccessibility = ({ isOpen, onClose }) => {
  const [accessibilityMode, setAccessibilityMode] = useState(false);
  const [screenReaderMode, setScreenReaderMode] = useState(false);
  const [voiceGuidance, setVoiceGuidance] = useState(true);
  const [detailedDescriptions, setDetailedDescriptions] = useState(true);
  const [keyboardShortcuts, setKeyboardShortcuts] = useState(true);
  const [highContrast, setHighContrast] = useState(false);
  const [fontSize, setFontSize] = useState('medium');
  const [currentlyReading, setCurrentlyReading] = useState(null);

  const {
    speak,
    isSpeaking,
    stopSpeaking,
    isSupported,
    availableVoices,
    currentVoice,
    changeVoice,
    updateSettings,
    speakDisclaimer
  } = useTextToSpeech({
    rate: 0.8, // Slower for accessibility
    pitch: 1.0,
    volume: 1.0,
    emphasizeImportant: true
  });

  // Load accessibility settings
  useEffect(() => {
    const settings = accessibilityService.getSettings();
    setScreenReaderMode(settings.screenReader);
    setHighContrast(settings.highContrast);
    setFontSize(settings.fontSize);
    setAccessibilityMode(settings.screenReader || settings.highContrast);
  }, []);

  // Keyboard shortcuts for accessibility
  useEffect(() => {
    if (!keyboardShortcuts) return;

    const handleKeyPress = (e) => {
      // Alt + R: Read current page
      if (e.altKey && e.key === 'r') {
        e.preventDefault();
        readCurrentPage();
      }
      
      // Alt + S: Stop reading
      if (e.altKey && e.key === 's') {
        e.preventDefault();
        stopSpeaking();
      }
      
      // Alt + H: Read help
      if (e.altKey && e.key === 'h') {
        e.preventDefault();
        readAccessibilityHelp();
      }
      
      // Alt + D: Read disclaimer
      if (e.altKey && e.key === 'd') {
        e.preventDefault();
        speakDisclaimer();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [keyboardShortcuts, stopSpeaking, speakDisclaimer]);

  // Auto-announce page changes for screen readers
  useEffect(() => {
    if (!voiceGuidance) return;

    const announcePageChange = () => {
      const pageTitle = document.title;
      const mainContent = document.querySelector('#main-content');
      
      if (mainContent) {
        const announcement = `Page loaded: ${pageTitle}. Use Alt+R to read the page content, Alt+H for help, or Alt+S to stop reading.`;
        setTimeout(() => speak(announcement), 1000);
      }
    };

    // Listen for route changes or content updates
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList' && mutation.target.id === 'main-content') {
          announcePageChange();
        }
      });
    });

    const mainContent = document.querySelector('#main-content');
    if (mainContent) {
      observer.observe(mainContent, { childList: true, subtree: true });
    }

    return () => observer.disconnect();
  }, [voiceGuidance, speak]);

  // Read current page content
  const readCurrentPage = useCallback(() => {
    const mainContent = document.querySelector('#main-content');
    if (!mainContent) return;

    // Extract readable text from the page
    const textContent = extractReadableText(mainContent);
    
    if (textContent) {
      setCurrentlyReading('page');
      speak(textContent);
    } else {
      speak('No readable content found on this page.');
    }
  }, [speak]);

  // Extract readable text from DOM element
  const extractReadableText = (element) => {
    const walker = document.createTreeWalker(
      element,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          const parent = node.parentElement;
          
          // Skip hidden elements
          if (parent.style.display === 'none' || parent.hidden) {
            return NodeFilter.FILTER_REJECT;
          }
          
          // Skip script and style elements
          if (['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(parent.tagName)) {
            return NodeFilter.FILTER_REJECT;
          }
          
          // Skip empty text nodes
          if (!node.textContent.trim()) {
            return NodeFilter.FILTER_REJECT;
          }
          
          return NodeFilter.FILTER_ACCEPT;
        }
      }
    );

    const textNodes = [];
    let node;
    
    while (node = walker.nextNode()) {
      textNodes.push(node.textContent.trim());
    }

    return textNodes.join(' ').replace(/\s+/g, ' ').trim();
  };

  // Read accessibility help
  const readAccessibilityHelp = useCallback(() => {
    const helpText = `
      MyDoc AI Accessibility Help.
      
      Keyboard Shortcuts:
      Alt + R: Read current page content
      Alt + S: Stop reading
      Alt + H: Read this help message
      Alt + D: Read medical disclaimer
      Tab: Navigate between interactive elements
      Enter or Space: Activate buttons and links
      Escape: Close dialogs and menus
      
      Voice Features:
      All AI responses are automatically read aloud.
      Medical terms are pronounced clearly.
      Important warnings are emphasized.
      
      Navigation:
      Use Tab to move between buttons, links, and form fields.
      Use arrow keys to navigate menus and lists.
      Use Enter to activate buttons and links.
      
      For additional help, contact support or visit our accessibility page.
    `;
    
    setCurrentlyReading('help');
    speak(helpText);
  }, [speak]);

  // Update accessibility setting
  const updateAccessibilitySetting = (key, value) => {
    accessibilityService.updateSetting(key, value);
    
    // Announce the change
    if (voiceGuidance) {
      const settingName = key.replace(/([A-Z])/g, ' $1').toLowerCase();
      const status = value ? 'enabled' : 'disabled';
      speak(`${settingName} ${status}`);
    }
  };

  // Voice settings for accessibility
  const accessibilityVoices = availableVoices.filter(voice => 
    voice.lang.startsWith('en') && 
    (voice.name.toLowerCase().includes('natural') || 
     voice.name.toLowerCase().includes('neural') ||
     voice.name.toLowerCase().includes('premium'))
  );

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[8500] flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="accessibility-title"
        aria-describedby="accessibility-description"
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-600 rounded-xl flex items-center justify-center">
                <FiEye className="text-white text-lg" />
              </div>
              <div>
                <h2 id="accessibility-title" className="text-xl font-bold text-gray-900 dark:text-white">
                  Voice Accessibility Settings
                </h2>
                <p id="accessibility-description" className="text-sm text-gray-600 dark:text-gray-400">
                  Enhanced voice features for visually impaired users
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              aria-label="Close accessibility settings"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh] space-y-6">
          {/* Quick Actions */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={readCurrentPage}
              className="flex flex-col items-center gap-2 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors"
              aria-label="Read current page content"
            >
              <FiPlay className="text-blue-600 dark:text-blue-400" size={20} />
              <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                Read Page
              </span>
            </button>

            <button
              onClick={stopSpeaking}
              className="flex flex-col items-center gap-2 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
              aria-label="Stop reading"
            >
              <FiPause className="text-red-600 dark:text-red-400" size={20} />
              <span className="text-sm font-medium text-red-800 dark:text-red-200">
                Stop Reading
              </span>
            </button>

            <button
              onClick={readAccessibilityHelp}
              className="flex flex-col items-center gap-2 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors"
              aria-label="Read accessibility help"
            >
              <FiSettings className="text-green-600 dark:text-green-400" size={20} />
              <span className="text-sm font-medium text-green-800 dark:text-green-200">
                Help
              </span>
            </button>

            <button
              onClick={speakDisclaimer}
              className="flex flex-col items-center gap-2 p-4 rounded-lg bg-purple-50 dark:bg-purple-900/20 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors"
              aria-label="Read medical disclaimer"
            >
              <FiVolume2 className="text-purple-600 dark:text-purple-400" size={20} />
              <span className="text-sm font-medium text-purple-800 dark:text-purple-200">
                Disclaimer
              </span>
            </button>
          </div>

          {/* Voice Guidance Settings */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Voice Guidance
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Auto-announce page changes
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Automatically read page titles and navigation changes
                  </p>
                </div>
                <button
                  onClick={() => {
                    setVoiceGuidance(!voiceGuidance);
                    updateAccessibilitySetting('announcements', !voiceGuidance);
                  }}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    voiceGuidance ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                  aria-label={`${voiceGuidance ? 'Disable' : 'Enable'} voice guidance`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                    voiceGuidance ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Detailed descriptions
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Include detailed descriptions of UI elements and content
                  </p>
                </div>
                <button
                  onClick={() => setDetailedDescriptions(!detailedDescriptions)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    detailedDescriptions ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                  aria-label={`${detailedDescriptions ? 'Disable' : 'Enable'} detailed descriptions`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                    detailedDescriptions ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Keyboard shortcuts
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Enable Alt+R, Alt+S, Alt+H keyboard shortcuts
                  </p>
                </div>
                <button
                  onClick={() => setKeyboardShortcuts(!keyboardShortcuts)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    keyboardShortcuts ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                  aria-label={`${keyboardShortcuts ? 'Disable' : 'Enable'} keyboard shortcuts`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                    keyboardShortcuts ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>
            </div>
          </div>

          {/* Voice Selection for Accessibility */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Accessibility Voice Settings
            </h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Preferred Voice for Accessibility
              </label>
              <select
                value={currentVoice?.name || ''}
                onChange={(e) => changeVoice(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                aria-label="Select voice for accessibility features"
              >
                <option value="">Default Voice</option>
                {accessibilityVoices.map(voice => (
                  <option key={voice.name} value={voice.name}>
                    {voice.name} ({voice.lang}) 
                    {voice.name.toLowerCase().includes('neural') && ' - Premium'}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Reading Speed: Slower for better comprehension
              </label>
              <input
                type="range"
                min="0.5"
                max="1.5"
                step="0.1"
                defaultValue="0.8"
                onChange={(e) => updateSettings({ voiceSpeed: parseFloat(e.target.value) })}
                className="w-full"
                aria-label="Adjust reading speed"
              />
            </div>
          </div>

          {/* Visual Accessibility */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Visual Accessibility
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    High contrast mode
                  </label>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Increase contrast for better visibility
                  </p>
                </div>
                <button
                  onClick={() => {
                    setHighContrast(!highContrast);
                    updateAccessibilitySetting('highContrast', !highContrast);
                  }}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    highContrast ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                  aria-label={`${highContrast ? 'Disable' : 'Enable'} high contrast mode`}
                >
                  <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                    highContrast ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Font Size
                </label>
                <select
                  value={fontSize}
                  onChange={(e) => {
                    setFontSize(e.target.value);
                    updateAccessibilitySetting('fontSize', e.target.value);
                  }}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  aria-label="Select font size"
                >
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                  <option value="large">Large</option>
                  <option value="extra-large">Extra Large</option>
                </select>
              </div>
            </div>
          </div>

          {/* Status Indicator */}
          {currentlyReading && (
            <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"
                />
                <span className="text-sm text-blue-800 dark:text-blue-200">
                  Currently reading: {currentlyReading}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Use Alt+H anytime for accessibility help
            </div>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default VoiceAccessibility;