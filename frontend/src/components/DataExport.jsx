import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useApi } from '../hooks/useApi';

const DataExport = ({ isOpen, onClose, darkMode = false }) => {
  const { user } = useAuth();
  const { apiCall, loading, error } = useApi();
  
  // State management
  const [exportFormat, setExportFormat] = useState('json');
  const [dataTypes, setDataTypes] = useState(['mood_entries', 'conversations', 'journal_entries']);
  const [dateRange, setDateRange] = useState('all');
  const [customStartDate, setCustomStartDate] = useState('');
  const [customEndDate, setCustomEndDate] = useState('');
  const [includeAnalysis, setIncludeAnalysis] = useState(true);
  const [exportSummary, setExportSummary] = useState(null);
  const [isExporting, setIsExporting] = useState(false);

  // Fetch export summary when component opens
  useEffect(() => {
    if (isOpen && user) {
      fetchExportSummary();
    }
  }, [isOpen, user, dateRange, customStartDate, customEndDate]);

  const fetchExportSummary = async () => {
    try {
      let params = new URLSearchParams();
      
      if (dateRange === 'custom' && customStartDate && customEndDate) {
        params.append('start_date', customStartDate);
        params.append('end_date', customEndDate);
      } else if (dateRange !== 'all') {
        const endDate = new Date();
        const startDate = new Date();
        
        switch (dateRange) {
          case '7d':
            startDate.setDate(endDate.getDate() - 7);
            break;
          case '30d':
            startDate.setDate(endDate.getDate() - 30);
            break;
          case '90d':
            startDate.setDate(endDate.getDate() - 90);
            break;
          case '1y':
            startDate.setFullYear(endDate.getFullYear() - 1);
            break;
        }
        
        params.append('start_date', startDate.toISOString());
        params.append('end_date', endDate.toISOString());
      }
      
      const summary = await apiCall(`/export/summary?${params.toString()}`);
      setExportSummary(summary);
    } catch (err) {
      console.error('Failed to fetch export summary:', err);
    }
  };

  const handleExport = async () => {
    if (!exportSummary) return;
    
    setIsExporting(true);
    
    try {
      let url = '';
      let params = new URLSearchParams();
      
      // Set date parameters
      if (dateRange === 'custom' && customStartDate && customEndDate) {
        params.append('start_date', customStartDate);
        params.append('end_date', customEndDate);
      } else if (dateRange !== 'all') {
        const endDate = new Date();
        const startDate = new Date();
        
        switch (dateRange) {
          case '7d':
            startDate.setDate(endDate.getDate() - 7);
            break;
          case '30d':
            startDate.setDate(endDate.getDate() - 30);
            break;
          case '90d':
            startDate.setDate(endDate.getDate() - 90);
            break;
          case '1y':
            startDate.setFullYear(endDate.getFullYear() - 1);
            break;
        }
        
        params.append('start_date', startDate.toISOString());
        params.append('end_date', endDate.toISOString());
      }
      
      if (exportFormat === 'json') {
        params.append('data_types', dataTypes.join(','));
        params.append('include_analysis', includeAnalysis.toString());
        url = `/export/json?${params.toString()}`;
      } else if (exportFormat === 'csv') {
        // For CSV, export each data type separately
        for (const dataType of dataTypes) {
          const csvParams = new URLSearchParams(params);
          csvParams.append('data_type', dataType);
          await downloadFile(`/export/csv?${csvParams.toString()}`);
        }
        setIsExporting(false);
        return;
      }
      
      await downloadFile(url);
      
    } catch (err) {
      console.error('Export failed:', err);
      alert('Export failed. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  const downloadFile = async (url) => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Download failed');
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      
      // Extract filename from Content-Disposition header
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = 'sukh_export';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      // Create download link
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up
      window.URL.revokeObjectURL(downloadUrl);
      
    } catch (err) {
      console.error('Download failed:', err);
      throw err;
    }
  };

  const handleDataTypeChange = (type, checked) => {
    if (checked) {
      setDataTypes([...dataTypes, type]);
    } else {
      setDataTypes(dataTypes.filter(t => t !== type));
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className={`w-full max-w-2xl rounded-lg shadow-xl ${
        darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold">Export Your Data</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Export Summary */}
          {exportSummary && (
            <div className={`p-4 rounded-lg ${
              darkMode ? 'bg-gray-700' : 'bg-gray-50'
            }`}>
              <h3 className="font-medium mb-3">Data Summary</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Mood Entries</div>
                  <div className="font-semibold">{exportSummary.total_mood_entries}</div>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Conversations</div>
                  <div className="font-semibold">{exportSummary.total_conversations}</div>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Messages</div>
                  <div className="font-semibold">{exportSummary.total_messages}</div>
                </div>
                <div>
                  <div className="text-gray-500 dark:text-gray-400">Journal Entries</div>
                  <div className="font-semibold">{exportSummary.total_journal_entries}</div>
                </div>
              </div>
            </div>
          )}

          {/* Export Format */}
          <div>
            <label className="block text-sm font-medium mb-2">Export Format</label>
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="json"
                  checked={exportFormat === 'json'}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="mr-2"
                />
                JSON (Complete data with analysis)
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="csv"
                  checked={exportFormat === 'csv'}
                  onChange={(e) => setExportFormat(e.target.value)}
                  className="mr-2"
                />
                CSV (Spreadsheet format)
              </label>
            </div>
          </div>

          {/* Data Types */}
          <div>
            <label className="block text-sm font-medium mb-2">Data to Export</label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={dataTypes.includes('mood_entries')}
                  onChange={(e) => handleDataTypeChange('mood_entries', e.target.checked)}
                  className="mr-2"
                />
                Mood Entries
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={dataTypes.includes('conversations')}
                  onChange={(e) => handleDataTypeChange('conversations', e.target.checked)}
                  className="mr-2"
                />
                Conversations & Messages
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={dataTypes.includes('journal_entries')}
                  onChange={(e) => handleDataTypeChange('journal_entries', e.target.checked)}
                  className="mr-2"
                />
                Journal Entries
              </label>
            </div>
          </div>

          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium mb-2">Date Range</label>
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className={`w-full p-2 border rounded-md ${
                darkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              }`}
            >
              <option value="all">All Time</option>
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="1y">Last Year</option>
              <option value="custom">Custom Range</option>
            </select>

            {dateRange === 'custom' && (
              <div className="mt-3 grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={customStartDate}
                    onChange={(e) => setCustomStartDate(e.target.value)}
                    className={`w-full p-2 border rounded-md text-sm ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">End Date</label>
                  <input
                    type="date"
                    value={customEndDate}
                    onChange={(e) => setCustomEndDate(e.target.value)}
                    className={`w-full p-2 border rounded-md text-sm ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    }`}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Include Analysis (JSON only) */}
          {exportFormat === 'json' && (
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={includeAnalysis}
                  onChange={(e) => setIncludeAnalysis(e.target.checked)}
                  className="mr-2"
                />
                Include analysis data (mood scores, sentiment, etc.)
              </label>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Your data will be downloaded to your device
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              Cancel
            </button>
            <button
              onClick={handleExport}
              disabled={isExporting || dataTypes.length === 0 || loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isExporting ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  Exporting...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Export Data
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataExport;