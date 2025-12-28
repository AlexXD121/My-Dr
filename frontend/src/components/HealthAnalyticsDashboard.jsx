import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

const HealthAnalyticsDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [selectedView, setSelectedView] = useState('overview');

  // Mock data for demo
  const mockData = {
    healthScore: 85,
    consultations: 3,
    symptoms: ['Headache', 'Fatigue', 'Cough'],
    riskLevel: 'Low'
  };



  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            📊 Health Analytics Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Your health insights and trends (Demo Mode)
          </p>
        </div>

        {/* View Selector */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2">
            {['overview', 'trends', 'insights'].map((view) => (
              <button
                key={view}
                onClick={() => setSelectedView(view)}
                className={`px-4 py-2 rounded-lg transition-colors ${selectedView === view
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
              >
                {view.charAt(0).toUpperCase() + view.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Health Metrics Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Health Score */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Health Score</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{mockData.healthScore}/100</p>
                </div>
                <div className="text-green-500">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Consultations */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Consultations</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{mockData.consultations}</p>
                </div>
                <div className="text-blue-500">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Active Symptoms */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Active Symptoms</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{mockData.symptoms.length}</p>
                </div>
                <div className="text-yellow-500">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>

            {/* Risk Level */}
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Risk Level</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{mockData.riskLevel}</p>
                </div>
                <div className="text-green-500">
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Main Content Based on Selected View */}
        {selectedView === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Recent Symptoms
              </h3>
              <div className="space-y-3">
                {mockData.symptoms.map((symptom, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <span className="text-gray-900 dark:text-white">{symptom}</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">Recent</span>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Health Summary
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Overall Health:</span>
                  <span className="font-medium text-green-600">Good</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Last Consultation:</span>
                  <span className="font-medium text-gray-900 dark:text-white">2 days ago</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 dark:text-gray-400">Next Checkup:</span>
                  <span className="font-medium text-blue-600">In 1 month</span>
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {selectedView === 'trends' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Health Trends (Coming Soon)
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Detailed trend analysis will be available once you have more consultation data.
            </p>
          </motion.div>
        )}

        {selectedView === 'insights' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Health Insights & Recommendations
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-lg border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  Stay Hydrated
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Based on your recent consultations, maintaining proper hydration could help with your symptoms.
                </p>
                <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  💡 Aim for 8 glasses of water daily
                </p>
              </div>

              <div className="p-6 rounded-lg border-l-4 border-green-500 bg-green-50 dark:bg-green-900">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                  Regular Exercise
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                  Your health score indicates good overall fitness. Keep up the good work!
                </p>
                <p className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  💡 Continue your current activity level
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default HealthAnalyticsDashboard;