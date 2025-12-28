import React, { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { format, parseISO } from 'date-fns';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const MoodTrendChart = ({ data, period = '30d', className = '' }) => {
  const chartRef = useRef();

  // Prepare chart data
  const chartData = {
    labels: data?.daily_averages?.map(item => {
      try {
        return format(parseISO(item.date), 'MMM dd');
      } catch (error) {
        return item.date;
      }
    }) || [],
    datasets: [
      {
        label: 'Mood Score',
        data: data?.daily_averages?.map(item => item.avg_mood) || [],
        borderColor: 'rgb(59, 130, 246)', // Blue-500
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
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
        text: `Mood Trend - Last ${period === '7d' ? '7 Days' : period === '30d' ? '30 Days' : period === '90d' ? '90 Days' : '1 Year'}`,
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
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            const value = context.parsed.y;
            let moodLabel = '';
            
            if (value >= 8) moodLabel = 'Great';
            else if (value >= 7) moodLabel = 'Good';
            else if (value >= 6) moodLabel = 'Okay';
            else if (value >= 5) moodLabel = 'Fair';
            else if (value >= 4) moodLabel = 'Low';
            else moodLabel = 'Very Low';
            
            return `Mood: ${value.toFixed(1)}/10 (${moodLabel})`;
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
          maxTicksLimit: 7,
          color: '#6b7280'
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
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  };

  // Loading state
  if (!data || !data.daily_averages || data.daily_averages.length === 0) {
    return (
      <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-gray-400 mb-2">
              <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="text-gray-500 text-sm">No mood data available</p>
            <p className="text-gray-400 text-xs mt-1">Start tracking your mood to see trends</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      <div className="h-64 relative">
        <Line ref={chartRef} data={chartData} options={options} />
      </div>
      
      {/* Trend indicator */}
      {data.overall_trend && (
        <div className="mt-4 flex items-center justify-center">
          <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            data.overall_trend === 'improving' 
              ? 'bg-green-100 text-green-800' 
              : data.overall_trend === 'declining' 
                ? 'bg-red-100 text-red-800' 
                : 'bg-gray-100 text-gray-800'
          }`}>
            {data.overall_trend === 'improving' && (
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            )}
            {data.overall_trend === 'declining' && (
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
            )}
            {data.overall_trend === 'stable' && (
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            )}
            Trend: {data.overall_trend}
          </div>
        </div>
      )}
    </div>
  );
};

export default MoodTrendChart;