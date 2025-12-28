import * as FiIcons from 'react-icons/fi';
import * as MdIcons from 'react-icons/md';
import * as RiIcons from 'react-icons/ri';
import * as HiIcons from 'react-icons/hi2';
import { motion } from 'framer-motion';

// Centralized icon mapping
const iconMap = {
  // Medical icons
  stethoscope: MdIcons.MdLocalHospital,
  pill: RiIcons.RiCapsuleLine,
  heart: FiIcons.FiHeart,
  activity: FiIcons.FiActivity,
  thermometer: MdIcons.MdThermostat,
  syringe: MdIcons.MdVaccines,
  bandage: MdIcons.MdHealing,
  microscope: MdIcons.MdScience,
  ambulance: MdIcons.MdLocalHospital,
  
  // UI icons
  menu: FiIcons.FiMenu,
  close: FiIcons.FiX,
  settings: FiIcons.FiSettings,
  user: FiIcons.FiUser,
  search: FiIcons.FiSearch,
  filter: FiIcons.FiFilter,
  
  // Actions
  send: FiIcons.FiSend,
  mic: FiIcons.FiMic,
  micOff: FiIcons.FiMicOff,
  play: FiIcons.FiPlay,
  pause: FiIcons.FiPause,
  stop: FiIcons.FiSquare,
  
  // Navigation
  home: FiIcons.FiHome,
  back: FiIcons.FiArrowLeft,
  forward: FiIcons.FiArrowRight,
  up: FiIcons.FiArrowUp,
  down: FiIcons.FiArrowDown,
  
  // Status
  check: FiIcons.FiCheck,
  checkCircle: FiIcons.FiCheckCircle,
  alert: FiIcons.FiAlertTriangle,
  alertCircle: FiIcons.FiAlertCircle,
  info: FiIcons.FiInfo,
  warning: HiIcons.HiExclamationTriangle,
  error: HiIcons.HiXCircle,
  
  // Data
  chart: FiIcons.FiBarChart,
  pieChart: FiIcons.FiPieChart,
  trendUp: FiIcons.FiTrendingUp,
  trendDown: FiIcons.FiTrendingDown,
  
  // Files
  file: FiIcons.FiFile,
  fileText: FiIcons.FiFileText,
  download: FiIcons.FiDownload,
  upload: FiIcons.FiUpload,
  
  // Communication
  mail: FiIcons.FiMail,
  phone: FiIcons.FiPhone,
  message: FiIcons.FiMessageSquare,
  
  // Time
  clock: FiIcons.FiClock,
  calendar: FiIcons.FiCalendar,
  
  // Theme
  sun: FiIcons.FiSun,
  moon: FiIcons.FiMoon,
  
  // Accessibility
  eye: FiIcons.FiEye,
  eyeOff: FiIcons.FiEyeOff,
  volume: FiIcons.FiVolume2,
  volumeOff: FiIcons.FiVolumeX,
};

export const Icon = ({ 
  name, 
  size = 20, 
  className = '', 
  medical = false,
  animated = false,
  color,
  ...props 
}) => {
  const IconComponent = iconMap[name];
  
  if (!IconComponent) {
    console.warn(`Icon "${name}" not found in iconMap`);
    return null;
  }
  
  const iconElement = (
    <IconComponent
      size={size}
      className={`
        ${className}
        ${medical ? 'text-medical-600 dark:text-medical-400' : ''}
        ${color ? `text-${color}` : ''}
        transition-colors duration-200
      `}
      {...props}
    />
  );
  
  if (animated) {
    return (
      <motion.span
        animate={{ 
          scale: [1, 1.1, 1],
          rotate: name === 'settings' ? [0, 180, 360] : 0
        }}
        transition={{ 
          duration: 2, 
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="inline-block"
      >
        {iconElement}
      </motion.span>
    );
  }
  
  return iconElement;
};

// Medical emoji icons for visual appeal
export const MedicalEmoji = ({ type, size = 24, animated = false, className = '' }) => {
  const emojis = {
    stethoscope: '🩺',
    pill: '💊',
    heart: '❤️',
    brain: '🧠',
    thermometer: '🌡️',
    syringe: '💉',
    bandage: '🩹',
    microscope: '🔬',
    dna: '🧬',
    ambulance: '🚑',
    hospital: '🏥',
    doctor: '👨‍⚕️',
    nurse: '👩‍⚕️',
    mask: '😷',
    tooth: '🦷',
    bone: '🦴',
    lungs: '🫁',
    stomach: '🫃',
  };
  
  const sizeClass = {
    16: 'text-sm',
    20: 'text-base',
    24: 'text-lg',
    32: 'text-xl',
    40: 'text-2xl',
    48: 'text-3xl',
  }[size] || 'text-lg';
  
  const emoji = emojis[type] || '🏥';
  
  if (animated) {
    return (
      <motion.span
        className={`inline-block ${sizeClass} ${className}`}
        animate={{ 
          scale: [1, 1.1, 1],
          rotate: [0, 5, -5, 0]
        }}
        transition={{ 
          duration: 2, 
          repeat: Infinity,
          ease: "easeInOut"
        }}
      >
        {emoji}
      </motion.span>
    );
  }
  
  return (
    <span className={`inline-block ${sizeClass} ${className}`}>
      {emoji}
    </span>
  );
};

export default Icon;