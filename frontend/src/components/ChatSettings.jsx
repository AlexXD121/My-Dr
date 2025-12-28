import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSettings, FiX, FiVolume2, FiVolumeX, FiMoon, FiSun, FiType, FiZap, FiMic, FiLayout } from 'react-icons/fi';
import ResponseFormattingSettings from './ResponseFormattingSettings';

const ChatSettings = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState({
    voiceEnabled: true,
    darkMode: document.documentElement.classList.contains('dark'),
    fontSize: 'medium',
    animationsEnabled: true,
    autoScroll: true,
    soundEffects: true,
    voiceInputVolume: 0.8,
    voiceOutputVolume: 0.9,
  });

  const [formattingSettingsOpen, setFormattingSettingsOpen] = useState(false);

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));

    // Apply settings immediately
    switch (key) {
      case 'darkMode':
        if (value) {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
        localStorage.setItem('theme', value ? 'dark' : 'light');
        break;
      case 'fontSize':
        document.documentElement.style.fontSize =
          value === 'small' ? '14px' :
            value === 'large' ? '18px' : '16px';
        localStorage.setItem('fontSize', value);
        break;
      default:
        localStorage.setItem(key, value);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999]"
            onClick={onClose}
          />

          {/* Settings Panel */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 
              w-full max-w-md mx-4 bg-white dark:bg-gray-800 rounded-3xl p-6 z-[10000]
              border border-gray-200 dark:border-gray-700 shadow-2xl
              max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-gray-800 rounded-2xl flex items-center justify-center">
                  <FiSettings className="text-white" size={20} />
                </div>
                <h2 className="text-xl font-bold text-gray-800 dark:text-gray-100">
                  Chat Settings
                </h2>
              </div>
              <motion.button
                onClick={onClose}
                className="p-2 rounded-xl bg-gray-100 dark:bg-gray-700 hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <FiX size={20} className="text-gray-600 dark:text-gray-400" />
              </motion.button>
            </div>

            {/* Settings Options */}
            <div className="space-y-4">
              {/* Voice Settings */}
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-2xl border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3">
                  {settings.voiceEnabled ? <FiVolume2 size={20} /> : <FiVolumeX size={20} />}
                  <div>
                    <h3 className="font-medium text-gray-800 dark:text-gray-100">Voice Responses</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Enable AI voice responses</p>
                  </div>
                </div>
                <motion.button
                  onClick={() => handleSettingChange('voiceEnabled', !settings.voiceEnabled)}
                  className={`w-12 h-6 rounded-full transition-colors ${settings.voiceEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  whileTap={{ scale: 0.95 }}
                >
                  <motion.div
                    className="w-5 h-5 bg-white rounded-full shadow-sm"
                    animate={{ x: settings.voiceEnabled ? 28 : 2 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                </motion.button>
              </div>

              {/* Theme Settings */}
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-2xl border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3">
                  {settings.darkMode ? <FiMoon size={20} /> : <FiSun size={20} />}
                  <div>
                    <h3 className="font-medium text-gray-800 dark:text-gray-100">Dark Mode</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Toggle dark theme</p>
                  </div>
                </div>
                <motion.button
                  onClick={() => handleSettingChange('darkMode', !settings.darkMode)}
                  className={`w-12 h-6 rounded-full transition-colors ${settings.darkMode ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  whileTap={{ scale: 0.95 }}
                >
                  <motion.div
                    className="w-5 h-5 bg-white rounded-full shadow-sm"
                    animate={{ x: settings.darkMode ? 28 : 2 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                </motion.button>
              </div>

              {/* Font Size */}
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-2xl border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3 mb-3">
                  <FiType size={20} />
                  <div>
                    <h3 className="font-medium text-gray-800 dark:text-gray-100">Font Size</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Adjust text size</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  {['small', 'medium', 'large'].map((size) => (
                    <motion.button
                      key={size}
                      onClick={() => handleSettingChange('fontSize', size)}
                      className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${settings.fontSize === size
                        ? 'bg-blue-600 text-white'
                        : 'bg-white dark:bg-gray-600 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-500'
                        }`}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      {size.charAt(0).toUpperCase() + size.slice(1)}
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Voice Input Volume */}
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-2xl border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3 mb-3">
                  <FiMic size={20} />
                  <div>
                    <h3 className="font-medium text-gray-800 dark:text-gray-100">Voice Input Sensitivity</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Adjust microphone sensitivity</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500 dark:text-gray-400">Low</span>
                  <input
                    type="range"
                    min="0.1"
                    max="1"
                    step="0.1"
                    value={settings.voiceInputVolume}
                    onChange={(e) => handleSettingChange('voiceInputVolume', parseFloat(e.target.value))}
                    className="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer"
                  />
                  <span className="text-xs text-gray-500 dark:text-gray-400">High</span>
                </div>
                <div className="text-center mt-2">
                  <span className="text-xs text-gray-600 dark:text-gray-300">
                    {Math.round(settings.voiceInputVolume * 100)}%
                  </span>
                </div>
              </div>

              {/* Voice Output Volume */}
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-2xl border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3 mb-3">
                  <FiVolume2 size={20} />
                  <div>
                    <h3 className="font-medium text-gray-800 dark:text-gray-100">Voice Output Volume</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Adjust AI voice volume</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500 dark:text-gray-400">Quiet</span>
                  <input
                    type="range"
                    min="0.1"
                    max="1"
                    step="0.1"
                    value={settings.voiceOutputVolume}
                    onChange={(e) => handleSettingChange('voiceOutputVolume', parseFloat(e.target.value))}
                    className="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer"
                  />
                  <span className="text-xs text-gray-500 dark:text-gray-400">Loud</span>
                </div>
                <div className="text-center mt-2">
                  <span className="text-xs text-gray-600 dark:text-gray-300">
                    {Math.round(settings.voiceOutputVolume * 100)}%
                  </span>
                </div>
              </div>

              {/* Response Formatting */}
              <motion.button
                onClick={() => setFormattingSettingsOpen(true)}
                className="w-full p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl border border-blue-200 dark:border-blue-800 hover:from-blue-100 hover:to-purple-100 dark:hover:from-blue-900/30 dark:hover:to-purple-900/30 transition-all"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center gap-3">
                  <FiLayout size={20} className="text-blue-600 dark:text-blue-400" />
                  <div className="text-left">
                    <h3 className="font-medium text-gray-800 dark:text-gray-100">Response Formatting</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Customize AI response display and structure</p>
                  </div>
                  <div className="ml-auto">
                    <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                      <span className="text-blue-600 dark:text-blue-400 text-sm">→</span>
                    </div>
                  </div>
                </div>
              </motion.button>

              {/* Animations */}
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-2xl border border-gray-200 dark:border-gray-600">
                <div className="flex items-center gap-3">
                  <FiZap size={20} />
                  <div>
                    <h3 className="font-medium text-gray-800 dark:text-gray-100">Animations</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Enable smooth animations</p>
                  </div>
                </div>
                <motion.button
                  onClick={() => handleSettingChange('animationsEnabled', !settings.animationsEnabled)}
                  className={`w-12 h-6 rounded-full transition-colors ${settings.animationsEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                    }`}
                  whileTap={{ scale: 0.95 }}
                >
                  <motion.div
                    className="w-5 h-5 bg-white rounded-full shadow-sm"
                    animate={{ x: settings.animationsEnabled ? 28 : 2 }}
                    transition={{ type: "spring", stiffness: 500, damping: 30 }}
                  />
                </motion.button>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-600">
              <p className="text-xs text-center text-gray-500 dark:text-gray-400">
                Settings are saved automatically
              </p>
            </div>
          </motion.div>

          {/* Response Formatting Settings Modal */}
          <ResponseFormattingSettings
            isOpen={formattingSettingsOpen}
            onClose={() => setFormattingSettingsOpen(false)}
            onSettingsChange={(formattingSettings) => {
              // Handle formatting settings changes
              console.log('Formatting settings updated:', formattingSettings);
            }}
          />
        </>
      )}
    </AnimatePresence>
  );
};

export default ChatSettings;