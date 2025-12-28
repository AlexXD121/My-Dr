import React from 'react';

const DateRangeSelector = ({ 
  selectedPeriod, 
  onPeriodChange, 
  customStartDate, 
  customEndDate, 
  onCustomDateChange,
  className = '' 
}) => {
  const periods = [
    { value: '7d', label: 'Last 7 Days', icon: '📅' },
    { value: '30d', label: 'Last 30 Days', icon: '📊' },
    { value: '90d', label: 'Last 3 Months', icon: '📈' },
    { value: '1y', label: 'Last Year', icon: '📋' },
    { value: 'custom', label: 'Custom Range', icon: '🗓️' }
  ];

  const handlePeriodClick = (period) => {
    onPeriodChange(period);
  };

  const formatDateForInput = (date) => {
    if (!date) return '';
    const d = new Date(date);
    return d.toISOString().split('T')[0];
  };

  const handleCustomDateChange = (field, value) => {
    if (onCustomDateChange) {
      onCustomDateChange(field, value);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-4 ${className}`}>
      <h3 className="text-sm font-medium text-gray-700 mb-3">Time Period</h3>
      
      {/* Period buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-4">
        {periods.map((period) => (
          <button
            key={period.value}
            onClick={() => handlePeriodClick(period.value)}
            className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all duration-200 ${
              selectedPeriod === period.value
                ? 'border-blue-500 bg-blue-50 text-blue-700'
                : 'border-gray-200 hover:border-gray-300 text-gray-600 hover:text-gray-800'
            }`}
          >
            <span className="text-lg mb-1">{period.icon}</span>
            <span className="text-xs font-medium text-center leading-tight">
              {period.label}
            </span>
          </button>
        ))}
      </div>

      {/* Custom date range inputs */}
      {selectedPeriod === 'custom' && (
        <div className="border-t border-gray-200 pt-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={formatDateForInput(customStartDate)}
                onChange={(e) => handleCustomDateChange('start', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                max={formatDateForInput(new Date())}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                End Date
              </label>
              <input
                type="date"
                value={formatDateForInput(customEndDate)}
                onChange={(e) => handleCustomDateChange('end', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min={formatDateForInput(customStartDate)}
                max={formatDateForInput(new Date())}
              />
            </div>
          </div>
          
          {customStartDate && customEndDate && (
            <div className="mt-3 p-2 bg-blue-50 rounded-md">
              <p className="text-xs text-blue-700">
                <span className="font-medium">Selected range:</span>{' '}
                {new Date(customStartDate).toLocaleDateString()} - {new Date(customEndDate).toLocaleDateString()}
                {' '}({Math.ceil((new Date(customEndDate) - new Date(customStartDate)) / (1000 * 60 * 60 * 24))} days)
              </p>
            </div>
          )}
        </div>
      )}

      {/* Quick stats for selected period */}
      {selectedPeriod !== 'custom' && (
        <div className="border-t border-gray-200 pt-3 mt-3">
          <div className="flex items-center justify-between text-xs text-gray-500">
            <span>Analyzing</span>
            <span className="font-medium">
              {selectedPeriod === '7d' && '7 days'}
              {selectedPeriod === '30d' && '30 days'}
              {selectedPeriod === '90d' && '90 days'}
              {selectedPeriod === '1y' && '365 days'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DateRangeSelector;