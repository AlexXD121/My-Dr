import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiX, FiToggleLeft, FiToggleRight, FiEye, FiType, 
  FiLayout, FiZap, FiSettings, FiInfo, FiCheck
} from 'react-icons/fi';

/**
 * Response Formatting Settings Component
 * Allows users to customize AI response formatting preferences
 */
const ResponseFormattingSettings = ({ isOpen, onClose, onSettingsChange }) => {
  const [settings, setSettings] = useState({
    enableFormatting: true,
    contextualFormatting: true,
    autoDetectContext: true,
    showSectionNavigation: true,
    highlightMedicalTerms: true,
    addVisualIcons: true,
    structuredLayout: true,
    showReadingTime: true,
    emergencyHighlighting: true,
    compactMode: false
  });

  const [previewText, setPreviewText] = useState('');

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('mydoc-formatting-settings');
    if (savedSettings) {
      const parsed = JSON.parse(savedSettings);
      setSettings(prev => ({ ...prev, ...parsed }));
    }
  }, []);

  useEffect(() => {
    // Save settings to localStorage
    localStorage.setItem('mydoc-formatting-settings', JSON.stringify(settings));
    
    // Notify parent component of changes
    onSettingsChange?.(settings);
  }, [settings, onSettingsChange]);

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const resetToDefaults = () => {
    const defaultSettings = {
      enableFormatting: true,
      contextualFormatting: true,
      autoDetectContext: true,
      showSectionNavigation: true,
      highlightMedicalTerms: true,
      addVisualIcons: true,
      structuredLayout: true,
      showReadingTime: true,
      emergencyHighlighting: true,
      compactMode: false
    };
    setSettings(defaultSettings);
  };

  const generatePreview = () => {
    const sampleText = `Based on your symptoms, you may have a common cold. Symptoms include runny nose, cough, and fatigue. Treatment options are rest, fluids, and over-the-counter medications. Prevention tips include washing hands frequently and avoiding close contact with sick individuals. Important: Seek medical attention if symptoms worsen or persist beyond 10 days.`;
    
    setPreviewText(sampleText);
  };

  const settingGroups = [
    {
      title: 'Core Formatting',
      icon: FiType,
      settings: [
        {
          key: 'enableFormatting',
          label: 'Enhanced Formatting',
          description: 'Apply advanced formatting to AI responses',
          type: 'toggle'
        },
        {
          key: 'contextualFormatting',
          label: 'Contextual Formatting',
          description: 'Format responses based on medical context',
          type: 'toggle',
          dependsOn: 'enableFormatting'
        },
        {
          key: 'autoDetectContext',
          label: 'Auto-Detect Context',
          description: 'Automatically identify medical topics',
          type: 'toggle',
          dependsOn: 'contextualFormatting'
        }
      ]
    },
    {
      title: 'Visual Enhancements',
      icon: FiEye,
      settings: [
        {
          key: 'showSectionNavigation',
          label: 'Section Navigation',
          description: 'Show quick navigation for response sections',
          type: 'toggle'
        },
        {
          key: 'highlightMedicalTerms',
          label: 'Highlight Medical Terms',
          description: 'Emphasize important medical terminology',
          type: 'toggle'
        },
        {
          key: 'addVisualIcons',
          label: 'Visual Icons',
          description: 'Add icons to different response sections',
          type: 'toggle'
        },
        {
          key: 'emergencyHighlighting',
          label: 'Emergency Highlighting',
          description: 'Special formatting for urgent information',
          type: 'toggle'
        }
      ]
    },
    {
      title: 'Layout Options',
      icon: FiLayout,
      settings: [
        {
          key: 'structuredLayout',
          label: 'Structured Layout',
          description: 'Organize content with headings and sections',
          type: 'toggle'
        },
        {
          key: 'showReadingTime',
          label: 'Reading Time',
          description: 'Display estimated reading time',
          type: 'toggle'
        },
        {
          key: 'compactMode',
          label: 'Compact Mode',
          description: 'Reduce spacing for denser layout',
          type: 'toggle'
        }
      ]
    }
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
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                <FiSettings className="text-white" size={20} />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Response Formatting Settings
                </h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Customize how AI responses are displayed and formatted
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

          <div className="flex h-[calc(90vh-120px)]">
            {/* Settings Panel */}
            <div className="flex-1 p-6 overflow-y-auto">
              <div className="space-y-8">
                {settingGroups.map((group) => {
                  const IconComponent = group.icon;
                  
                  return (
                    <motion.div
                      key={group.title}
                      className="space-y-4"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white flex items-center gap-2">
                        <IconComponent className="text-blue-500" size={18} />
                        {group.title}
                      </h3>
                      
                      <div className="space-y-3">
                        {group.settings.map((setting) => {
                          const isDisabled = setting.dependsOn && !settings[setting.dependsOn];
                          
                          return (
                            <motion.div
                              key={setting.key}
                              className={`p-4 rounded-xl border transition-all ${
                                isDisabled
                                  ? 'border-gray-200 dark:border-gray-700 opacity-50'
                                  : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600'
                              }`}
                              whileHover={!isDisabled ? { scale: 1.02 } : {}}
                            >
                              <div className="flex items-center justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-2">
                                    <h4 className="font-medium text-gray-900 dark:text-white">
                                      {setting.label}
                                    </h4>
                                    {setting.dependsOn && (
                                      <span className="text-xs text-gray-500 dark:text-gray-400">
                                        (requires {settingGroups
                                          .flatMap(g => g.settings)
                                          .find(s => s.key === setting.dependsOn)?.label})
                                      </span>
                                    )}
                                  </div>
                                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                    {setting.description}
                                  </p>
                                </div>
                                
                                <motion.button
                                  onClick={() => !isDisabled && handleSettingChange(setting.key, !settings[setting.key])}
                                  disabled={isDisabled}
                                  className={`ml-4 ${isDisabled ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                                  whileTap={!isDisabled ? { scale: 0.95 } : {}}
                                >
                                  {settings[setting.key] ? (
                                    <FiToggleRight 
                                      className={`text-2xl ${isDisabled ? 'text-gray-400' : 'text-blue-500'}`} 
                                    />
                                  ) : (
                                    <FiToggleLeft 
                                      className={`text-2xl ${isDisabled ? 'text-gray-400' : 'text-gray-400'}`} 
                                    />
                                  )}
                                </motion.button>
                              </div>
                            </motion.div>
                          );
                        })}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Preview Panel */}
            <div className="w-1/2 border-l border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900">
              <div className="h-full flex flex-col">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Preview
                  </h3>
                  <button
                    onClick={generatePreview}
                    className="flex items-center gap-2 px-3 py-2 text-sm bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    <FiZap size={14} />
                    Generate Preview
                  </button>
                </div>
                
                <div className="flex-1 bg-white dark:bg-gray-800 rounded-xl p-4 overflow-y-auto">
                  {previewText ? (
                    <div className="space-y-4">
                      <div className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                        Sample AI response with current formatting settings:
                      </div>
                      
                      {/* Preview would show formatted response here */}
                      <div className="prose prose-sm dark:prose-invert max-w-none">
                        {settings.enableFormatting ? (
                          <div>
                            {settings.addVisualIcons && <span className="text-lg">🩺</span>}
                            <h3 className={settings.structuredLayout ? "font-semibold text-blue-600 dark:text-blue-400" : ""}>
                              Medical Assessment
                            </h3>
                            <p>
                              Based on your {settings.highlightMedicalTerms ? <strong>symptoms</strong> : 'symptoms'}, 
                              you may have a common cold.
                            </p>
                            
                            {settings.structuredLayout && (
                              <>
                                <h4 className="font-medium mt-4 mb-2">
                                  {settings.addVisualIcons && '🔍 '}Symptoms
                                </h4>
                                <ul className="list-disc list-inside">
                                  <li>Runny nose</li>
                                  <li>Cough</li>
                                  <li>Fatigue</li>
                                </ul>
                              </>
                            )}
                            
                            {settings.emergencyHighlighting && (
                              <div className="mt-4 p-3 bg-orange-50 dark:bg-orange-900/20 border-l-4 border-orange-500 rounded">
                                <strong>⚠️ Important:</strong> Seek medical attention if symptoms worsen.
                              </div>
                            )}
                            
                            {settings.showReadingTime && (
                              <div className="text-xs text-gray-500 mt-4">
                                📖 Estimated reading time: 1 minute
                              </div>
                            )}
                          </div>
                        ) : (
                          <p className="text-gray-600 dark:text-gray-400">
                            {previewText}
                          </p>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
                      <div className="text-center">
                        <FiEye size={48} className="mx-auto mb-4 opacity-50" />
                        <p>Click "Generate Preview" to see how your settings affect response formatting</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
              <FiInfo size={16} />
              <span>Settings are automatically saved</span>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={resetToDefaults}
                className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors"
              >
                Reset to Defaults
              </button>
              
              <motion.button
                onClick={onClose}
                className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <FiCheck size={16} />
                Done
              </motion.button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ResponseFormattingSettings;