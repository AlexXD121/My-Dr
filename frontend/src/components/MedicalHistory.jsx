import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import apiService from '../services/api';
import MedicalDataExport from './MedicalDataExport';

const MedicalHistory = ({ isOpen, onClose, darkMode }) => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [stats, setStats] = useState(null);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [showExportModal, setShowExportModal] = useState(false);
  
  // Filters and search
  const [filters, setFilters] = useState({
    recordType: '',
    status: '',
    condition: '',
    provider: '',
    dateFrom: '',
    dateTo: '',
    search: '',
    tags: '',
    sortBy: 'date_recorded',
    sortOrder: 'desc'
  });
  
  // Pagination
  const [pagination, setPagination] = useState({
    limit: 20,
    offset: 0,
    hasMore: true
  });

  const [newRecord, setNewRecord] = useState({
    record_type: 'visit',
    title: '',
    description: '',
    date_recorded: new Date().toISOString().split('T')[0],
    healthcare_provider: '',
    provider_specialty: '',
    facility_name: '',
    facility_address: '',
    condition: '',
    icd_code: '',
    severity: '',
    status: 'active',
    medications: [],
    dosages: {},
    treatments: [],
    test_results: {},
    allergies: [],
    symptoms: [],
    vital_signs: {},
    follow_up_date: '',
    follow_up_instructions: '',
    referrals: [],
    notes: '',
    tags: [],
    priority: 'normal',
    is_private: true
  });

  // Load medical records
  const loadRecords = async (resetPagination = false) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      
      // Add filters
      Object.entries(filters).forEach(([key, value]) => {
        if (value) {
          params.append(key, value);
        }
      });
      
      // Add pagination
      if (resetPagination) {
        params.append('limit', pagination.limit);
        params.append('offset', 0);
      } else {
        params.append('limit', pagination.limit);
        params.append('offset', pagination.offset);
      }
      
      const response = await apiService.get(`/medical-history/records?${params.toString()}`);
      
      if (resetPagination) {
        setRecords(response);
        setPagination(prev => ({ ...prev, offset: 0 }));
      } else {
        setRecords(prev => [...prev, ...response]);
      }
      
      setPagination(prev => ({
        ...prev,
        hasMore: response.length === pagination.limit
      }));
      
    } catch (err) {
      console.error('Failed to load medical records:', err);
      setError('Failed to load medical records. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Load statistics
  const loadStats = async () => {
    try {
      const statsData = await apiService.get('/medical-history/stats');
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load medical history stats:', err);
    }
  };

  // Load data when component opens
  useEffect(() => {
    if (isOpen) {
      loadRecords(true);
      loadStats();
    }
  }, [isOpen]);

  // Reload when filters change
  useEffect(() => {
    if (isOpen) {
      loadRecords(true);
    }
  }, [filters]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);
      
      // Prepare data
      const recordData = {
        ...newRecord,
        date_recorded: new Date(newRecord.date_recorded).toISOString(),
        follow_up_date: newRecord.follow_up_date ? new Date(newRecord.follow_up_date).toISOString() : null,
        tags: newRecord.tags.filter(tag => tag.trim()),
        medications: newRecord.medications.filter(med => med.name?.trim()),
        treatments: newRecord.treatments.filter(treatment => treatment.trim()),
        allergies: newRecord.allergies.filter(allergy => allergy.trim()),
        symptoms: newRecord.symptoms.filter(symptom => symptom.trim()),
        referrals: newRecord.referrals.filter(referral => referral.trim())
      };
      
      let savedRecord;
      if (editingRecord) {
        savedRecord = await apiService.put(`/medical-history/records/${editingRecord.id}`, recordData);
        setRecords(prev => prev.map(r => r.id === editingRecord.id ? savedRecord : r));
      } else {
        savedRecord = await apiService.post('/medical-history/records', recordData);
        setRecords(prev => [savedRecord, ...prev]);
      }
      
      // Reset form
      setNewRecord({
        record_type: 'visit',
        title: '',
        description: '',
        date_recorded: new Date().toISOString().split('T')[0],
        healthcare_provider: '',
        provider_specialty: '',
        facility_name: '',
        facility_address: '',
        condition: '',
        icd_code: '',
        severity: '',
        status: 'active',
        medications: [],
        dosages: {},
        treatments: [],
        test_results: {},
        allergies: [],
        symptoms: [],
        vital_signs: {},
        follow_up_date: '',
        follow_up_instructions: '',
        referrals: [],
        notes: '',
        tags: [],
        priority: 'normal',
        is_private: true
      });
      
      setShowAddForm(false);
      setEditingRecord(null);
      loadStats(); // Refresh stats
      
    } catch (err) {
      console.error('Failed to save medical record:', err);
      setError('Failed to save medical record. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle record deletion
  const handleDelete = async (recordId) => {
    if (!confirm('Are you sure you want to delete this medical record? This action cannot be undone.')) {
      return;
    }
    
    try {
      setLoading(true);
      await apiService.delete(`/medical-history/records/${recordId}`);
      setRecords(prev => prev.filter(r => r.id !== recordId));
      setSelectedRecord(null);
      loadStats(); // Refresh stats
    } catch (err) {
      console.error('Failed to delete medical record:', err);
      setError('Failed to delete medical record. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle edit
  const handleEdit = (record) => {
    setEditingRecord(record);
    setNewRecord({
      record_type: record.record_type,
      title: record.title,
      description: record.description || '',
      date_recorded: new Date(record.date_recorded).toISOString().split('T')[0],
      healthcare_provider: record.healthcare_provider || '',
      provider_specialty: record.provider_specialty || '',
      facility_name: record.facility_name || '',
      facility_address: record.facility_address || '',
      condition: record.condition || '',
      icd_code: record.icd_code || '',
      severity: record.severity || '',
      status: record.status,
      medications: record.medications || [],
      dosages: record.dosages || {},
      treatments: record.treatments || [],
      test_results: record.test_results || {},
      allergies: record.allergies || [],
      symptoms: record.symptoms || [],
      vital_signs: record.vital_signs || {},
      follow_up_date: record.follow_up_date ? new Date(record.follow_up_date).toISOString().split('T')[0] : '',
      follow_up_instructions: record.follow_up_instructions || '',
      referrals: record.referrals || [],
      notes: record.notes || '',
      tags: record.tags || [],
      priority: record.priority,
      is_private: record.is_private
    });
    setShowAddForm(true);
  };

  // Add medication
  const addMedication = () => {
    setNewRecord(prev => ({
      ...prev,
      medications: [...prev.medications, { name: '', dosage: '', frequency: '', notes: '' }]
    }));
  };

  // Remove medication
  const removeMedication = (index) => {
    setNewRecord(prev => ({
      ...prev,
      medications: prev.medications.filter((_, i) => i !== index)
    }));
  };

  // Update medication
  const updateMedication = (index, field, value) => {
    setNewRecord(prev => ({
      ...prev,
      medications: prev.medications.map((med, i) => 
        i === index ? { ...med, [field]: value } : med
      )
    }));
  };

  // Add tag
  const addTag = (tag) => {
    if (tag && !newRecord.tags.includes(tag)) {
      setNewRecord(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
  };

  // Remove tag
  const removeTag = (tagToRemove) => {
    setNewRecord(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  // Format date for display
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Get priority color
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'normal': return 'text-blue-600 bg-blue-100';
      case 'low': return 'text-gray-600 bg-gray-100';
      default: return 'text-blue-600 bg-blue-100';
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-100';
      case 'resolved': return 'text-blue-600 bg-blue-100';
      case 'chronic': return 'text-yellow-600 bg-yellow-100';
      case 'monitoring': return 'text-purple-600 bg-purple-100';
      case 'inactive': return 'text-gray-600 bg-gray-100';
      default: return 'text-green-600 bg-green-100';
    }
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`flex-1 ${darkMode ? 'bg-gray-900' : 'bg-white'} overflow-y-auto`}
    >
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              📋 Medical History
            </h1>
            {stats && (
              <p className={`text-sm mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                {stats.total_records} records • {stats.follow_ups_due} follow-ups due
              </p>
            )}
          </div>

        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} border ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {stats.total_records}
              </h3>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                Total Records
              </p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} border ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {stats.recent_records_count}
              </h3>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                Recent (30 days)
              </p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} border ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {stats.follow_ups_due}
              </h3>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                Follow-ups Due
              </p>
            </div>
            <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} border ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {Object.keys(stats.records_by_type).length}
              </h3>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                Record Types
              </p>
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="flex flex-wrap gap-4 mb-6">
          <button
            onClick={() => {
              setEditingRecord(null);
              setShowAddForm(true);
            }}
            className="bg-gradient-to-r from-blue-600 to-gray-800 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-gray-900 transition-all"
          >
            Add Record
          </button>
          
          <button
            onClick={() => setShowExportModal(true)}
            className="bg-gradient-to-r from-green-600 to-blue-600 text-white px-4 py-2 rounded-lg hover:from-green-700 hover:to-blue-700 transition-all"
          >
            Export & Share
          </button>
          
          {/* Search */}
          <input
            type="text"
            placeholder="Search records..."
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            className={`px-3 py-2 rounded-lg border ${
              darkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-800'
            }`}
          />
          
          {/* Filters */}
          <select
            value={filters.recordType}
            onChange={(e) => setFilters(prev => ({ ...prev, recordType: e.target.value }))}
            className={`px-3 py-2 rounded-lg border ${
              darkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-800'
            }`}
          >
            <option value="">All Types</option>
            <option value="visit">Visit</option>
            <option value="diagnosis">Diagnosis</option>
            <option value="medication">Medication</option>
            <option value="test">Test</option>
            <option value="procedure">Procedure</option>
            <option value="vaccination">Vaccination</option>
            <option value="allergy">Allergy</option>
          </select>
          
          <select
            value={filters.status}
            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
            className={`px-3 py-2 rounded-lg border ${
              darkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-800'
            }`}
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="resolved">Resolved</option>
            <option value="chronic">Chronic</option>
            <option value="monitoring">Monitoring</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>

        {/* Add/Edit Form */}
        <AnimatePresence>
          {showAddForm && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className={`mb-6 p-6 rounded-lg border ${darkMode ? 'bg-gray-800 border-gray-600' : 'bg-gray-50 border-gray-200'}`}
            >
              <h3 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {editingRecord ? 'Edit Medical Record' : 'Add New Medical Record'}
              </h3>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Record Type *
                    </label>
                    <select
                      value={newRecord.record_type}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, record_type: e.target.value }))}
                      required
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                    >
                      <option value="visit">Visit</option>
                      <option value="diagnosis">Diagnosis</option>
                      <option value="medication">Medication</option>
                      <option value="test">Test</option>
                      <option value="procedure">Procedure</option>
                      <option value="vaccination">Vaccination</option>
                      <option value="allergy">Allergy</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Title *
                    </label>
                    <input
                      type="text"
                      value={newRecord.title}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, title: e.target.value }))}
                      required
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                      placeholder="Brief title or summary"
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Date *
                    </label>
                    <input
                      type="date"
                      value={newRecord.date_recorded}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, date_recorded: e.target.value }))}
                      required
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                    />
                  </div>
                </div>

                {/* Healthcare Provider Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Healthcare Provider
                    </label>
                    <input
                      type="text"
                      value={newRecord.healthcare_provider}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, healthcare_provider: e.target.value }))}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                      placeholder="Dr. Smith, City Hospital"
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Specialty
                    </label>
                    <input
                      type="text"
                      value={newRecord.provider_specialty}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, provider_specialty: e.target.value }))}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                      placeholder="Cardiology, Family Medicine"
                    />
                  </div>
                </div>

                {/* Medical Details */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Condition/Diagnosis
                    </label>
                    <input
                      type="text"
                      value={newRecord.condition}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, condition: e.target.value }))}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                      placeholder="Hypertension, Diabetes"
                    />
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Severity
                    </label>
                    <select
                      value={newRecord.severity}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, severity: e.target.value }))}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                    >
                      <option value="">Select Severity</option>
                      <option value="mild">Mild</option>
                      <option value="moderate">Moderate</option>
                      <option value="severe">Severe</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Status
                    </label>
                    <select
                      value={newRecord.status}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, status: e.target.value }))}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                    >
                      <option value="active">Active</option>
                      <option value="resolved">Resolved</option>
                      <option value="chronic">Chronic</option>
                      <option value="monitoring">Monitoring</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Priority
                    </label>
                    <select
                      value={newRecord.priority}
                      onChange={(e) => setNewRecord(prev => ({ ...prev, priority: e.target.value }))}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                    >
                      <option value="low">Low</option>
                      <option value="normal">Normal</option>
                      <option value="high">High</option>
                      <option value="urgent">Urgent</option>
                    </select>
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Description
                  </label>
                  <textarea
                    value={newRecord.description}
                    onChange={(e) => setNewRecord(prev => ({ ...prev, description: e.target.value }))}
                    rows={3}
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-800'
                    }`}
                    placeholder="Detailed description of the medical event..."
                  />
                </div>

                {/* Medications */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <label className={`block text-sm font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Medications
                    </label>
                    <button
                      type="button"
                      onClick={addMedication}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      + Add Medication
                    </button>
                  </div>
                  {newRecord.medications.map((medication, index) => (
                    <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-2 mb-2">
                      <input
                        type="text"
                        placeholder="Medication name"
                        value={medication.name || ''}
                        onChange={(e) => updateMedication(index, 'name', e.target.value)}
                        className={`p-2 rounded border ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-800'
                        }`}
                      />
                      <input
                        type="text"
                        placeholder="Dosage"
                        value={medication.dosage || ''}
                        onChange={(e) => updateMedication(index, 'dosage', e.target.value)}
                        className={`p-2 rounded border ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-800'
                        }`}
                      />
                      <input
                        type="text"
                        placeholder="Frequency"
                        value={medication.frequency || ''}
                        onChange={(e) => updateMedication(index, 'frequency', e.target.value)}
                        className={`p-2 rounded border ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-800'
                        }`}
                      />
                      <button
                        type="button"
                        onClick={() => removeMedication(index)}
                        className="text-red-600 hover:text-red-800 px-2"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>

                {/* Notes */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Additional Notes
                  </label>
                  <textarea
                    value={newRecord.notes}
                    onChange={(e) => setNewRecord(prev => ({ ...prev, notes: e.target.value }))}
                    rows={3}
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-800'
                    }`}
                    placeholder="Any additional notes or observations..."
                  />
                </div>

                {/* Form Actions */}
                <div className="flex gap-2 pt-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-gradient-to-r from-blue-600 to-gray-800 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-gray-900 transition-all disabled:opacity-50"
                  >
                    {loading ? 'Saving...' : (editingRecord ? 'Update Record' : 'Save Record')}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowAddForm(false);
                      setEditingRecord(null);
                    }}
                    className={`px-6 py-2 rounded-lg ${darkMode ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'} transition-colors`}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Records List */}
        <div className="space-y-4">
          {loading && records.length === 0 ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className={`mt-2 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Loading medical records...</p>
            </div>
          ) : records.length === 0 ? (
            <div className="text-center py-8">
              <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                No medical records found. Add your first record to get started.
              </p>
            </div>
          ) : (
            records.map((record) => (
              <motion.div
                key={record.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-4 rounded-lg border ${darkMode ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-200'} hover:shadow-lg transition-shadow cursor-pointer`}
                onClick={() => setSelectedRecord(record)}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                        {record.title}
                      </h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(record.priority)}`}>
                        {record.priority}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(record.status)}`}>
                        {record.status}
                      </span>
                    </div>
                    <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                      {record.record_type.charAt(0).toUpperCase() + record.record_type.slice(1)} • {formatDate(record.date_recorded)}
                    </p>
                    {record.healthcare_provider && (
                      <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                        <strong>Provider:</strong> {record.healthcare_provider}
                      </p>
                    )}
                    {record.condition && (
                      <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                        <strong>Condition:</strong> {record.condition}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit(record);
                      }}
                      className="text-blue-600 hover:text-blue-800 p-1"
                      title="Edit record"
                    >
                      ✏️
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(record.id);
                      }}
                      className="text-red-600 hover:text-red-800 p-1"
                      title="Delete record"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                
                {record.description && (
                  <p className={`text-sm mt-2 ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    {record.description.length > 150 
                      ? `${record.description.substring(0, 150)}...` 
                      : record.description
                    }
                  </p>
                )}
                
                {record.tags && record.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {record.tags.map((tag, index) => (
                      <span
                        key={index}
                        className={`px-2 py-1 rounded-full text-xs ${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-700'}`}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </motion.div>
            ))
          )}
        </div>

        {/* Load More Button */}
        {pagination.hasMore && !loading && (
          <div className="text-center mt-6">
            <button
              onClick={() => {
                setPagination(prev => ({ ...prev, offset: prev.offset + prev.limit }));
                loadRecords();
              }}
              className="bg-gradient-to-r from-blue-600 to-gray-800 text-white px-6 py-2 rounded-lg hover:from-blue-700 hover:to-gray-900 transition-all"
            >
              Load More Records
            </button>
          </div>
        )}

        {/* Record Detail Modal */}
        <AnimatePresence>
          {selectedRecord && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60 p-4"
              onClick={() => setSelectedRecord(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className={`max-w-2xl w-full max-h-[80vh] overflow-y-auto rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} p-6`}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex justify-between items-start mb-4">
                  <h2 className={`text-xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                    {selectedRecord.title}
                  </h2>
                  <button
                    onClick={() => setSelectedRecord(null)}
                    className={`text-gray-500 hover:text-gray-700 ${darkMode ? 'hover:text-gray-300' : ''}`}
                  >
                    ✕
                  </button>
                </div>
                
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <strong className={darkMode ? 'text-gray-300' : 'text-gray-700'}>Type:</strong>
                      <p className={darkMode ? 'text-white' : 'text-gray-900'}>
                        {selectedRecord.record_type.charAt(0).toUpperCase() + selectedRecord.record_type.slice(1)}
                      </p>
                    </div>
                    <div>
                      <strong className={darkMode ? 'text-gray-300' : 'text-gray-700'}>Date:</strong>
                      <p className={darkMode ? 'text-white' : 'text-gray-900'}>
                        {formatDate(selectedRecord.date_recorded)}
                      </p>
                    </div>
                  </div>
                  
                  {selectedRecord.description && (
                    <div>
                      <strong className={darkMode ? 'text-gray-300' : 'text-gray-700'}>Description:</strong>
                      <p className={darkMode ? 'text-white' : 'text-gray-900'}>
                        {selectedRecord.description}
                      </p>
                    </div>
                  )}
                  
                  {selectedRecord.healthcare_provider && (
                    <div>
                      <strong className={darkMode ? 'text-gray-300' : 'text-gray-700'}>Healthcare Provider:</strong>
                      <p className={darkMode ? 'text-white' : 'text-gray-900'}>
                        {selectedRecord.healthcare_provider}
                        {selectedRecord.provider_specialty && ` (${selectedRecord.provider_specialty})`}
                      </p>
                    </div>
                  )}
                  
                  {selectedRecord.condition && (
                    <div>
                      <strong className={darkMode ? 'text-gray-300' : 'text-gray-700'}>Condition:</strong>
                      <p className={darkMode ? 'text-white' : 'text-gray-900'}>
                        {selectedRecord.condition}
                      </p>
                    </div>
                  )}
                  
                  {selectedRecord.medications && selectedRecord.medications.length > 0 && (
                    <div>
                      <strong className={darkMode ? 'text-gray-300' : 'text-gray-700'}>Medications:</strong>
                      <ul className={`list-disc list-inside ${darkMode ? 'text-white' : 'text-gray-900'}`}>
                        {selectedRecord.medications.map((med, index) => (
                          <li key={index}>
                            {med.name} {med.dosage && `- ${med.dosage}`} {med.frequency && `(${med.frequency})`}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {selectedRecord.notes && (
                    <div>
                      <strong className={darkMode ? 'text-gray-300' : 'text-gray-700'}>Notes:</strong>
                      <p className={darkMode ? 'text-white' : 'text-gray-900'}>
                        {selectedRecord.notes}
                      </p>
                    </div>
                  )}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Export Modal */}
        <MedicalDataExport
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
          darkMode={darkMode}
        />
      </div>
    </motion.div>
  );
};

export default MedicalHistory;