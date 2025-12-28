import React from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const MoodDistribution = ({ data, className = '' }) => {
  // Process mood data into distribution categories
  const processMoodData = (moodEntries) => {
    if (!moodEntries || moodEntries.length === 0) {
      return {
        labels: [],
        data: [],
        total: 0
      };
    }

    const categories = {
      'Excellent (9-10)': { count: 0, color: '#10b981', range: [9, 10] },
      'Great (8-8.9)': { count: 0, color: '#34d399', range: [8, 8.9] },
      'Good (7-7.9)': { count: 0, color: '#60a5fa', range: [7, 7.9] },
      'Okay (6-6.9)': { count: 0, color: '#a78bfa', range: [6, 6.9] },
      'Fair (5-5.9)': { count: 0, color: '#fbbf24', range: [5, 5.9] },
      'Low (4-4.9)': { count: 0, color: '#fb923c', range: [4, 4.9] },
      'Poor (1-3.9)': { count: 0, color: '#f87171', range: [1, 3.9] }
    };

    moodEntries.forEach(entry => {
      const score = entry.avg_mood || entry.mood_score || 5.5;
      
      for (const [category, info] of Object.entries(categories)) {
        if (score >= info.range[0] && score <= info.range[1]) {
          info.count++;
          break;
        }
      }
    });

    // Filter out categories with no data
    const filteredCategories = Object.entries(categories)
      .filter(([_, info]) => info.count > 0)
      .sort((a, b) => b[1].count - a[1].count);

    return {
      labels: filteredCategories.map(([label]) => label),
      data: filteredCategories.map(([_, info]) => info.count),
      colors: filteredCategories.map(([_, info]) => info.color),
      total: moodEntries.length
    };
  };

  const distributionData = processMoodData(data?.daily_averages || []);

  // Chart data
  const chartData = {
    labels: distributionData.labels,
    datasets: [
      {
        data: distributionData.data,
        backgroundColor: distributionData.colors,
        borderColor: '#ffffff',
        borderWidth: 2,
        hoverBorderWidth: 3,
        hoverOffset: 4
      }
    ]
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true,
          font: {
            size: 12
          },
          color: '#374151'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const percentage = ((context.parsed / distributionData.total) * 100).toFixed(1);
            return `${context.label}: ${context.parsed} days (${percentage}%)`;
          }
        }
      }
    },
    cutout: '60%'
  };

  // Loading/empty state
  if (!data || !data.daily_averages || data.daily_averages.length === 0) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Mood Distribution</h3>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-gray-400 mb-2">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
              </svg>
            </div>
            <p className="text-gray-500 text-sm">No mood data available</p>
            <p className="text-gray-400 text-xs mt-1">Track your mood to see distribution</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Mood Distribution</h3>
      
      <div className="h-64 relative mb-4">
        <Doughnut data={chartData} options={options} />
        
        {/* Center text showing total entries */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-800">{distributionData.total}</div>
            <div className="text-sm text-gray-500">entries</div>
          </div>
        </div>
      </div>

      {/* Summary stats */}
      {distributionData.total > 0 && (
        <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <div className="text-sm text-gray-500">Most Common</div>
            <div className="font-medium text-gray-800">
              {distributionData.labels[0]?.split(' ')[0] || 'N/A'}
            </div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-500">Total Days</div>
            <div className="font-medium text-gray-800">{distributionData.total}</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MoodDistribution;