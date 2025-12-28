import { GiHamburgerMenu } from 'react-icons/gi';
import {
  FiBookOpen,
  FiBarChart,
  FiMessageCircle,
  FiMic,
  FiMicOff,
  FiVolume2,
  FiVolumeX,
  FiSettings
} from 'react-icons/fi';
import { RiCapsuleLine, RiStethoscopeLine } from 'react-icons/ri';
import { MdTipsAndUpdates } from 'react-icons/md';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useState } from 'react';
import VoiceSettings from './VoiceSettings';

export default function Header({
  toggleSidebar,
  toggleDarkMode,
  darkMode,
  onProfileClick,
  onSymptomCheckerClick,
  onMedicalHistoryClick,
  onDrugInteractionsClick,
  onHealthTipsClick,
  onAnalyticsClick
}) {
  const { currentUser } = useAuth();
  const [notifications] = useState(3); // Mock notification count
  const [voiceInputEnabled, setVoiceInputEnabled] = useState(true);
  const [voiceOutputEnabled, setVoiceOutputEnabled] = useState(true);
  const [voiceSettingsOpen, setVoiceSettingsOpen] = useState(false);

  const navigationItems = [
    {
      label: 'Chat',
      icon: FiMessageCircle,
      onClick: () => window.location.reload(),
      color: 'from-blue-500 to-blue-600',
      description: 'AI Medical Chat'
    },
    {
      label: 'Symptoms',
      icon: RiStethoscopeLine,
      onClick: onSymptomCheckerClick,
      color: 'from-green-500 to-green-600',
      description: 'Check Symptoms'
    },
    {
      label: 'History',
      icon: FiBookOpen,
      onClick: onMedicalHistoryClick,
      color: 'from-purple-500 to-purple-600',
      description: 'Medical Records'
    },
    {
      label: 'Medications',
      icon: RiCapsuleLine,
      onClick: onDrugInteractionsClick,
      color: 'from-orange-500 to-orange-600',
      description: 'Drug Interactions'
    },
    {
      label: 'Health Tips',
      icon: MdTipsAndUpdates,
      onClick: onHealthTipsClick,
      color: 'from-pink-500 to-pink-600',
      description: 'Wellness Tips'
    },
    {
      label: 'Analytics',
      icon: FiBarChart,
      onClick: onAnalyticsClick,
      color: 'from-indigo-500 to-indigo-600',
      description: 'Health Analytics'
    }
  ];

  return (
    <motion.header
      role="banner"
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, type: 'spring' }}
      className="w-full px-4 sm:px-6 py-3 sm:py-4 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700
      flex justify-between items-center backdrop-blur-xl z-30 sticky top-0 shadow-sm"
    >
      {/* Logo + Name */}
      <motion.div
        className="flex items-center gap-3 select-none cursor-pointer"
        whileHover={{ scale: 1.02 }}
        onClick={() => window.location.reload()}
      >
        <motion.div
          className="rounded-xl w-10 h-10 flex items-center justify-center shadow-lg overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20"
          whileHover={{ rotate: 5, scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <img
            src="/logo.png"
            alt="MyDoc AI Logo"
            className="w-full h-full object-cover rounded-xl"
          />
        </motion.div>
        <div className="hidden sm:block">
          <h1 className="text-xl font-bold text-blue-600">
            MyDoc AI
          </h1>
          <p className="text-xs text-black dark:text-white -mt-1">Your Health Assistant</p>
        </div>
      </motion.div>

      {/* Enhanced Desktop Navigation */}
      <nav className="hidden xl:flex items-center gap-1">
        {navigationItems.map((item) => (
          <motion.button
            key={item.label}
            onClick={item.onClick}
            className="group relative flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gray-50 dark:bg-gray-800
            text-black dark:text-white hover:text-white transition-all duration-300 text-sm font-medium
            hover:shadow-lg overflow-hidden"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            {/* Gradient background on hover */}
            <motion.div
              className={`absolute inset-0 bg-gradient-to-r ${item.color} opacity-0 group-hover:opacity-100 transition-opacity duration-300`}
              initial={false}
            />

            {/* Icon with animation */}
            <motion.div
              className="relative z-10"
              whileHover={{ rotate: 5 }}
            >
              <item.icon size={16} />
            </motion.div>

            {/* Label */}
            <span className="relative z-10">{item.label}</span>

            {/* Tooltip */}
            <motion.div
              className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 bg-gray-900 dark:bg-gray-700 text-white text-xs px-2 py-1 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none whitespace-nowrap"
              initial={{ opacity: 0, y: -10 }}
              whileHover={{ opacity: 1, y: 0 }}
            >
              {item.description}
              <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900 dark:bg-gray-700 rotate-45"></div>
            </motion.div>
          </motion.button>
        ))}
      </nav>

      {/* Enhanced Controls */}
      <div className="flex items-center gap-2">
        {/* Voice Input Control */}
        <motion.button
          onClick={() => setVoiceInputEnabled(!voiceInputEnabled)}
          aria-label={`${voiceInputEnabled ? 'Disable' : 'Enable'} voice input`}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className={`p-2.5 rounded-xl transition-all duration-200 ${
            voiceInputEnabled
              ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-800/30'
              : 'bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
        >
          {voiceInputEnabled ? <FiMic size={18} /> : <FiMicOff size={18} />}
        </motion.button>

        {/* Voice Output Control */}
        <motion.button
          onClick={() => setVoiceOutputEnabled(!voiceOutputEnabled)}
          aria-label={`${voiceOutputEnabled ? 'Disable' : 'Enable'} voice output`}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className={`p-2.5 rounded-xl transition-all duration-200 ${
            voiceOutputEnabled
              ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-800/30'
              : 'bg-gray-50 dark:bg-gray-800 text-gray-400 dark:text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700'
          }`}
        >
          {voiceOutputEnabled ? <FiVolume2 size={18} /> : <FiVolumeX size={18} />}
        </motion.button>

        {/* Voice Settings */}
        <motion.button
          onClick={() => setVoiceSettingsOpen(true)}
          aria-label="Voice settings"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 text-gray-600 dark:text-gray-300 
          hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200"
        >
          <FiSettings size={18} />
        </motion.button>

        {/* Notifications */}
        <motion.button
          aria-label="Notifications"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="relative p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 text-black dark:text-white 
          hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200"
        >
          <img src="/bell.png" alt="Notifications" className="w-[18px] h-[18px]" />
          {notifications > 0 && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center font-bold"
            >
              {notifications}
            </motion.span>
          )}
        </motion.button>

        {/* Theme Toggle with enhanced animation */}
        <motion.button
          onClick={toggleDarkMode}
          aria-label="Toggle dark mode"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 text-black dark:text-white 
          hover:text-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 transition-all duration-200"
        >
          <AnimatePresence mode="wait">
            {darkMode ? (
              <motion.div
                key="sun"
                initial={{ rotate: -180, opacity: 0, scale: 0.5 }}
                animate={{ rotate: 0, opacity: 1, scale: 1 }}
                exit={{ rotate: 180, opacity: 0, scale: 0.5 }}
                transition={{ duration: 0.3 }}
              >
                <img src="/sun.png" alt="Light mode" className="w-[18px] h-[18px]" />
              </motion.div>
            ) : (
              <motion.div
                key="moon"
                initial={{ rotate: -180, opacity: 0, scale: 0.5 }}
                animate={{ rotate: 0, opacity: 1, scale: 1 }}
                exit={{ rotate: 180, opacity: 0, scale: 0.5 }}
                transition={{ duration: 0.3 }}
              >
                <img src="/moon.png" alt="Dark mode" className="w-[18px] h-[18px]" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>

        {/* Enhanced User Profile Button */}
        <motion.button
          onClick={onProfileClick}
          aria-label="User profile"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="flex items-center gap-2 px-3 py-2 rounded-xl bg-blue-50 dark:bg-blue-900/20
          text-black dark:text-white hover:bg-blue-100 dark:hover:bg-blue-800/30 
          transition-all duration-200 border border-blue-200 dark:border-blue-700"
        >
          <motion.div
            className="w-7 h-7 rounded-full flex items-center justify-center shadow-md bg-gradient-to-br from-blue-500 to-indigo-600"
            whileHover={{ rotate: 5 }}
          >
            <span className="text-xs font-bold text-white">
              {currentUser?.displayName ? currentUser.displayName.charAt(0).toUpperCase() :
                currentUser?.email ? currentUser.email.charAt(0).toUpperCase() : 'D'}
            </span>
          </motion.div>
          <div className="hidden sm:block text-left">
            <div className="text-sm font-medium">
              {currentUser?.displayName || 'Demo User'}
            </div>
            <div className="text-xs text-black dark:text-white -mt-0.5">
              Online
            </div>
          </div>
        </motion.button>

        {/* Mobile Menu Button */}
        <motion.button
          onClick={toggleSidebar}
          aria-label="Toggle menu"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="xl:hidden p-2.5 rounded-xl bg-gray-50 dark:bg-gray-800 text-black dark:text-white 
          hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all duration-200"
        >
          <GiHamburgerMenu size={18} />
        </motion.button>
      </div>

      {/* Voice Settings Modal */}
      <VoiceSettings
        isOpen={voiceSettingsOpen}
        onClose={() => setVoiceSettingsOpen(false)}
      />
    </motion.header>
  );
}
