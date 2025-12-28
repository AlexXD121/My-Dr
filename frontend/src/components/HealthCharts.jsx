import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
} from 'chart.js';
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

// Health Score Trend Chart
export const HealthScoreTrendChart = ({ data, isDark = false }) => {
  const chartData = {
    labels: data?.labels || [],
    datasets: [
      {
        label: 'Health Score',
        data: data?.values || [],
        borderColor: isDark ? '#60A5FA' : '#3B82F6',
        backgroundColor: isDark ? 'rgba(96, 165, 250, 0.1)' : 'rgba(59, 130, 246, 0.1)',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: isDark ? '#60A5FA' : '#3B82F6',
        pointBorderColor: isDark ? '#1F2937' : '#FFFFFF',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: isDark ? '#374151' : '#FFFFFF',
        titleColor: isDark ? '#F9FAFB' : '#111827',
        bodyColor: isDark ? '#F9FAFB' : '#111827',
        borderColor: isDark ? '#4B5563' : '#E5E7EB',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: function(context) {
            return `Health Score: ${context.parsed.y}/100`;
          }
        }
      }
    },
    scales: {
      x: {
        grid: {
          color: isDark ? '#374151' : '#F3F4F6',
          borderColor: isDark ? '#4B5563' : '#E5E7EB'
        },
        ticks: {
          color: isDark ? '#9CA3AF' : '#6B7280'
        }
      },
      y: {
        min: 0,
        max: 100,
        grid: {
          color: isDark ? '#374151' : '#F3F4F6',
          borderColor: isDark ? '#4B5563' : '#E5E7EB'
        },
        ticks: {
          color: isDark ? '#9CA3AF' : '#6B7280',
          callback: function(value) {
            return value + '/100';
          }
        }
      }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  };

  return (
    <div className="h-64 w-full">
      <Line data={chartData} options={options} />
    </div>
  );
};

// Consultation Frequency Chart
export const ConsultationFrequencyChart = ({ data, isDark = false }) => {
  const chartData = {
    labels: data?.labels || [],
    datasets: [
      {
        label: 'Consultations',
        data: data?.values || [],
        backgroundColor: isDark ? 'rgba(34, 197, 94, 0.8)' : 'rgba(34, 197, 94, 0.6)',
        borderColor: isDark ? '#22C55E' : '#16A34A',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: isDark ? '#374151' : '#FFFFFF',
        titleColor: isDark ? '#F9FAFB' : '#111827',
        bodyColor: isDark ? '#F9FAFB' : '#111827',
        borderColor: isDark ? '#4B5563' : '#E5E7EB',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: function(context) {
            const value = context.parsed.y;
            return `${value} consultation${value !== 1 ? 's' : ''}`;
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
          color: isDark ? '#9CA3AF' : '#6B7280'
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: isDark ? '#374151' : '#F3F4F6',
          borderColor: isDark ? '#4B5563' : '#E5E7EB'
        },
        ticks: {
          color: isDark ? '#9CA3AF' : '#6B7280',
          stepSize: 1
        }
      }
    }
  };

  return (
    <div className="h-64 w-full">
      <Bar data={chartData} options={options} />
    </div>
  );
};

// Symptom Distribution Chart
export const SymptomDistributionChart = ({ data, isDark = false }) => {
  const colors = [
    '#EF4444', '#F97316', '#F59E0B', '#EAB308', '#84CC16',
    '#22C55E', '#10B981', '#14B8A6', '#06B6D4', '#0EA5E9',
    '#3B82F6', '#6366F1', '#8B5CF6', '#A855F7', '#D946EF'
  ];

  const chartData = {
    labels: data?.labels || [],
    datasets: [
      {
        data: data?.values || [],
        backgroundColor: colors.slice(0, data?.labels?.length || 0),
        borderColor: isDark ? '#1F2937' : '#FFFFFF',
        borderWidth: 2,
        hoverBorderWidth: 3,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: isDark ? '#F9FAFB' : '#111827',
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle',
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        backgroundColor: isDark ? '#374151' : '#FFFFFF',
        titleColor: isDark ? '#F9FAFB' : '#111827',
        bodyColor: isDark ? '#F9FAFB' : '#111827',
        borderColor: isDark ? '#4B5563' : '#E5E7EB',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    },
    cutout: '50%'
  };

  return (
    <div className="h-64 w-full">
      <Doughnut data={chartData} options={options} />
    </div>
  );
};

// Risk Assessment Radar Chart
export const RiskAssessmentChart = ({ data, isDark = false }) => {
  const chartData = {
    labels: data?.labels || ['Age', 'Medical History', 'Lifestyle', 'Symptoms', 'Medications'],
    datasets: [
      {
        label: 'Risk Level',
        data: data?.values || [0, 0, 0, 0, 0],
        backgroundColor: isDark ? 'rgba(239, 68, 68, 0.2)' : 'rgba(239, 68, 68, 0.1)',
        borderColor: isDark ? '#EF4444' : '#DC2626',
        borderWidth: 2,
        pointBackgroundColor: isDark ? '#EF4444' : '#DC2626',
        pointBorderColor: isDark ? '#1F2937' : '#FFFFFF',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: isDark ? '#374151' : '#FFFFFF',
        titleColor: isDark ? '#F9FAFB' : '#111827',
        bodyColor: isDark ? '#F9FAFB' : '#111827',
        borderColor: isDark ? '#4B5563' : '#E5E7EB',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: false,
        callbacks: {
          label: function(context) {
            const riskLevels = ['Very Low', 'Low', 'Moderate', 'High', 'Very High'];
            const level = Math.min(Math.floor(context.parsed.r), 4);
            return `${context.label}: ${riskLevels[level]}`;
          }
        }
      }
    },
    scales: {
      r: {
        beginAtZero: true,
        min: 0,
        max: 5,
        ticks: {
          stepSize: 1,
          color: isDark ? '#9CA3AF' : '#6B7280',
          backdropColor: 'transparent',
          callback: function(value) {
            const labels = ['', 'Low', '', 'Med', '', 'High'];
            return labels[value] || '';
          }
        },
        grid: {
          color: isDark ? '#374151' : '#F3F4F6'
        },
        angleLines: {
          color: isDark ? '#374151' : '#F3F4F6'
        },
        pointLabels: {
          color: isDark ? '#F9FAFB' : '#111827',
          font: {
            size: 12
          }
        }
      }
    }
  };

  return (
    <div className="h-64 w-full">
      <Radar data={chartData} options={options} />
    </div>
  );
};

// Health Timeline Chart
export const HealthTimelineChart = ({ data, isDark = false }) => {
  const chartData = {
    labels: data?.labels || [],
    datasets: [
      {
        label: 'Health Events',
        data: data?.consultations || [],
        borderColor: isDark ? '#3B82F6' : '#2563EB',
        backgroundColor: isDark ? 'rgba(59, 130, 246, 0.1)' : 'rgba(37, 99, 235, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: isDark ? '#3B82F6' : '#2563EB',
        pointBorderColor: isDark ? '#1F2937' : '#FFFFFF',
        pointBorderWidth: 2,
        pointRadius: 4,
      },
      {
        label: 'Symptoms',
        data: data?.symptoms || [],
        borderColor: isDark ? '#F59E0B' : '#D97706',
        backgroundColor: isDark ? 'rgba(245, 158, 11, 0.1)' : 'rgba(217, 119, 6, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: isDark ? '#F59E0B' : '#D97706',
        pointBorderColor: isDark ? '#1F2937' : '#FFFFFF',
        pointBorderWidth: 2,
        pointRadius: 4,
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: isDark ? '#F9FAFB' : '#111827',
          padding: 20,
          usePointStyle: true,
          pointStyle: 'circle'
        }
      },
      tooltip: {
        backgroundColor: isDark ? '#374151' : '#FFFFFF',
        titleColor: isDark ? '#F9FAFB' : '#111827',
        bodyColor: isDark ? '#F9FAFB' : '#111827',
        borderColor: isDark ? '#4B5563' : '#E5E7EB',
        borderWidth: 1,
        cornerRadius: 8,
        mode: 'index',
        intersect: false
      }
    },
    scales: {
      x: {
        grid: {
          color: isDark ? '#374151' : '#F3F4F6',
          borderColor: isDark ? '#4B5563' : '#E5E7EB'
        },
        ticks: {
          color: isDark ? '#9CA3AF' : '#6B7280'
        }
      },
      y: {
        beginAtZero: true,
        grid: {
          color: isDark ? '#374151' : '#F3F4F6',
          borderColor: isDark ? '#4B5563' : '#E5E7EB'
        },
        ticks: {
          color: isDark ? '#9CA3AF' : '#6B7280',
          stepSize: 1
        }
      }
    },
    interaction: {
      intersect: false,
      mode: 'index'
    }
  };

  return (
    <div className="h-64 w-full">
      <Line data={chartData} options={options} />
    </div>
  );
};

// Health Metrics Cards Component
export const HealthMetricsCards = ({ metrics, isDark = false }) => {
  const cards = [
    {
      title: 'Overall Health Score',
      value: metrics?.healthScore || 0,
      unit: '/100',
      icon: '🏥',
      color: 'blue',
      trend: metrics?.healthScoreTrend || 'stable'
    },
    {
      title: 'Risk Level',
      value: metrics?.riskLevel || 'Low',
      unit: '',
      icon: '⚠️',
      color: metrics?.riskLevel === 'High' ? 'red' : metrics?.riskLevel === 'Moderate' ? 'yellow' : 'green',
      trend: metrics?.riskTrend || 'stable'
    },
    {
      title: 'Active Symptoms',
      value: metrics?.activeSymptoms || 0,
      unit: '',
      icon: '🩺',
      color: 'purple',
      trend: metrics?.symptomsTrend || 'stable'
    },
    {
      title: 'Consultations',
      value: metrics?.consultations || 0,
      unit: ' this month',
      icon: '💬',
      color: 'green',
      trend: metrics?.consultationsTrend || 'stable'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
      red: 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200',
      yellow: 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200',
      green: 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
      purple: 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200'
    };
    return colors[color] || colors.blue;
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return '📈';
      case 'decreasing': return '📉';
      default: return '➡️';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <div
          key={index}
          className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
        >
          <div className="flex items-center justify-between mb-4">
            <div className={`p-2 rounded-lg ${getColorClasses(card.color)}`}>
              <span className="text-2xl">{card.icon}</span>
            </div>
            <span className="text-lg">{getTrendIcon(card.trend)}</span>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
              {card.title}
            </p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {card.value}{card.unit}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
};