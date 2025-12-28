import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import apiService from '../services/api';

const MedicalDataExport = ({ isOpen, onClose, darkMode }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [records, setRecords] = useState([]);
  const [selectedRecords, setSelectedRecords] = useState([]);
  const [exportOptions, setExportOptions] = useState({
    format: 'json',
    dateFrom: '',
    dateTo: '',
    recordTypes: [],
    includePrivate: true,
    summaryOnly: false
  });
  
  const [shareOptions, setShareOptions] = useState({
    recordIds: [],
    includeSensitive: false,
    expiryHours: 24,
    recipientEmail: ''
  });
  
  const [activeTab, setActiveTab] = useState('export');
  const [backupData, setBackupData] = useState(null);

  // Load records for selection
  useEffect(() => {
    if (isOpen) {
      loadRecords();
    }
  }, [isOpen]);

  const loadRecords = async () => {
    try {
      setLoading(true);
      const response = await apiService.getMedicalRecords({ limit: 100 });
      setRecords(response);
    } catch (err) {
      console.error('Failed to load records:', err);
      setError('Failed to load medical records');
    } finally {
      setLoading(false);
    }
  };

  // Handle export
  const handleExport = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const params = new URLSearchParams();
      params.append('format', exportOptions.format);
      
      if (exportOptions.dateFrom) {
        params.append('date_from', exportOptions.dateFrom);
      }
      
      if (exportOptions.dateTo) {
        params.append('date_to', exportOptions.dateTo);
      }
      
      if (exportOptions.recordTypes.length > 0) {
        params.append('record_types', exportOptions.recordTypes.join(','));
      }
      
      params.append('include_private', exportOptions.includePrivate);
      params.append('summary_only', exportOptions.summaryOnly);

      const response = await fetch(`${apiService.baseURL}/medical-history/export?${params.toString()}`, {
        method: 'GET',
        headers: apiService.getHeaders()
      });

      if (!response.ok) {
        throw new Error(`Export failed: ${response.statusText}`);
      }

      // Handle different response types
      if (exportOptions.format === 'json') {
        const data = await response.json();
        downloadJSON(data, `medical_history_${new Date().toISOString().split('T')[0]}.json`);
      } else {
        // For PDF and CSV, handle as blob
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `medical_history_${new Date().toISOString().split('T')[0]}.${exportOptions.format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }

      setSuccess(`Medical history exported successfully as ${exportOptions.format.toUpperCase()}`);
      
    } catch (err) {
      console.error('Export failed:', err);
      setError('Failed to export medical history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Download JSON data
  const downloadJSON = (data, filename) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  // Handle share creation
  const handleCreateShare = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const shareData = {
        record_ids: shareOptions.recordIds,
        include_sensitive: shareOptions.includeSensitive,
        expiry_hours: shareOptions.expiryHours,
        recipient_email: shareOptions.recipientEmail || null
      };

      const response = await apiService.post('/medical-history/share', shareData);
      
      setSuccess(`Shareable link created successfully. Expires: ${new Date(response.expiry_date).toLocaleString()}`);
      
      // Copy share URL to clipboard
      const shareUrl = `${window.location.origin}${response.share_url}`;
      await navigator.clipboard.writeText(shareUrl);
      
    } catch (err) {
      console.error('Failed to create share:', err);
      setError('Failed to create shareable link. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle backup creation
  const handleCreateBackup = async () => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const response = await apiService.get('/medical-history/backup?include_attachments=false');
      setBackupData(response);
      
      // Download backup
      downloadJSON(response, `medical_backup_${new Date().toISOString().split('T')[0]}.json`);
      
      setSuccess('Complete backup created and downloaded successfully');
      
    } catch (err) {
      console.error('Failed to create backup:', err);
      setError('Failed to create backup. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle backup restore
  const handleRestoreBackup = async (file) => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(null);

      const text = await file.text();
      const backupData = JSON.parse(text);

      const response = await apiService.post('/medical-history/restore', backupData);
      
      setSuccess(`Backup restored successfully. ${response.restored_records} records restored, ${response.skipped_records} skipped.`);
      
    } catch (err) {
      console.error('Failed to restore backup:', err);
      setError('Failed to restore backup. Please check the file format and try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle record selection
  const toggleRecordSelection = (recordId) => {
    setSelectedRecords(prev => 
      prev.includes(recordId) 
        ? prev.filter(id => id !== recordId)
        : [...prev, recordId]
    );
  };

  // Select all records
  const selectAllRecords = () => {
    setSelectedRecords(records.map(r => r.id));
  };

  // Clear selection
  const clearSelection = () => {
    setSelectedRecords([]);
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`fixed inset-0 z-50 ${darkMode ? 'bg-gray-900' : 'bg-white'} overflow-y-auto`}
    >
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            📤 Medical Data Export & Sharing
          </h1>
          <button
            onClick={onClose}
            className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'} transition-colors`}
          >
            Close
          </button>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
            {success}
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-1 mb-6">
          {['export', 'share', 'backup'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : darkMode
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Export Tab */}
        {activeTab === 'export' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-6 rounded-lg border ${darkMode ? 'bg-gray-800 border-gray-600' : 'bg-gray-50 border-gray-200'}`}
          >
            <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              Export Medical History
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Export Options */}
              <div className="space-y-4">
                <div>
                  <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Export Format
                  </label>
                  <select
                    value={exportOptions.format}
                    onChange={(e) => setExportOptions(prev => ({ ...prev, format: e.target.value }))}
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-800'
                    }`}
                  >
                    <option value="json">JSON (Complete Data)</option>
                    <option value="pdf">PDF (Formatted Report)</option>
                    <option value="csv">CSV (Spreadsheet)</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      From Date
                    </label>
                    <input
                      type="date"
                      value={exportOptions.dateFrom}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, dateFrom: e.target.value }))}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                    />
                  </div>
                  <div>
                    <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      To Date
                    </label>
                    <input
                      type="date"
                      value={exportOptions.dateTo}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, dateTo: e.target.value }))}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                    />
                  </div>
                </div>

                <div>
                  <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Record Types
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {['visit', 'diagnosis', 'medication', 'test', 'procedure', 'vaccination', 'allergy'].map((type) => (
                      <label key={type} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={exportOptions.recordTypes.includes(type)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setExportOptions(prev => ({ 
                                ...prev, 
                                recordTypes: [...prev.recordTypes, type] 
                              }));
                            } else {
                              setExportOptions(prev => ({ 
                                ...prev, 
                                recordTypes: prev.recordTypes.filter(t => t !== type) 
                              }));
                            }
                          }}
                          className="mr-2"
                        />
                        <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={exportOptions.includePrivate}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, includePrivate: e.target.checked }))}
                      className="mr-2"
                    />
                    <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Include private records
                    </span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={exportOptions.summaryOnly}
                      onChange={(e) => setExportOptions(prev => ({ ...prev, summaryOnly: e.target.checked }))}
                      className="mr-2"
                    />
                    <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Summary only (exclude detailed notes)
                    </span>
                  </label>
                </div>
              </div>

              {/* Export Preview */}
              <div>
                <h3 className={`text-lg font-medium mb-3 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                  Export Preview
                </h3>
                <div className={`p-4 rounded-lg border ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'}`}>
                  <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Format: <strong>{exportOptions.format.toUpperCase()}</strong>
                  </p>
                  <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Date Range: {exportOptions.dateFrom || 'All'} to {exportOptions.dateTo || 'All'}
                  </p>
                  <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Record Types: {exportOptions.recordTypes.length > 0 ? exportOptions.recordTypes.join(', ') : 'All'}
                  </p>
                  <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Privacy: {exportOptions.includePrivate ? 'Include private' : 'Public only'}
                  </p>
                  <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Detail Level: {exportOptions.summaryOnly ? 'Summary' : 'Complete'}
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={handleExport}
                disabled={loading}
                className="bg-gradient-to-r from-blue-600 to-gray-800 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-gray-900 transition-all disabled:opacity-50"
              >
                {loading ? 'Exporting...' : 'Export Medical History'}
              </button>
            </div>
          </motion.div>
        )}

        {/* Share Tab */}
        {activeTab === 'share' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-6 rounded-lg border ${darkMode ? 'bg-gray-800 border-gray-600' : 'bg-gray-50 border-gray-200'}`}
          >
            <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              Share Medical Summary
            </h2>

            <div className="space-y-6">
              {/* Record Selection */}
              <div>
                <div className="flex justify-between items-center mb-3">
                  <label className={`text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Select Records to Share ({selectedRecords.length} selected)
                  </label>
                  <div className="space-x-2">
                    <button
                      onClick={selectAllRecords}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Select All
                    </button>
                    <button
                      onClick={clearSelection}
                      className="text-gray-600 hover:text-gray-800 text-sm"
                    >
                      Clear
                    </button>
                  </div>
                </div>
                
                <div className={`max-h-60 overflow-y-auto border rounded-lg ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
                  {records.map((record) => (
                    <label
                      key={record.id}
                      className={`flex items-center p-3 border-b ${darkMode ? 'border-gray-600 hover:bg-gray-700' : 'border-gray-200 hover:bg-gray-50'} cursor-pointer`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedRecords.includes(record.id)}
                        onChange={() => toggleRecordSelection(record.id)}
                        className="mr-3"
                      />
                      <div className="flex-1">
                        <p className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                          {record.title}
                        </p>
                        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                          {record.record_type} • {new Date(record.date_recorded).toLocaleDateString()}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Share Options */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Recipient Email (Optional)
                  </label>
                  <input
                    type="email"
                    value={shareOptions.recipientEmail}
                    onChange={(e) => setShareOptions(prev => ({ ...prev, recipientEmail: e.target.value }))}
                    placeholder="doctor@hospital.com"
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-800'
                    }`}
                  />
                </div>
                
                <div>
                  <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Link Expiry (Hours)
                  </label>
                  <select
                    value={shareOptions.expiryHours}
                    onChange={(e) => setShareOptions(prev => ({ ...prev, expiryHours: parseInt(e.target.value) }))}
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-800'
                    }`}
                  >
                    <option value={1}>1 Hour</option>
                    <option value={6}>6 Hours</option>
                    <option value={24}>24 Hours</option>
                    <option value={72}>3 Days</option>
                    <option value={168}>1 Week</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={shareOptions.includeSensitive}
                    onChange={(e) => setShareOptions(prev => ({ ...prev, includeSensitive: e.target.checked }))}
                    className="mr-2"
                  />
                  <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Include sensitive/private information
                  </span>
                </label>
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={() => {
                  setShareOptions(prev => ({ ...prev, recordIds: selectedRecords }));
                  handleCreateShare();
                }}
                disabled={loading || selectedRecords.length === 0}
                className="bg-gradient-to-r from-green-600 to-blue-600 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-blue-700 transition-all disabled:opacity-50"
              >
                {loading ? 'Creating Share Link...' : 'Create Shareable Link'}
              </button>
            </div>
          </motion.div>
        )}

        {/* Backup Tab */}
        {activeTab === 'backup' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-6 rounded-lg border ${darkMode ? 'bg-gray-800 border-gray-600' : 'bg-gray-50 border-gray-200'}`}
          >
            <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              Backup & Restore
            </h2>

            <div className="space-y-6">
              {/* Create Backup */}
              <div className={`p-4 rounded-lg border ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'}`}>
                <h3 className={`text-lg font-medium mb-3 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                  Create Complete Backup
                </h3>
                <p className={`text-sm mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Download a complete backup of all your medical data including user profile, 
                  medical records, and metadata. This backup can be used to restore your data later.
                </p>
                <button
                  onClick={handleCreateBackup}
                  disabled={loading}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all disabled:opacity-50"
                >
                  {loading ? 'Creating Backup...' : 'Create & Download Backup'}
                </button>
              </div>

              {/* Restore Backup */}
              <div className={`p-4 rounded-lg border ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-white border-gray-200'}`}>
                <h3 className={`text-lg font-medium mb-3 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                  Restore from Backup
                </h3>
                <p className={`text-sm mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                  Upload a previously created backup file to restore your medical data. 
                  Existing records with the same ID will be skipped unless you choose to overwrite.
                </p>
                <input
                  type="file"
                  accept=".json"
                  onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) {
                      handleRestoreBackup(file);
                    }
                  }}
                  className={`w-full p-3 rounded-lg border ${
                    darkMode 
                      ? 'bg-gray-600 border-gray-500 text-white' 
                      : 'bg-white border-gray-300 text-gray-800'
                  }`}
                />
              </div>

              {/* Privacy Notice */}
              <div className={`p-4 rounded-lg border-l-4 border-yellow-500 ${darkMode ? 'bg-yellow-900 bg-opacity-20' : 'bg-yellow-50'}`}>
                <h4 className={`font-medium mb-2 ${darkMode ? 'text-yellow-200' : 'text-yellow-800'}`}>
                  Privacy & Security Notice
                </h4>
                <ul className={`text-sm space-y-1 ${darkMode ? 'text-yellow-300' : 'text-yellow-700'}`}>
                  <li>• Backup files contain sensitive medical information</li>
                  <li>• Store backup files securely and encrypt if possible</li>
                  <li>• Shared links expire automatically for security</li>
                  <li>• Only share medical data with trusted healthcare providers</li>
                  <li>• You can revoke shared access at any time</li>
                </ul>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default MedicalDataExport;