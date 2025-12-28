import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import accessibilityService from '../services/accessibilityService';

export default function AccessibilitySettings({ isOpen, onClose }) {
  const [settings, setSettings] = useState(accessibilityService.getSettings());

  useEffect(() => {
    const handleSettingsChange = (e) => {
      setSettings(e.detail);
    };

    window.addEventListener('accessibility-settings-changed', handleSettingsChange);
    return () => {
      window.removeEventListener('accessibility-settings-changed', handleSettingsChange);
    };
  }, []);

  const updateSetting = (key, value) => {
    accessibilityService.updateSetting(key, value);
    accessibilityService.announce(`${key} setting changed to ${value}`);
  };

  const resetSettings = () => {
    accessibilityService.resetSettings();
    accessibilityService.announce('Accessibility settings reset to defaults');
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
          onClick={onClose}
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto bg-white dark:bg-gray-800 
            rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700"
          role="dialog"
          aria-labelledby="accessibility-title"
          aria-describedby="accessibility-description"
        >
          {/* Header */}
          <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 
            px-6 py-4 rounded-t-2xl">
            <div className="flex items-center justify-between">
              <div>
                <h2 id="accessibility-title" className="text-xl font-semibold text-gray-900 dark:text-white">
                  Accessibility Settings
                </h2>
                <p id="accessibility-description" className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                  Customize your experience for better accessibility
                </p>
              </div>
              <motion.button
                onClick={onClose}
                className="p-2 rounded-lg text-gray-500 hover:text-gray-700 dark:text-gray-400 
                  dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                aria-label="Close accessibility settings"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </motion.button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Visual Settings */}
            <section>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Visual Settings
              </h3>
              
              <div className="space-y-4">
                {/* High Contrast */}
                <div className="flex items-center justify-between">
                  <div>
                    <label htmlFor="high-contrast" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      High Contrast Mode
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Increases contrast for better visibility
                    </p>
                  </div>
                  <motion.button
                    id="high-contrast"
                    onClick={() => updateSetting('highContrast', !settings.highContrast)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${settings.highContrast ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}`}
                    whileTap={{ scale: 0.95 }}
                    role="switch"
                    aria-checked={settings.highContrast}
                    aria-describedby="high-contrast-desc"
                  >
                    <motion.span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${settings.highContrast ? 'translate-x-6' : 'translate-x-1'}`}
                      layout
                    />
                  </motion.button>
                </div>

                {/* Font Size */}
                <div>
                  <label htmlFor="font-size" className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-2">
                    Font Size
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {['small', 'medium', 'large', 'extra-large'].map((size) => (
                      <motion.button
                        key={size}
                        onClick={() => updateSetting('fontSize', size)}
                        className={`px-3 py-2 text-xs rounded-lg border transition-colors
                          ${settings.fontSize === size
                            ? 'bg-blue-600 text-white border-blue-600'
                            : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600'
                          }`}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        aria-pressed={settings.fontSize === size}
                      >
                        {size.charAt(0).toUpperCase() + size.slice(1).replace('-', ' ')}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Reduced Motion */}
                <div className="flex items-center justify-between">
                  <div>
                    <label htmlFor="reduced-motion" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Reduce Motion
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Minimizes animations and transitions
                    </p>
                  </div>
                  <motion.button
                    id="reduced-motion"
                    onClick={() => updateSetting('reducedMotion', !settings.reducedMotion)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${settings.reducedMotion ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}`}
                    whileTap={{ scale: 0.95 }}
                    role="switch"
                    aria-checked={settings.reducedMotion}
                  >
                    <motion.span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${settings.reducedMotion ? 'translate-x-6' : 'translate-x-1'}`}
                      layout
                    />
                  </motion.button>
                </div>
              </div>
            </section>

            {/* Navigation Settings */}
            <section>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Navigation Settings
              </h3>
              
              <div className="space-y-4">
                {/* Keyboard Navigation */}
                <div className="flex items-center justify-between">
                  <div>
                    <label htmlFor="keyboard-nav" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Enhanced Keyboard Navigation
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Improved keyboard shortcuts and navigation
                    </p>
                  </div>
                  <motion.button
                    id="keyboard-nav"
                    onClick={() => updateSetting('keyboardNavigation', !settings.keyboardNavigation)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${settings.keyboardNavigation ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}`}
                    whileTap={{ scale: 0.95 }}
                    role="switch"
                    aria-checked={settings.keyboardNavigation}
                  >
                    <motion.span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${settings.keyboardNavigation ? 'translate-x-6' : 'translate-x-1'}`}
                      layout
                    />
                  </motion.button>
                </div>

                {/* Focus Visible */}
                <div className="flex items-center justify-between">
                  <div>
                    <label htmlFor="focus-visible" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Enhanced Focus Indicators
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      More visible focus outlines for keyboard navigation
                    </p>
                  </div>
                  <motion.button
                    id="focus-visible"
                    onClick={() => updateSetting('focusVisible', !settings.focusVisible)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${settings.focusVisible ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}`}
                    whileTap={{ scale: 0.95 }}
                    role="switch"
                    aria-checked={settings.focusVisible}
                  >
                    <motion.span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${settings.focusVisible ? 'translate-x-6' : 'translate-x-1'}`}
                      layout
                    />
                  </motion.button>
                </div>
              </div>
            </section>

            {/* Screen Reader Settings */}
            <section>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Screen Reader Settings
              </h3>
              
              <div className="space-y-4">
                {/* Screen Reader Detection */}
                <div className="flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Screen Reader Detected
                    </span>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {settings.screenReader ? 'Screen reader support is active' : 'No screen reader detected'}
                    </p>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-medium
                    ${settings.screenReader 
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                    }`}>
                    {settings.screenReader ? 'Active' : 'Inactive'}
                  </div>
                </div>

                {/* Announcements */}
                <div className="flex items-center justify-between">
                  <div>
                    <label htmlFor="announcements" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      System Announcements
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Announce important changes and updates
                    </p>
                  </div>
                  <motion.button
                    id="announcements"
                    onClick={() => updateSetting('announcements', !settings.announcements)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors
                      ${settings.announcements ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'}`}
                    whileTap={{ scale: 0.95 }}
                    role="switch"
                    aria-checked={settings.announcements}
                  >
                    <motion.span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform
                        ${settings.announcements ? 'translate-x-6' : 'translate-x-1'}`}
                      layout
                    />
                  </motion.button>
                </div>
              </div>
            </section>

            {/* Keyboard Shortcuts */}
            <section>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Keyboard Shortcuts
              </h3>
              
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">Skip to main content:</span>
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 rounded border text-xs">Tab</kbd>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">Close modal/menu:</span>
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 rounded border text-xs">Esc</kbd>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">Navigate menu:</span>
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 rounded border text-xs">↑↓</kbd>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">Navigate tabs:</span>
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 rounded border text-xs">←→</kbd>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">First/Last item:</span>
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 rounded border text-xs">Home/End</kbd>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-300">Activate button:</span>
                    <kbd className="px-2 py-1 bg-white dark:bg-gray-800 rounded border text-xs">Enter/Space</kbd>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 
            px-6 py-4 rounded-b-2xl">
            <div className="flex items-center justify-between">
              <motion.button
                onClick={resetSettings}
                className="px-4 py-2 text-sm text-gray-600 dark:text-gray-300 hover:text-gray-800 
                  dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Reset to Defaults
              </motion.button>
              
              <motion.button
                onClick={onClose}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                  transition-colors text-sm font-medium"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Done
              </motion.button>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}