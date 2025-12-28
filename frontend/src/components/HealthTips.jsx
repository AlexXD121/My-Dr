import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const HealthTips = ({ isOpen, onClose, darkMode }) => {
  const [selectedCategory, setSelectedCategory] = useState('general');
  const [tips, setTips] = useState([]);

  const categories = {
    general: '🏥 General Health',
    nutrition: '🥗 Nutrition',
    exercise: '🏃‍♂️ Exercise',
    mental_health: '🧠 Mental Health'
  };

  const healthTips = {
    general: [
      'Stay hydrated by drinking at least 8 glasses of water daily',
      'Aim for 7-9 hours of quality sleep each night',
      'Wash your hands frequently to prevent infections',
      'Schedule regular check-ups with your healthcare provider',
      'Take breaks from screens every 20 minutes'
    ],
    nutrition: [
      'Include a variety of colorful fruits and vegetables in your diet',
      'Choose whole grains over refined grains',
      'Limit processed foods and added sugars',
      'Include lean proteins in your meals',
      'Practice portion control'
    ],
    exercise: [
      'Aim for at least 150 minutes of moderate exercise per week',
      'Include both cardio and strength training exercises',
      'Take regular breaks from sitting throughout the day',
      'Start with small, achievable fitness goals',
      'Find physical activities you enjoy'
    ],
    mental_health: [
      'Practice mindfulness and meditation',
      'Maintain social connections with friends and family',
      'Set realistic goals and expectations',
      'Take breaks when feeling overwhelmed',
      'Seek professional help when needed'
    ]
  };

  useEffect(() => {
    setTips(healthTips[selectedCategory] || []);
  }, [selectedCategory]);

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`flex-1 ${darkMode ? 'bg-gray-900' : 'bg-white'}`}
    >
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            💡 Health Tips
          </h1>

        </div>

        <div className="max-w-4xl mx-auto">
          {/* Category Selection */}
          <div className="mb-8">
            <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              Choose a category:
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {Object.entries(categories).map(([key, label]) => (
                <button
                  key={key}
                  onClick={() => setSelectedCategory(key)}
                  className={`p-4 rounded-lg border-2 transition-colors ${
                    selectedCategory === key
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900'
                      : darkMode
                      ? 'border-gray-600 bg-gray-800 hover:bg-gray-700'
                      : 'border-gray-200 bg-white hover:bg-gray-50'
                  }`}
                >
                  <div className={`text-center ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                    {label}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Tips Display */}
          <div className="space-y-4">
            <h3 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              {categories[selectedCategory]} Tips
            </h3>
            
            {tips.map((tip, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-4 rounded-lg border ${
                  darkMode 
                    ? 'bg-gray-800 border-gray-600' 
                    : 'bg-white border-gray-200'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-100 to-gray-100 dark:from-blue-900 dark:to-gray-800 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 dark:text-blue-300 font-semibold text-sm">
                      {index + 1}
                    </span>
                  </div>
                  <p className={`${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    {tip}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Disclaimer */}
          <div className={`mt-8 p-4 rounded-lg ${darkMode ? 'bg-yellow-900' : 'bg-yellow-100'}`}>
            <p className={`text-sm ${darkMode ? 'text-yellow-200' : 'text-yellow-800'}`}>
              ⚠️ These are general health tips and should not replace professional medical advice. 
              Always consult with your healthcare provider for personalized medical guidance.
            </p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default HealthTips;