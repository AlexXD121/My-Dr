
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiMic, FiVolume2, FiSettings, FiPlay, FiPause, FiRefreshCw } from 'react-icons/fi';
import speechService from '../services/speechService';
import useSpeechRecognition from '../hooks/useSpeechRecognition';
import useTextToSpeech from '../hooks/useTextToSpeech';

/**
 * Voice Settings Component
 * Provides comprehensive voice configuration and testing interface
 */
const VoiceSettings = ({ isOpen, onClose }) => {
  const [settings, setSettings] = useState({});
  const [availableVoices, setAvailableVoices] = useState([]);
  const [isTestingRecognition, setIsTestingRecognition] = useState(false);
  const [isTestingSynthesis, setIsTestingSynthesis] = useState(false);
  const [testResults, setTestResults] = useState({});
  const [activeTab, setActiveTab] = useState('recognition');

  const { 
    isSupported: recognitionSupported,
    testRecognition,
    getVoiceCommands
  } = useSpeechRecognition();

  const {
    isSupported: synthesisSupported,
    testSpeech,
    changeVoice,
    updateSettings: updateSpeechSettings
  } = useTextToSpeech();

  // Load settings and voices on mount
  useEffect(() => {
    if (isOpen) {
      loadSettings();
      loadVoices();
    }
  }, [isOpen]);

  // Load current settings
  const loadSettings = () => {
    const currentSettings = speechService.getSettings();
    setSettings(currentSettings);
  };

  // Load available voices
  const loadVoices = () => {
    const voices = speechService.getAvailableVoices();
    setAvailableVoices(voices);
  };

  // Update setting
  const updateSetting = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    speechService.updateSettings(newSettings);
    updateSpeechSettings(newSettings);
  };

  // Test speech recognition
  const handleTestRecognition = async () => {
    setIsTestingRecognition(true);
    setTestResults(prev => ({ ...prev, recognition: null }));

    try {
      const result = await testRecognition();
      setTestResults(prev => ({
        ...prev,
        recognition: {
          success: result.success,
          message: result.success ? `Recognized: "${result.result}"` : result.error,
          timestamp: Date.now()
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        recognition: {
          success: false,
          message: error.message,
          timestamp: Date.now()
        }
      }));
    } finally {
      setIsTestingRecognition(false);
    }
  };

  // Test speech synthesis
  const handleTestSynthesis = async () => {
    setIsTestingSynthesis(true);
    setTestResults(prev => ({ ...prev, synthesis: null }));

    const testText = "Hello! This is a test of the speech synthesis system. I can help you with medical questions and provide voice responses.";

    try {
      const result = await testSpeech(testText);
      setTestResults(prev => ({
        ...prev,
        synthesis: {
          success: result.success,
          message: result.success ? "Speech synthesis test completed successfully" : result.error,
          timestamp: Date.now()
        }
      }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        synthesis: {
          success: false,
          message: error.message,
          timestamp: Date.now()
        }
      }));
    } finally {
      setIsTestingSynthesis(false);
    }
  };

  // Get voice commands list
  const voiceCommands = getVoiceCommands();

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[8000] flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <FiMic className="text-white text-lg" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  Voice Settings
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Configure speech recognition and synthesis
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-700 flex items-center justify-center hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {[
            { id: 'recognition', label: 'Speech Recognition', icon: FiMic },
            { id: 'synthesis', label: 'Text-to-Speech', icon: FiVolume2 },
            { id: 'commands', label: 'Voice Commands', icon: FiSettings }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {/* Speech Recognition Tab */}
          {activeTab === 'recognition' && (
            <div className="space-y-6">
              {/* Support Status */}
              <div className="flex items-center gap-3 p-4 rounded-lg bg-gray-50 dark:bg-gray-700">
                <div className={`w-3 h-3 rounded-full ${recognitionSupported ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm font-medium">
                  Speech Recognition: {recognitionSupported ? 'Supported' : 'Not Supported'}
                </span>
              </div>

              {recognitionSupported && (
                <>
                  {/* Language Setting */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Language
                    </label>
                    <select
                      value={settings.language || 'en-US'}
                      onChange={(e) => updateSetting('language', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="en-US">English (US)</option>
                      <option value="en-GB">English (UK)</option>
                      <option value="en-AU">English (Australia)</option>
                      <option value="en-CA">English (Canada)</option>
                      <option value="es-ES">Spanish (Spain)</option>
                      <option value="es-MX">Spanish (Mexico)</option>
                      <option value="fr-FR">French (France)</option>
                      <option value="de-DE">German (Germany)</option>
                    </select>
                  </div>

                  {/* Recognition Settings */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Medical Terms Recognition
                      </label>
                      <button
                        onClick={() => updateSetting('medicalTermsEnabled', !settings.medicalTermsEnabled)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.medicalTermsEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                          settings.medicalTermsEnabled ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Voice Commands
                      </label>
                      <button
                        onClick={() => updateSetting('commandsEnabled', !settings.commandsEnabled)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.commandsEnabled ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                          settings.commandsEnabled ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Continuous Listening
                      </label>
                      <button
                        onClick={() => updateSetting('continuous', !settings.continuous)}
                        className={`w-12 h-6 rounded-full transition-colors ${
                          settings.continuous ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                        }`}
                      >
                        <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                          settings.continuous ? 'translate-x-6' : 'translate-x-0.5'
                        }`} />
                      </button>
                    </div>
                  </div>

                  {/* Test Recognition */}
                  <div>
                    <button
                      onClick={handleTestRecognition}
                      disabled={isTestingRecognition}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isTestingRecognition ? (
                        <>
                          <FiRefreshCw className="animate-spin" size={16} />
                          Testing...
                        </>
                      ) : (
                        <>
                          <FiPlay size={16} />
                          Test Recognition
                        </>
                      )}
                    </button>

                    {testResults.recognition && (
                      <div className={`mt-3 p-3 rounded-lg ${
                        testResults.recognition.success 
                          ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                          : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                      }`}>
                        {testResults.recognition.message}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          )}

          {/* Text-to-Speech Tab */}
          {activeTab === 'synthesis' && (
            <div className="space-y-6">
              {/* Support Status */}
              <div className="flex items-center gap-3 p-4 rounded-lg bg-gray-50 dark:bg-gray-700">
                <div className={`w-3 h-3 rounded-full ${synthesisSupported ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm font-medium">
                  Text-to-Speech: {synthesisSupported ? 'Supported' : 'Not Supported'}
                </span>
              </div>

              {synthesisSupported && (
                <>
                  {/* Voice Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Voice
                    </label>
                    <select
                      value={settings.preferredVoice || ''}
                      onChange={(e) => {
                        updateSetting('preferredVoice', e.target.value);
                        changeVoice(e.target.value);
                      }}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="">Default Voice</option>
                      {availableVoices.map(voice => (
                        <option key={voice.name} value={voice.name}>
                          {voice.name} ({voice.lang})
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Voice Controls */}
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Speed: {settings.voiceSpeed || 0.9}
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="2"
                        step="0.1"
                        value={settings.voiceSpeed || 0.9}
                        onChange={(e) => updateSetting('voiceSpeed', parseFloat(e.target.value))}
                        className="w-full"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Pitch: {settings.voicePitch || 1.0}
                      </label>
                      <input
                        type="range"
                        min="0.5"
                        max="2"
                        step="0.1"
                        value={settings.voicePitch || 1.0}
                        onChange={(e) => updateSetting('voicePitch', parseFloat(e.target.value))}
                        className="w-full"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Volume: {settings.voiceVolume || 1.0}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        value={settings.voiceVolume || 1.0}
                        onChange={(e) => updateSetting('voiceVolume', parseFloat(e.target.value))}
                        className="w-full"
                      />
                    </div>
                  </div>

                  {/* Auto-speak Setting */}
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      Auto-speak AI Responses
                    </label>
                    <button
                      onClick={() => updateSetting('autoSpeak', !settings.autoSpeak)}
                      className={`w-12 h-6 rounded-full transition-colors ${
                        settings.autoSpeak ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    >
                      <div className={`w-5 h-5 bg-white rounded-full shadow-md transform transition-transform ${
                        settings.autoSpeak ? 'translate-x-6' : 'translate-x-0.5'
                      }`} />
                    </button>
                  </div>

                  {/* Test Synthesis */}
                  <div>
                    <button
                      onClick={handleTestSynthesis}
                      disabled={isTestingSynthesis}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isTestingSynthesis ? (
                        <>
                          <FiRefreshCw className="animate-spin" size={16} />
                          Testing...
                        </>
                      ) : (
                        <>
                          <FiPlay size={16} />
                          Test Voice
                        </>
                      )}
                    </button>

                    {testResults.synthesis && (
                      <div className={`mt-3 p-3 rounded-lg ${
                        testResults.synthesis.success 
                          ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200'
                          : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200'
                      }`}>
                        {testResults.synthesis.message}
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          )}

          {/* Voice Commands Tab */}
          {activeTab === 'commands' && (
            <div className="space-y-6">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Available voice commands for hands-free navigation:
              </div>

              <div className="grid gap-4">
                {voiceCommands.map((cmd, index) => (
                  <div key={index} className="p-4 rounded-lg bg-gray-50 dark:bg-gray-700">
                    <div className="font-medium text-gray-900 dark:text-white">
                      "{cmd.command}"
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {cmd.description}
                    </div>
                  </div>
                ))}
              </div>

              <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                <div className="text-sm text-blue-800 dark:text-blue-200">
                  <strong>Tip:</strong> Speak clearly and wait for the microphone to activate. 
                  Voice commands work best in quiet environments.
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Voice features enhance accessibility and hands-free interaction
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

export default VoiceSettings;