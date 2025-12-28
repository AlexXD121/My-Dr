import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX, FiPlus, FiActivity, FiClock, FiMapPin, FiAlertTriangle, FiCheckCircle, FiArrowLeft, FiArrowRight } from 'react-icons/fi';
import apiService from '../services/api';

const SymptomChecker = ({ isOpen, onClose, darkMode }) => {
  // Multi-step form state
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [error, setError] = useState(null);

  // Symptom form data
  const [formData, setFormData] = useState({
    symptoms: [],
    newSymptom: '',
    duration: '',
    severityRating: 5,
    location: '',
    triggers: [],
    alleviatingFactors: [],
    associatedSymptoms: [],
    selectedBodyPart: null
  });

  // Body diagram state
  const [hoveredBodyPart, setHoveredBodyPart] = useState(null);

  // Common symptoms for quick selection
  const commonSymptoms = [
    'Headache', 'Fever', 'Cough', 'Sore throat', 'Fatigue', 'Nausea',
    'Chest pain', 'Shortness of breath', 'Dizziness', 'Back pain',
    'Joint pain', 'Muscle aches', 'Stomach pain', 'Diarrhea', 'Vomiting'
  ];

  // Duration options
  const durationOptions = [
    'Less than 1 hour', '1-6 hours', '6-24 hours', '1-3 days',
    '3-7 days', '1-2 weeks', '2-4 weeks', 'More than 1 month'
  ];

  // Body parts for diagram
  const bodyParts = [
    { id: 'head', name: 'Head', x: 50, y: 15, symptoms: ['Headache', 'Dizziness', 'Vision problems'] },
    { id: 'neck', name: 'Neck', x: 50, y: 25, symptoms: ['Neck pain', 'Stiff neck', 'Sore throat'] },
    { id: 'chest', name: 'Chest', x: 50, y: 40, symptoms: ['Chest pain', 'Shortness of breath', 'Heart palpitations'] },
    { id: 'abdomen', name: 'Abdomen', x: 50, y: 55, symptoms: ['Stomach pain', 'Nausea', 'Bloating'] },
    { id: 'back', name: 'Back', x: 50, y: 45, symptoms: ['Back pain', 'Muscle spasms', 'Stiffness'] },
    { id: 'left_arm', name: 'Left Arm', x: 25, y: 40, symptoms: ['Arm pain', 'Numbness', 'Weakness'] },
    { id: 'right_arm', name: 'Right Arm', x: 75, y: 40, symptoms: ['Arm pain', 'Numbness', 'Weakness'] },
    { id: 'left_leg', name: 'Left Leg', x: 40, y: 75, symptoms: ['Leg pain', 'Swelling', 'Cramps'] },
    { id: 'right_leg', name: 'Right Leg', x: 60, y: 75, symptoms: ['Leg pain', 'Swelling', 'Cramps'] }
  ];

  // Urgency level colors and descriptions
  const urgencyLevels = {
    routine: {
      color: 'bg-emerald-500',
      bgColor: 'bg-emerald-50 dark:bg-emerald-900/20',
      borderColor: 'border-emerald-200 dark:border-emerald-700',
      textColor: 'text-emerald-800 dark:text-emerald-200',
      text: 'Routine',
      description: 'Can wait for regular appointment'
    },
    moderate: {
      color: 'bg-yellow-500',
      bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
      borderColor: 'border-yellow-200 dark:border-yellow-700',
      textColor: 'text-yellow-800 dark:text-yellow-200',
      text: 'Moderate',
      description: 'Should see doctor within days'
    },
    urgent: {
      color: 'bg-orange-500',
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
      borderColor: 'border-orange-200 dark:border-orange-700',
      textColor: 'text-orange-800 dark:text-orange-200',
      text: 'Urgent',
      description: 'Should see doctor within hours'
    },
    emergency: {
      color: 'bg-red-500',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      borderColor: 'border-red-200 dark:border-red-700',
      textColor: 'text-red-800 dark:text-red-200',
      text: 'Emergency',
      description: 'Seek immediate medical attention'
    },
    critical: {
      color: 'bg-red-700',
      bgColor: 'bg-red-50 dark:bg-red-900/20',
      borderColor: 'border-red-200 dark:border-red-700',
      textColor: 'text-red-800 dark:text-red-200',
      text: 'Critical',
      description: 'Call emergency services immediately'
    }
  };

  // Add symptom to list
  const addSymptom = useCallback((symptom) => {
    if (symptom && !formData.symptoms.includes(symptom)) {
      setFormData(prev => ({
        ...prev,
        symptoms: [...prev.symptoms, symptom],
        newSymptom: ''
      }));
    }
  }, [formData.symptoms]);

  // Remove symptom from list
  const removeSymptom = useCallback((symptom) => {
    setFormData(prev => ({
      ...prev,
      symptoms: prev.symptoms.filter(s => s !== symptom)
    }));
  }, []);

  // Handle body part selection
  const handleBodyPartClick = useCallback((bodyPart) => {
    setFormData(prev => ({
      ...prev,
      selectedBodyPart: bodyPart.id,
      location: bodyPart.name
    }));
  }, []);

  // Handle form input changes
  const handleInputChange = useCallback((field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  // Analyze symptoms
  const analyzeSymptoms = async () => {
    if (formData.symptoms.length === 0) {
      setError('Please add at least one symptom');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const requestData = {
        symptoms: formData.symptoms,
        duration: formData.duration || null,
        severity_rating: formData.severityRating,
        location: formData.location || null,
        triggers: formData.triggers,
        alleviating_factors: formData.alleviatingFactors,
        associated_symptoms: formData.associatedSymptoms
      };

      console.log('Sending symptom analysis request:', requestData);

      const response = await apiService.post('/symptoms/analyze', requestData);
      console.log('Received symptom analysis response:', response);

      setAnalysis(response);
      setCurrentStep(4); // Move to results step
    } catch (err) {
      console.error('Symptom analysis error:', err);
      setError(err.message || 'Failed to analyze symptoms. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      symptoms: [],
      newSymptom: '',
      duration: '',
      severityRating: 5,
      location: '',
      triggers: [],
      alleviatingFactors: [],
      associatedSymptoms: [],
      selectedBodyPart: null
    });
    setAnalysis(null);
    setError(null);
    setCurrentStep(1);
  };

  // Handle step navigation
  const nextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    } else {
      analyzeSymptoms();
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Render urgency indicator
  const renderUrgencyIndicator = (urgencyLevel, urgencyScore) => {
    const level = urgencyLevels[urgencyLevel] || urgencyLevels.moderate;

    return (
      <div className={`p-6 rounded-2xl border ${level.bgColor} ${level.borderColor} mb-6`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${level.color}`} />
            <span className={`text-lg font-semibold ${level.textColor}`}>
              Urgency Level: {level.text}
            </span>
          </div>
          <span className={`px-4 py-2 rounded-full text-white text-sm font-medium ${level.color}`}>
            {urgencyScore}/10
          </span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-3">
          <div
            className={`h-3 rounded-full ${level.color} transition-all duration-500`}
            style={{ width: `${(urgencyScore / 10) * 100}%` }}
          />
        </div>
        <p className={`text-sm ${level.textColor}`}>
          {level.description}
        </p>
      </div>
    );
  };

  // Render body diagram
  const renderBodyDiagram = () => (
    <div className="relative">
      <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
        <FiMapPin className="inline w-5 h-5 mr-2" />
        Select affected body area (optional)
      </h3>
      <div className="relative mx-auto w-64 h-96 bg-gradient-to-b from-blue-50 to-indigo-100 dark:from-gray-800 dark:to-gray-700 rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-600 shadow-lg">
        {/* Simple body outline */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100">
          {/* Head */}
          <circle
            cx="50" cy="15" r="8"
            fill={formData.selectedBodyPart === 'head' ? '#3B82F6' : '#E5E7EB'}
            stroke="#374151" strokeWidth="1"
            className="cursor-pointer hover:fill-blue-400 transition-all duration-200 drop-shadow-sm"
            onClick={() => handleBodyPartClick(bodyParts.find(p => p.id === 'head'))}
            onMouseEnter={() => setHoveredBodyPart('head')}
            onMouseLeave={() => setHoveredBodyPart(null)}
          />

          {/* Neck */}
          <rect
            x="47" y="23" width="6" height="8" rx="2"
            fill={formData.selectedBodyPart === 'neck' ? '#3B82F6' : '#E5E7EB'}
            stroke="#374151" strokeWidth="1"
            className="cursor-pointer hover:fill-blue-400 transition-all duration-200 drop-shadow-sm"
            onClick={() => handleBodyPartClick(bodyParts.find(p => p.id === 'neck'))}
            onMouseEnter={() => setHoveredBodyPart('neck')}
            onMouseLeave={() => setHoveredBodyPart(null)}
          />

          {/* Torso */}
          <rect
            x="40" y="31" width="20" height="30" rx="4"
            fill={formData.selectedBodyPart === 'chest' ? '#3B82F6' : '#E5E7EB'}
            stroke="#374151" strokeWidth="1"
            className="cursor-pointer hover:fill-blue-400 transition-all duration-200 drop-shadow-sm"
            onClick={() => handleBodyPartClick(bodyParts.find(p => p.id === 'chest'))}
            onMouseEnter={() => setHoveredBodyPart('chest')}
            onMouseLeave={() => setHoveredBodyPart(null)}
          />

          {/* Arms */}
          <rect
            x="25" y="35" width="12" height="20" rx="6"
            fill={formData.selectedBodyPart === 'left_arm' ? '#3B82F6' : '#E5E7EB'}
            stroke="#374151" strokeWidth="1"
            className="cursor-pointer hover:fill-blue-400 transition-all duration-200 drop-shadow-sm"
            onClick={() => handleBodyPartClick(bodyParts.find(p => p.id === 'left_arm'))}
            onMouseEnter={() => setHoveredBodyPart('left_arm')}
            onMouseLeave={() => setHoveredBodyPart(null)}
          />
          <rect
            x="63" y="35" width="12" height="20" rx="6"
            fill={formData.selectedBodyPart === 'right_arm' ? '#3B82F6' : '#E5E7EB'}
            stroke="#374151" strokeWidth="1"
            className="cursor-pointer hover:fill-blue-400 transition-all duration-200 drop-shadow-sm"
            onClick={() => handleBodyPartClick(bodyParts.find(p => p.id === 'right_arm'))}
            onMouseEnter={() => setHoveredBodyPart('right_arm')}
            onMouseLeave={() => setHoveredBodyPart(null)}
          />

          {/* Legs */}
          <rect
            x="42" y="65" width="6" height="25" rx="3"
            fill={formData.selectedBodyPart === 'left_leg' ? '#3B82F6' : '#E5E7EB'}
            stroke="#374151" strokeWidth="1"
            className="cursor-pointer hover:fill-blue-400 transition-all duration-200 drop-shadow-sm"
            onClick={() => handleBodyPartClick(bodyParts.find(p => p.id === 'left_leg'))}
            onMouseEnter={() => setHoveredBodyPart('left_leg')}
            onMouseLeave={() => setHoveredBodyPart(null)}
          />
          <rect
            x="52" y="65" width="6" height="25" rx="3"
            fill={formData.selectedBodyPart === 'right_leg' ? '#3B82F6' : '#E5E7EB'}
            stroke="#374151" strokeWidth="1"
            className="cursor-pointer hover:fill-blue-400 transition-all duration-200 drop-shadow-sm"
            onClick={() => handleBodyPartClick(bodyParts.find(p => p.id === 'right_leg'))}
            onMouseEnter={() => setHoveredBodyPart('right_leg')}
            onMouseLeave={() => setHoveredBodyPart(null)}
          />
        </svg>

        {/* Hover tooltip */}
        {hoveredBodyPart && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute top-4 left-4 bg-black/80 backdrop-blur-sm text-white text-xs px-3 py-2 rounded-lg shadow-lg"
          >
            {bodyParts.find(p => p.id === hoveredBodyPart)?.name}
          </motion.div>
        )}
      </div>

      {formData.selectedBodyPart && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-4 p-4 rounded-xl border ${darkMode ? 'bg-blue-900/20 border-blue-700' : 'bg-blue-50 border-blue-200'}`}
        >
          <p className={`text-sm ${darkMode ? 'text-blue-200' : 'text-blue-800'}`}>
            <FiCheckCircle className="inline w-4 h-4 mr-2" />
            Selected: <strong>{bodyParts.find(p => p.id === formData.selectedBodyPart)?.name}</strong>
          </p>
        </motion.div>
      )}
    </div>
  );

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`flex-1 ${darkMode ? 'bg-gray-900/95' : 'bg-white/95'} backdrop-blur-sm overflow-y-auto`}
    >
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
              <FiActivity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                Symptom Checker
              </h1>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                AI-powered health assessment tool
              </p>
            </div>
          </div>

        </div>

        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex items-center">
                <motion.div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 ${step <= currentStep
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg'
                      : darkMode ? 'bg-gray-700 text-gray-400 border border-gray-600' : 'bg-gray-200 text-gray-600 border border-gray-300'
                    }`}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {step <= currentStep ? <FiCheckCircle className="w-5 h-5" /> : step}
                </motion.div>
                {step < 4 && (
                  <div className={`w-16 h-1 mx-3 rounded-full transition-all duration-300 ${step < currentStep
                      ? 'bg-gradient-to-r from-blue-500 to-indigo-600'
                      : darkMode ? 'bg-gray-700' : 'bg-gray-200'
                    }`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-4">
            <span className={`text-sm font-medium px-4 py-2 rounded-full ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-600'}`}>
              {currentStep === 1 && 'Describe Symptoms'}
              {currentStep === 2 && 'Symptom Details'}
              {currentStep === 3 && 'Additional Information'}
              {currentStep === 4 && 'Analysis Results'}
            </span>
          </div>
        </div>

        {/* Error display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-200 rounded-xl shadow-lg"
          >
            <div className="flex items-center space-x-2">
              <FiAlertTriangle className="w-5 h-5" />
              <p className="font-medium">Error:</p>
            </div>
            <p className="mt-1">{error}</p>
          </motion.div>
        )}

        <AnimatePresence mode="wait">
          {/* Step 1: Symptom Input */}
          {currentStep === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-8"
            >
              <div className="grid lg:grid-cols-2 gap-8">
                <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-gray-200'} backdrop-blur-sm shadow-xl`}>
                  <h2 className={`text-xl font-semibold mb-6 ${darkMode ? 'text-white' : 'text-gray-800'} flex items-center`}>
                    <FiActivity className="w-5 h-5 mr-2 text-blue-500" />
                    What symptoms are you experiencing?
                  </h2>

                  {/* Manual symptom input */}
                  <div className="mb-6">
                    <div className="flex space-x-3">
                      <input
                        type="text"
                        value={formData.newSymptom}
                        onChange={(e) => handleInputChange('newSymptom', e.target.value)}
                        placeholder="Type a symptom..."
                        className={`flex-1 p-4 rounded-xl border transition-all duration-200 ${darkMode
                            ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                            : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                          }`}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            addSymptom(formData.newSymptom);
                          }
                        }}
                      />
                      <button
                        onClick={() => addSymptom(formData.newSymptom)}
                        disabled={!formData.newSymptom.trim()}
                        className="px-6 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl"
                      >
                        <FiPlus className="w-5 h-5" />
                      </button>
                    </div>
                  </div>

                  {/* Common symptoms */}
                  <div className="mb-6">
                    <p className={`text-sm font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Or select from common symptoms:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {commonSymptoms.map((symptom) => (
                        <motion.button
                          key={symptom}
                          onClick={() => addSymptom(symptom)}
                          disabled={formData.symptoms.includes(symptom)}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          className={`px-4 py-2 text-sm rounded-xl border transition-all duration-200 ${formData.symptoms.includes(symptom)
                              ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700 text-blue-700 dark:text-blue-300 cursor-not-allowed'
                              : darkMode
                                ? 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600 hover:border-gray-500'
                                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-gray-400 shadow-sm hover:shadow-md'
                            }`}
                        >
                          {symptom}
                        </motion.button>
                      ))}
                    </div>
                  </div>

                  {/* Selected symptoms */}
                  {formData.symptoms.length > 0 && (
                    <div>
                      <p className={`text-sm font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        Selected symptoms ({formData.symptoms.length}):
                      </p>
                      <div className="space-y-2">
                        {formData.symptoms.map((symptom, index) => (
                          <motion.div
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: 10 }}
                            className={`flex items-center justify-between p-3 rounded-xl ${darkMode ? 'bg-gray-700 border border-gray-600' : 'bg-gray-50 border border-gray-200'
                              } shadow-sm`}
                          >
                            <span className={`${darkMode ? 'text-white' : 'text-gray-800'} font-medium`}>
                              {symptom}
                            </span>
                            <button
                              onClick={() => removeSymptom(symptom)}
                              className="p-1 text-red-500 hover:text-red-700 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all duration-200"
                            >
                              <FiX className="w-4 h-4" />
                            </button>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Body diagram */}
                <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-gray-200'} backdrop-blur-sm shadow-xl`}>
                  {renderBodyDiagram()}
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 2: Symptom Details */}
          {currentStep === 2 && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-gray-200'} backdrop-blur-sm shadow-xl`}>
                <h2 className={`text-xl font-semibold mb-6 ${darkMode ? 'text-white' : 'text-gray-800'} flex items-center`}>
                  <FiClock className="w-5 h-5 mr-2 text-blue-500" />
                  Tell us more about your symptoms
                </h2>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Duration */}
                  <div>
                    <label className={`block text-sm font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      How long have you had these symptoms?
                    </label>
                    <select
                      value={formData.duration}
                      onChange={(e) => handleInputChange('duration', e.target.value)}
                      className={`w-full p-4 rounded-xl border transition-all duration-200 ${darkMode
                          ? 'bg-gray-700 border-gray-600 text-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                          : 'bg-white border-gray-300 text-gray-800 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                        }`}
                    >
                      <option value="">Select duration...</option>
                      {durationOptions.map((duration) => (
                        <option key={duration} value={duration}>
                          {duration}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Severity rating */}
                  <div>
                    <label className={`block text-sm font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Rate your symptom severity (1-10)
                    </label>
                    <div className="space-y-3">
                      <input
                        type="range"
                        min="1"
                        max="10"
                        value={formData.severityRating}
                        onChange={(e) => handleInputChange('severityRating', parseInt(e.target.value))}
                        className="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
                      />
                      <div className="flex justify-between text-sm">
                        <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Mild (1)</span>
                        <span className={`font-bold text-lg px-3 py-1 rounded-lg ${darkMode ? 'text-white bg-gray-700' : 'text-gray-800 bg-gray-100'}`}>
                          {formData.severityRating}
                        </span>
                        <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Severe (10)</span>
                      </div>
                    </div>
                  </div>

                  {/* Location */}
                  <div>
                    <label className={`block text-sm font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Specific location (optional)
                    </label>
                    <input
                      type="text"
                      value={formData.location}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      placeholder="e.g., left side of head, lower back..."
                      className={`w-full p-4 rounded-xl border transition-all duration-200 ${darkMode
                          ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                          : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                        }`}
                    />
                  </div>

                  {/* Associated symptoms */}
                  <div>
                    <label className={`block text-sm font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Any other symptoms? (optional)
                    </label>
                    <textarea
                      value={formData.associatedSymptoms.join(', ')}
                      onChange={(e) => handleInputChange('associatedSymptoms', e.target.value.split(',').map(s => s.trim()).filter(s => s))}
                      placeholder="e.g., sweating, dizziness, nausea..."
                      className={`w-full p-4 rounded-xl border transition-all duration-200 ${darkMode
                          ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                          : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                        }`}
                      rows={4}
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 3: Additional Information */}
          {currentStep === 3 && (
            <motion.div
              key="step3"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-gray-200'} backdrop-blur-sm shadow-xl`}>
                <h2 className={`text-xl font-semibold mb-6 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                  Additional details (optional)
                </h2>

                <div className="grid md:grid-cols-2 gap-6">
                  {/* Triggers */}
                  <div>
                    <label className={`block text-sm font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      What makes it worse?
                    </label>
                    <textarea
                      value={formData.triggers.join(', ')}
                      onChange={(e) => handleInputChange('triggers', e.target.value.split(',').map(s => s.trim()).filter(s => s))}
                      placeholder="e.g., movement, stress, certain foods..."
                      className={`w-full p-4 rounded-xl border transition-all duration-200 ${darkMode
                          ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                          : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                        }`}
                      rows={4}
                    />
                  </div>

                  {/* Alleviating factors */}
                  <div>
                    <label className={`block text-sm font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      What makes it better?
                    </label>
                    <textarea
                      value={formData.alleviatingFactors.join(', ')}
                      onChange={(e) => handleInputChange('alleviatingFactors', e.target.value.split(',').map(s => s.trim()).filter(s => s))}
                      placeholder="e.g., rest, medication, heat/cold..."
                      className={`w-full p-4 rounded-xl border transition-all duration-200 ${darkMode
                          ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                          : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20'
                        }`}
                      rows={4}
                    />
                  </div>
                </div>

                {/* Summary */}
                <div className={`mt-8 p-6 rounded-xl border ${darkMode ? 'bg-gray-700/50 border-gray-600' : 'bg-gray-50 border-gray-200'}`}>
                  <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'} flex items-center`}>
                    <FiCheckCircle className="w-5 h-5 mr-2 text-green-500" />
                    Summary
                  </h3>
                  <div className="space-y-3 text-sm">
                    <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                      <strong className={darkMode ? 'text-white' : 'text-gray-800'}>Symptoms:</strong> {formData.symptoms.join(', ') || 'None specified'}
                    </p>
                    <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                      <strong className={darkMode ? 'text-white' : 'text-gray-800'}>Duration:</strong> {formData.duration || 'Not specified'}
                    </p>
                    <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                      <strong className={darkMode ? 'text-white' : 'text-gray-800'}>Severity:</strong> {formData.severityRating}/10
                    </p>
                    {formData.location && (
                      <p className={darkMode ? 'text-gray-300' : 'text-gray-600'}>
                        <strong className={darkMode ? 'text-white' : 'text-gray-800'}>Location:</strong> {formData.location}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 4: Results */}
          {currentStep === 4 && analysis && (
            <motion.div
              key="step4"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-gray-800/50 border-gray-700' : 'bg-white/80 border-gray-200'} backdrop-blur-sm shadow-xl`}>
                <h2 className={`text-2xl font-bold mb-6 ${darkMode ? 'text-white' : 'text-gray-800'} flex items-center`}>
                  <FiActivity className="w-6 h-6 mr-3 text-blue-500" />
                  Analysis Results
                </h2>

                {/* Urgency indicator */}
                {renderUrgencyIndicator(analysis.urgency_level, analysis.urgency_score)}

                {/* Emergency indicators */}
                {analysis.emergency_indicators && analysis.emergency_indicators.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700 rounded-2xl shadow-lg mb-6"
                  >
                    <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-3 flex items-center">
                      <FiAlertTriangle className="w-5 h-5 mr-2" />
                      Emergency Indicators Detected
                    </h3>
                    <ul className="list-disc list-inside text-red-700 dark:text-red-300 space-y-1">
                      {analysis.emergency_indicators.map((indicator, index) => (
                        <li key={index}>{indicator}</li>
                      ))}
                    </ul>
                  </motion.div>
                )}

                {/* Red flags */}
                {analysis.red_flags && analysis.red_flags.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-6 bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-700 rounded-2xl shadow-lg mb-6"
                  >
                    <h3 className="text-lg font-semibold text-orange-800 dark:text-orange-200 mb-3 flex items-center">
                      <FiAlertTriangle className="w-5 h-5 mr-2" />
                      Warning Signs
                    </h3>
                    <ul className="list-disc list-inside text-orange-700 dark:text-orange-300 space-y-1">
                      {analysis.red_flags.map((flag, index) => (
                        <li key={index}>{flag}</li>
                      ))}
                    </ul>
                  </motion.div>
                )}

                {/* Possible conditions */}
                {analysis.possible_conditions && analysis.possible_conditions.length > 0 && (
                  <div>
                    <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                      Possible Conditions
                    </h3>
                    <div className="space-y-4">
                      {analysis.possible_conditions.map((condition, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className={`p-5 rounded-xl border ${darkMode ? 'bg-gray-700/50 border-gray-600' : 'bg-gray-50 border-gray-200'} shadow-lg`}
                        >
                          <div className="flex justify-between items-start mb-3">
                            <h4 className={`font-semibold text-lg ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                              {condition.condition_name}
                            </h4>
                            <span className="text-sm bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-3 py-1 rounded-full font-medium">
                              {Math.round(condition.confidence_score * 100)}% match
                            </span>
                          </div>
                          <p className={`text-sm mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-600'} leading-relaxed`}>
                            {condition.description}
                          </p>
                          {condition.recommended_actions && condition.recommended_actions.length > 0 && (
                            <div>
                              <p className={`text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                                Recommended actions:
                              </p>
                              <ul className={`text-sm list-disc list-inside space-y-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                {condition.recommended_actions.map((action, actionIndex) => (
                                  <li key={actionIndex}>{action}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {analysis.recommendations && analysis.recommendations.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-6 rounded-xl border ${darkMode ? 'bg-blue-900/20 border-blue-700' : 'bg-blue-50 border-blue-200'} mt-6`}
                  >
                    <h3 className={`text-lg font-semibold mb-3 ${darkMode ? 'text-blue-200' : 'text-blue-800'} flex items-center`}>
                      <FiCheckCircle className="w-5 h-5 mr-2" />
                      General Recommendations
                    </h3>
                    <ul className={`list-disc list-inside space-y-1 ${darkMode ? 'text-blue-300' : 'text-blue-700'}`}>
                      {analysis.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navigation buttons */}
        <div className="flex justify-between items-center mt-8">
          <button
            onClick={prevStep}
            disabled={currentStep === 1 || currentStep === 4}
            className={`flex items-center space-x-2 px-6 py-3 rounded-xl transition-all duration-200 ${currentStep === 1 || currentStep === 4
                ? 'opacity-50 cursor-not-allowed'
                : darkMode
                  ? 'bg-gray-700 hover:bg-gray-600 text-white'
                  : 'bg-gray-200 hover:bg-gray-300 text-gray-800'
              } shadow-lg hover:shadow-xl`}
          >
            <FiArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>

          <div className="flex space-x-3">
            {currentStep === 4 ? (
              <button
                onClick={resetForm}
                className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all duration-200 shadow-lg hover:shadow-xl font-medium"
              >
                Start New Analysis
              </button>
            ) : (
              <button
                onClick={nextStep}
                disabled={loading || (currentStep === 1 && formData.symptoms.length === 0)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-xl transition-all duration-200 font-medium ${loading || (currentStep === 1 && formData.symptoms.length === 0)
                    ? 'opacity-50 cursor-not-allowed bg-gray-400'
                    : 'bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl'
                  }`}
              >
                <span>{currentStep === 3 ? (loading ? 'Analyzing...' : 'Analyze Symptoms') : 'Next'}</span>
                {!loading && <FiArrowRight className="w-4 h-4" />}
                {loading && (
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SymptomChecker;