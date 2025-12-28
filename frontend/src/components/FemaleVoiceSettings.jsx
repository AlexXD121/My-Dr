import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiX, FiPlay, FiPause, FiSettings, FiHeart, 
  FiUser, FiVolume2, FiMic, FiStar 
} from 'react-icons/fi';
import femaleVoiceService from '../services/femaleVoiceService';

/**
 * Female Voice Settings Component
 * Allows users to customize the female AI voice
 */
const FemaleVoiceSettings = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState({});
  const [availableVoices, setAvailableVoices] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [testingVoice, setTestingVoice] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
      loadAvailableVoices();
    }
  }, [isOpen]);

  const loadSettings = () => {
    const currentSettings = femaleVoiceService.getCurrentSettings();
    setSettings(currentSettings);
  };

  const loadAvailableVoices = () => {
    const voices = femaleVoiceService.getAvailableVoices();
    setAvailableVoices(voices);
  };

  const handleSettingChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    
    // Apply setting immediately
    switch (key) {
      case 'speed':
        femaleVoiceService.setSpeed(value);
        break;
      case 'pitch':
        femaleVoiceService.setPitch(value);
        break;
      case 'emotion':
        femaleVoiceService.setEmotion(value);
        break;
      case 'model':
        femaleVoiceService.setVoiceModel(value);
        break;
    }
  };

  const testVoice = async (voiceModel = null) => {
    if (isPlaying) {
      femaleVoiceService.stop();
      setIsPlaying(false);
      setTestingVoice(null);
      return;
    }

    try {
      setIsPlaying(true);
      setTestingVoice(voiceModel || settings.model);
      
      const result = await femaleVoiceService.testVoice(voiceModel);
      
      if (!result.success) {
        console.error('Voice test failed:', result.message);
      }
    } catch (error) {
      console.error('Voice test error:', error);
    } finally {
      setIsPlaying(false);
      setTestingVoice(null);
    }
  };

  const voicePersonalities = {
    jenny: {
      icon: FiHeart,
      color: 'pink',
      description: 'Warm and caring, perfect for medical consultations'
    },
    aria: {
      icon: FiUser,
      color: 'purple',
      description: 'Gentle and reassuring, ideal for health guidance'
    },
    maya: {
      icon: FiStar,
      color: 'blue',
      description: 'Intelligent and friendly, great for medical AI'
    }
  };

  const emotionSettings = [
    { value: 'caring', label: 'Caring & Warm', description: 'Empathetic and nurturing tone' },
    { value: 'professional', label: 'Professional', description: 'Clear and authoritative' },
    { value: 'friendly', label: 'Friendly', description: 'Approachable and cheerful' },
    { value: 'gentle', label: 'Gentle', description: 'Soft and soothing' }
  ];

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-purple-600 rounded-xl flex items-center justify-center">
                <FiMic className="text-white" size={20} />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Female Voice Settings
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Customize your AI medical assistant's voice
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              <FiX size={16} />
            </button>
          </div>

          <div className="p-6 space-y-8">
            {/* Voice Model Selection */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FiUser size={18} />
                Voice Personality
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {availableVoices.map((voice) => {
                  const personality = voicePersonalities[voice.id] || voicePersonalities.jenny;
                  const IconComponent = personality.icon;
                  const isSelected = settings.model === voice.id;
                  const isTesting = testingVoice === voice.id;

                  return (
                    <motion.div
                      key={voice.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        isSelected
                          ? `border-${personality.color}-500 bg-${personality.color}-50 dark:bg-${personality.color}-900/20`
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                      onClick={() => handleSettingChange('model', voice.id)}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className={`w-8 h-8 rounded-lg bg-${personality.color}-100 dark:bg-${personality.color}-900/30 flex items-center justify-center`}>
                          <IconComponent className={`text-${personality.color}-600 dark:text-${personality.color}-400`} size={16} />
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            testVoice(voice.id);
                          }}
                          className={`w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors ${
                            isTesting ? 'animate-pulse' : ''
                          }`}
                        >
                          {isTesting ? <FiPause size={14} /> : <FiPlay size={14} />}
                        </button>
                      </div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                        {voice.name}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {voice.description}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {voice.characteristics.map((char) => (
                          <span
                            key={char}
                            className={`px-2 py-1 text-xs rounded-full bg-${personality.color}-100 dark:bg-${personality.color}-900/30 text-${personality.color}-700 dark:text-${personality.color}-300`}
                          >
                            {char}
                          </span>
                        ))}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Emotion Settings */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FiHeart size={18} />
                Voice Emotion
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {emotionSettings.map((emotion) => (
                  <motion.button
                    key={emotion.value}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSettingChange('emotion', emotion.value)}
                    className={`p-4 rounded-xl border-2 text-left transition-all ${
                      settings.emotion === emotion.value
                        ? 'border-pink-500 bg-pink-50 dark:bg-pink-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <h4 className="font-medium text-gray-900 dark:text-white mb-1">
                      {emotion.label}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {emotion.description}
                    </p>
                  </motion.button>
                ))}
              </div>
            </div>

            {/* Voice Speed */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FiSettings size={18} />
                Speech Speed
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Slower</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {settings.speed?.toFixed(1)}x
                  </span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Faster</span>
                </div>
                <input
                  type="range"
                  min="0.5"
                  max="1.5"
                  step="0.1"
                  value={settings.speed || 0.9}
                  onChange={(e) => handleSettingChange('speed', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>0.5x</span>
                  <span>1.0x</span>
                  <span>1.5x</span>
                </div>
              </div>
            </div>

            {/* Voice Pitch */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FiVolume2 size={18} />
                Voice Pitch
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 dark:text-gray-400">Lower</span>
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {settings.pitch?.toFixed(1)}
                  </span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">Higher</span>
                </div>
                <input
                  type="range"
                  min="0.8"
                  max="1.4"
                  step="0.1"
                  value={settings.pitch || 1.1}
                  onChange={(e) => handleSettingChange('pitch', parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>0.8</span>
                  <span>1.0</span>
                  <span>1.4</span>
                </div>
              </div>
            </div>

            {/* Test Voice Button */}
            <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => testVoice()}
                disabled={isPlaying}
                className={`w-full py-3 px-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 ${
                  isPlaying
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700 text-white'
                }`}
              >
                {isPlaying ? (
                  <>
                    <FiPause size={18} />
                    Stop Voice Test
                  </>
                ) : (
                  <>
                    <FiPlay size={18} />
                    Test Current Voice
                  </>
                )}
              </motion.button>
            </div>

            {/* Voice Info */}
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4">
              <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                💡 Voice Tips
              </h4>
              <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                <li>• Jenny voice is optimized for medical consultations</li>
                <li>• Caring emotion adds warmth to health discussions</li>
                <li>• Slower speed (0.8-0.9x) is better for complex medical terms</li>
                <li>• Higher pitch (1.1-1.2) creates a more feminine, caring tone</li>
              </ul>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default FemaleVoiceSettings;