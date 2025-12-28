import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import pwaService from '../services/pwaService';

export default function PWAInstallPrompt() {
  const [showInstall, setShowInstall] = useState(false);
  const [showUpdate, setShowUpdate] = useState(false);
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  useEffect(() => {
    // Listen for PWA events
    const handleInstallAvailable = () => setShowInstall(true);
    const handleInstallCompleted = () => setShowInstall(false);
    const handleUpdateAvailable = () => setShowUpdate(true);
    const handleNetworkOffline = () => setIsOffline(true);
    const handleNetworkOnline = () => setIsOffline(false);

    window.addEventListener('pwa-install-available', handleInstallAvailable);
    window.addEventListener('pwa-install-completed', handleInstallCompleted);
    window.addEventListener('pwa-update-available', handleUpdateAvailable);
    window.addEventListener('network-offline', handleNetworkOffline);
    window.addEventListener('network-online', handleNetworkOnline);

    return () => {
      window.removeEventListener('pwa-install-available', handleInstallAvailable);
      window.removeEventListener('pwa-install-completed', handleInstallCompleted);
      window.removeEventListener('pwa-update-available', handleUpdateAvailable);
      window.removeEventListener('network-offline', handleNetworkOffline);
      window.removeEventListener('network-online', handleNetworkOnline);
    };
  }, []);

  const handleInstall = async () => {
    await pwaService.installApp();
    setShowInstall(false);
  };

  const handleUpdate = () => {
    window.location.reload();
  };

  return (
    <>
      {/* Install Prompt */}
      <AnimatePresence>
        {showInstall && (
          <motion.div
            initial={{ opacity: 0, y: 100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 100 }}
            className="fixed bottom-20 left-4 right-4 z-50 lg:left-auto lg:right-4 lg:w-96"
          >
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 p-4">
              <div className="flex items-start gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-gray-800 rounded-2xl flex items-center justify-center text-2xl">
                  🩺
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                    Install MyDoc AI
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mb-3">
                    Get quick access to your medical assistant. Install the app for a better experience.
                  </p>
                  <div className="flex gap-2">
                    <motion.button
                      onClick={handleInstall}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium
                        hover:bg-blue-700 transition-colors duration-200"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Install
                    </motion.button>
                    <motion.button
                      onClick={() => setShowInstall(false)}
                      className="px-4 py-2 text-gray-600 dark:text-gray-300 rounded-lg text-sm font-medium
                        hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Later
                    </motion.button>
                  </div>
                </div>
                <motion.button
                  onClick={() => setShowInstall(false)}
                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Update Available Prompt */}
      <AnimatePresence>
        {showUpdate && (
          <motion.div
            initial={{ opacity: 0, y: -100 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -100 }}
            className="fixed top-4 left-4 right-4 z-50 lg:left-auto lg:right-4 lg:w-96"
          >
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-2xl p-4">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 bg-green-100 dark:bg-green-800 rounded-full flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-green-900 dark:text-green-100 mb-1">
                    Update Available
                  </h3>
                  <p className="text-sm text-green-700 dark:text-green-300 mb-3">
                    A new version of MyDoc AI is available with improvements and bug fixes.
                  </p>
                  <div className="flex gap-2">
                    <motion.button
                      onClick={handleUpdate}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium
                        hover:bg-green-700 transition-colors duration-200"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Update Now
                    </motion.button>
                    <motion.button
                      onClick={() => setShowUpdate(false)}
                      className="px-4 py-2 text-green-700 dark:text-green-300 rounded-lg text-sm font-medium
                        hover:bg-green-100 dark:hover:bg-green-800 transition-colors duration-200"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      Later
                    </motion.button>
                  </div>
                </div>
                <motion.button
                  onClick={() => setShowUpdate(false)}
                  className="p-1 text-green-400 hover:text-green-600 dark:hover:text-green-300"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Offline Status */}
      <AnimatePresence>
        {isOffline && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-16 left-4 right-4 z-40 lg:left-auto lg:right-4 lg:w-80"
          >
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  You're offline
                </span>
                <span className="text-xs text-yellow-600 dark:text-yellow-300 ml-auto">
                  Messages will sync when online
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}