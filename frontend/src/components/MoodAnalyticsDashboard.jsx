import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useApi } from '../hooks/useApi';
import MoodTrendChart from './MoodTrendChart';
import MoodDistribution from './MoodDistribution';
import ActivityCorrelation from './ActivityCorrelation';
import DateRangeSelector from './DateRangeSelector';
import DataExport from './DataExport';

const MoodAnalyticsDashboard = () => {
  const { user } = useAuth();
  const { apiCall, loading, error } = useApi();
  
  // State management
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [customStartDate, setCustomStartDate] = useState(null);
  const [customEndDate, setCustomEndDate] = useState(null);
  const [moodData, setMoodData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [showExportModal, setShowExportModal] = useState(false);

  // Fetch mood data based on selected period
  const fetchMoodData = async (period, startDate = null, endDate = null) => {
    try {
      let trendsResponse, summaryResponse;

      if (period === 'custom' && startDate && endDate) {
        // For custom date range, calculate days difference
        const daysDiff = Math.ceil((new Date(endDate) - new Date(startDate)) / (1000 * 60 * 60 * 24));
        
        [trendsResponse, summaryResponse] = await Promise.all([
          apiCall(`/mood/trends?period=custom&start_date=${startDate}&end_date=${endDate}`),
          apiCall(`/mood/summary?days=${daysDiff}&start_date=${startDate}&end_date=${endDate}`)
        ]);
      } else {
        // For predefined periods
        const days = period === '7d' ? 7 : period === '30d' ? 30 : period === '90d' ? 90 : 365;
        
        [trendsResponse, summaryResponse] = await Promise.all([
          apiCall(`/mood/trends?period=${period}`),
          apiCall(`/mood/summary?days=${days}`)
        ]);
      }

      setTrendsData(trendsResponse);
      setSummaryData(summaryResponse);
      setMoodData(trendsResponse); // Use trends data for charts
      
    } catch (err) {
      console.error('Failed to fetch mood data:', err);
    }
  };

  // Effect to fetch data when period changes
  useEffect(() => {
    if (user) {
      if (selectedPeriod === 'custom' && customStartDate && customEndDate) {
        fetchMoodData('custom', customStartDate, customEndDate);
      } else if (selectedPeriod !== 'custom') {
        fetchMoodData(selectedPeriod);
      }
    }
  }, [user, selectedPeriod, customStartDate, customEndDate]);

  // Handle period change
  const handlePeriodChange = (period) => {
    setSelectedPeriod(period);
    if (period !== 'custom') {
      setCustomStartDate(null);
      setCustomEndDate(null);
    }
  };

  // Handle custom date change
  const handleCustomDateChange = (field, value) => {
    if (field === 'start') {
      setCustomStartDate(value);
    } else {
      setCustomEndDate(value);
    }
  };

  // Loading state
  if (loading && !moodData) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              <div className="h-32 bg-gray-200 rounded-lg"></div>
              <div className="h-32 bg-gray-200 rounded-lg"></div>
              <div className="h-32 bg-gray-200 rounded-lg"></div>
            </div>
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <div className="h-80 bg-gray-200 rounded-lg"></div>
              <div className="h-80 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !moodData) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <div className="text-red-400 mb-4">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-red-800 mb-2">Failed to Load Analytics</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={() => fetchMoodData(selectedPeriod, customStartDate, customEndDate)}
              className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Mood Analytics</h1>
            <p className="text-gray-600">Track your emotional wellbeing and discover patterns</p>
          </div>
          <button
            onClick={() => setShowExportModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export Data
          </button>
        </div>

        {/* Date Range Selector */}
        <DateRangeSelector
          selectedPeriod={selectedPeriod}
          onPeriodChange={handlePeriodChange}
          customStartDate={customStartDate}
          customEndDate={customEndDate}
          onCustomDateChange={handleCustomDateChange}
          className="mb-6"
        />

        {/* Summary Cards */}
        {summaryData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Average Mood</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {summaryData.avg_mood?.toFixed(1) || 'N/A'}/10
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Trend</p>
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {summaryData.mood_trend || 'Stable'}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Entries</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {summaryData.total_entries || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Top Emotion</p>
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {summaryData.dominant_emotions?.[0] || 'None'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Charts Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
          <MoodTrendChart 
            data={trendsData} 
            period={selectedPeriod}
            className="xl:col-span-2"
          />
          
          <MoodDistribution 
            data={trendsData}
          />
          
          <ActivityCorrelation 
            data={trendsData}
          />
        </div>

        {/* Insights Section */}
        {summaryData && summaryData.dominant_emotions && summaryData.dominant_emotions.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Insights</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-700 mb-2">Most Common Emotions</h4>
                <div className="flex flex-wrap gap-2">
                  {summaryData.dominant_emotions.slice(0, 5).map((emotion, index) => (
                    <span
                      key={emotion}
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        index === 0 
                          ? 'bg-blue-100 text-blue-800' 
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {emotion}
                    </span>
                  ))}
                </div>
              </div>
              
              {summaryData.common_triggers && summaryData.common_triggers.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Common Triggers</h4>
                  <div className="flex flex-wrap gap-2">
                    {summaryData.common_triggers.slice(0, 5).map((trigger, index) => (
                      <span
                        key={trigger}
                        className={`px-3 py-1 rounded-full text-sm font-medium ${
                          index === 0 
                            ? 'bg-orange-100 text-orange-800' 
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {trigger}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Data Export Modal */}
        <DataExport
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
          darkMode={false}
        />
      </div>
    </div>
  );
};

export default MoodAnalyticsDashboard;