import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const ActivityCorrelation = ({ data, className = '' }) => {
  // Process activity correlation data
  const processActivityData = (moodEntries) => {
    if (!moodEntries || moodEntries.length === 0) {
      return {
        activities: [],
        correlations: [],
        colors: []
      };
    }

    // Count trigger occurrences and calculate average mood for each
    const triggerData = {};
    
    moodEntries.forEach(entry => {
      const triggers = entry.triggers || [];
      const moodScore = entry.avg_mood || entry.mood_score || 5.5;
      
      triggers.forEach(trigger => {
        if (!triggerData[trigger]) {
          triggerData[trigger] = {
            count: 0,
            totalMood: 0,
            avgMood: 0
          };
        }
        triggerData[trigger].count++;
        triggerData[trigger].totalMood += moodScore;
      });
    });

    // Calculate averages and sort by frequency
    const processedTriggers = Object.entries(triggerData)
      .map(([trigger, data]) => ({
        trigger: trigger.charAt(0).toUpperCase() + trigger.slice(1),
        avgMood: data.totalMood / data.count,
        count: data.count,
        correlation: data.totalMood / data.count - 5.5 // Deviation from neutral (5.5)
      }))
      .filter(item => item.count >= 2) // Only show triggers that appear at least twice
      .sort((a, b) => b.count - a.count)
      .slice(0, 8); // Show top 8 triggers

    return {
      activities: processedTriggers.map(item => item.trigger),
      correlations: processedTriggers.map(item => item.avgMood),
      counts: processedTriggers.map(item => item.count),
      colors: processedTriggers.map(item => {
        if (item.avgMood >= 7) return '#10b981'; // Green for positive
        if (item.avgMood >= 6) return '#60a5fa'; // Blue for neutral-positive
        if (item.avgMood >= 5) return '#fbbf24'; // Yellow for neutral
        if (item.avgMood >= 4) return '#fb923c'; // Orange for negative
        return '#f87171'; // Red for very negative
      })
    };
  };

  const activityData = processActivityData(data?.daily_averages || []);

  // Chart data
  const chartData = {
    labels: activityData.activities,
    datasets: [
      {
        label: 'Average Mood Score',
        data: activityData.correlations,
        backgroundColor: activityData.colors,
        borderColor: activityData.colors.map(color => color),
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false,
      }
    ]
  };

  // Chart options
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: true,
        text: 'Mood by Activity/Trigger',
        font: {
          size: 16,
          weight: 'bold'
        },
        color: '#1f2937'
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#ffffff',
        bodyColor: '#ffffff',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const index = context.dataIndex;
            const count = activityData.counts[index];
            const avgMood = context.parsed.y;
            
            let moodLabel = '';
            if (avgMood >= 8) moodLabel = 'Great';
            else if (avgMood >= 7) moodLabel = 'Good';
            else if (avgMood >= 6) moodLabel = 'Okay';
            else if (avgMood >= 5) moodLabel = 'Fair';
            else if (avgMood >= 4) moodLabel = 'Low';
            else moodLabel = 'Poor';
            
            return [
              `Average Mood: ${avgMood.toFixed(1)}/10 (${moodLabel})`,
              `Occurrences: ${count} times`
            ];
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          display: false
        },
        ticks: {
          color: '#6b7280',
          maxRotation: 45,
          minRotation: 0
        }
      },
      y: {
        min: 1,
        max: 10,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        ticks: {
          stepSize: 1,
          color: '#6b7280',
          callback: function(value) {
            return value.toFixed(0);
          }
        }
      }
    }
  };

  // Loading/empty state
  if (!data || !data.daily_averages || data.daily_averages.length === 0 || activityData.activities.length === 0) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Activity Correlation</h3>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-gray-400 mb-2">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="text-gray-500 text-sm">No activity data available</p>
            <p className="text-gray-400 text-xs mt-1">Track activities to see correlations</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="h-64 relative">
        <Bar data={chartData} options={options} />
      </div>
      
      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-2 justify-center">
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-green-500 rounded mr-1"></div>
          <span className="text-gray-600">Positive (7+)</span>
        </div>
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-blue-400 rounded mr-1"></div>
          <span className="text-gray-600">Good (6-7)</span>
        </div>
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-yellow-400 rounded mr-1"></div>
          <span className="text-gray-600">Neutral (5-6)</span>
        </div>
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-orange-400 rounded mr-1"></div>
          <span className="text-gray-600">Low (4-5)</span>
        </div>
        <div className="flex items-center text-xs">
          <div className="w-3 h-3 bg-red-400 rounded mr-1"></div>
          <span className="text-gray-600">Poor (&lt;4)</span>
        </div>
      </div>
    </div>
  );
};

export default ActivityCorrelation;