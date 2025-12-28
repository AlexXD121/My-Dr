import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import apiService from '../services/api';

const MedicationManager = ({ isOpen, onClose, darkMode }) => {
  const [medications, setMedications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingMedication, setEditingMedication] = useState(null);
  const [searchSuggestions, setSearchSuggestions] = useState([]);
  const [doseHistory, setDoseHistory] = useState({});
  const [showDoseHistory, setShowDoseHistory] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    medication_name: '',
    dosage: '',
    frequency: '',
    instructions: '',
    prescribed_by: '',
    start_date: '',
    end_date: '',
    schedule_times: [],
    reminder_enabled: true
  });

  useEffect(() => {
    if (isOpen) {
      loadMedications();
      seedDatabaseIfNeeded();
    }
  }, [isOpen]);

  const seedDatabaseIfNeeded = async () => {
    try {
      await apiService.post('/medications/seed-database');
    } catch (error) {
      console.log('Database seeding skipped (likely already seeded)');
    }
  };

  const loadMedications = async () => {
    setLoading(true);
    try {
      const response = await apiService.get('/medications/user-medications?include_inactive=true');
      setMedications(response.medications || []);
    } catch (error) {
      setError('Failed to load medications');
      console.error('Failed to load medications:', error);
    } finally {
      setLoading(false);
    }
  };

  const searchMedications = async (query) => {
    if (query.length < 2) {
      setSearchSuggestions([]);
      return;
    }

    try {
      const response = await apiService.get(`/medications/search?query=${encodeURIComponent(query)}&limit=10`);
      setSearchSuggestions(response.medications || []);
    } catch (error) {
      console.error('Failed to search medications:', error);
      setSearchSuggestions([]);
    }
  };

  const handleFormChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    if (field === 'medication_name' && value.length >= 2) {
      searchMedications(value);
    } else if (field === 'medication_name') {
      setSearchSuggestions([]);
    }
  };

  const selectSuggestion = (medication) => {
    setFormData(prev => ({ ...prev, medication_name: medication.name }));
    setSearchSuggestions([]);
  };

  const resetForm = () => {
    setFormData({
      medication_name: '',
      dosage: '',
      frequency: '',
      instructions: '',
      prescribed_by: '',
      start_date: '',
      end_date: '',
      schedule_times: [],
      reminder_enabled: true
    });
    setSearchSuggestions([]);
    setEditingMedication(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (editingMedication) {
        // Update existing medication
        await apiService.put(`/medications/user-medications/${editingMedication.id}`, {
          dosage: formData.dosage,
          frequency: formData.frequency,
          instructions: formData.instructions,
          status: formData.status,
          schedule_times: formData.schedule_times,
          reminder_enabled: formData.reminder_enabled,
          patient_notes: formData.patient_notes
        });
        setSuccess('Medication updated successfully');
      } else {
        // Add new medication
        await apiService.post('/medications/user-medications', formData);
        setSuccess('Medication added successfully');
      }
      
      resetForm();
      setShowAddForm(false);
      loadMedications();
    } catch (error) {
      setError(error.message || 'Failed to save medication');
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (medication) => {
    setEditingMedication(medication);
    setFormData({
      medication_name: medication.medication?.name || '',
      dosage: medication.dosage || '',
      frequency: medication.frequency || '',
      instructions: medication.instructions || '',
      prescribed_by: medication.prescribed_by || '',
      start_date: medication.start_date ? medication.start_date.split('T')[0] : '',
      end_date: medication.end_date ? medication.end_date.split('T')[0] : '',
      schedule_times: medication.schedule_times || [],
      reminder_enabled: medication.reminder_enabled ?? true,
      status: medication.status || 'active',
      patient_notes: medication.patient_notes || ''
    });
    setShowAddForm(true);
  };

  const handleDelete = async (medicationId) => {
    if (!confirm('Are you sure you want to delete this medication?')) return;

    setLoading(true);
    try {
      await apiService.delete(`/medications/user-medications/${medicationId}`);
      setSuccess('Medication deleted successfully');
      loadMedications();
    } catch (error) {
      setError('Failed to delete medication');
    } finally {
      setLoading(false);
    }
  };

  const logDose = async (userMedicationId, status) => {
    try {
      await apiService.post('/medications/dose-log', {
        user_medication_id: userMedicationId,
        status: status,
        actual_time: new Date().toISOString()
      });
      setSuccess(`Dose logged as ${status}`);
      loadMedications(); // Refresh to update adherence stats
    } catch (error) {
      setError('Failed to log dose');
    }
  };

  const loadDoseHistory = async (userMedicationId) => {
    try {
      const response = await apiService.get(`/medications/dose-history/${userMedicationId}?days=30`);
      setDoseHistory(prev => ({ ...prev, [userMedicationId]: response }));
      setShowDoseHistory(userMedicationId);
    } catch (error) {
      setError('Failed to load dose history');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      active: darkMode ? 'bg-green-900 text-green-200' : 'bg-green-100 text-green-800',
      paused: darkMode ? 'bg-yellow-900 text-yellow-200' : 'bg-yellow-100 text-yellow-800',
      discontinued: darkMode ? 'bg-red-900 text-red-200' : 'bg-red-100 text-red-800',
      completed: darkMode ? 'bg-blue-900 text-blue-200' : 'bg-blue-100 text-blue-800'
    };
    return colors[status] || colors.active;
  };

  const getAdherenceColor = (percentage) => {
    if (percentage >= 90) return darkMode ? 'text-green-400' : 'text-green-600';
    if (percentage >= 70) return darkMode ? 'text-yellow-400' : 'text-yellow-600';
    return darkMode ? 'text-red-400' : 'text-red-600';
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`fixed inset-0 z-50 ${darkMode ? 'bg-gray-900' : 'bg-white'} overflow-y-auto`}
    >
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex justify-between items-center mb-6">
          <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            💊 Medication Manager
          </h1>
          <button
            onClick={onClose}
            className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'} transition-colors`}
          >
            Close
          </button>
        </div>

        {/* Success/Error Messages */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`mb-4 p-3 rounded-lg border ${darkMode ? 'bg-red-900 border-red-700 text-red-200' : 'bg-red-100 border-red-300 text-red-800'}`}
            >
              ⚠️ {error}
              <button
                onClick={() => setError(null)}
                className="float-right text-lg leading-none"
              >
                ×
              </button>
            </motion.div>
          )}
          
          {success && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`mb-4 p-3 rounded-lg border ${darkMode ? 'bg-green-900 border-green-700 text-green-200' : 'bg-green-100 border-green-300 text-green-800'}`}
            >
              ✅ {success}
              <button
                onClick={() => setSuccess(null)}
                className="float-right text-lg leading-none"
              >
                ×
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Add Medication Button */}
        <div className="mb-6">
          <button
            onClick={() => {
              setShowAddForm(!showAddForm);
              if (!showAddForm) resetForm();
            }}
            className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all"
          >
            {showAddForm ? 'Cancel' : '+ Add Medication'}
          </button>
        </div>

        {/* Add/Edit Medication Form */}
        <AnimatePresence>
          {showAddForm && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className={`mb-6 p-6 rounded-lg border ${darkMode ? 'bg-gray-800 border-gray-600' : 'bg-gray-50 border-gray-200'}`}
            >
              <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {editingMedication ? 'Edit Medication' : 'Add New Medication'}
              </h2>
              
              <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Medication Name */}
                <div className="relative">
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Medication Name *
                  </label>
                  <input
                    type="text"
                    value={formData.medication_name}
                    onChange={(e) => handleFormChange('medication_name', e.target.value)}
                    placeholder="e.g., Aspirin, Ibuprofen"
                    required
                    disabled={editingMedication} // Can't change medication name when editing
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500'
                    } ${editingMedication ? 'opacity-50 cursor-not-allowed' : ''}`}
                  />
                  
                  {/* Search Suggestions */}
                  {searchSuggestions.length > 0 && !editingMedication && (
                    <div className={`absolute z-10 w-full mt-1 rounded-lg border shadow-lg ${
                      darkMode ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-300'
                    }`}>
                      {searchSuggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          type="button"
                          onClick={() => selectSuggestion(suggestion)}
                          className={`w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${
                            index === 0 ? 'rounded-t-lg' : ''
                          } ${
                            index === searchSuggestions.length - 1 ? 'rounded-b-lg' : ''
                          }`}
                        >
                          <div className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                            {suggestion.name}
                          </div>
                          {suggestion.brand_names && suggestion.brand_names.length > 0 && (
                            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                              {suggestion.brand_names.join(', ')}
                            </div>
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Dosage */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Dosage *
                  </label>
                  <input
                    type="text"
                    value={formData.dosage}
                    onChange={(e) => handleFormChange('dosage', e.target.value)}
                    placeholder="e.g., 500mg, 1 tablet"
                    required
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500'
                    }`}
                  />
                </div>

                {/* Frequency */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Frequency *
                  </label>
                  <input
                    type="text"
                    value={formData.frequency}
                    onChange={(e) => handleFormChange('frequency', e.target.value)}
                    placeholder="e.g., twice daily, every 8 hours"
                    required
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500'
                    }`}
                  />
                </div>

                {/* Prescribed By */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Prescribed By
                  </label>
                  <input
                    type="text"
                    value={formData.prescribed_by}
                    onChange={(e) => handleFormChange('prescribed_by', e.target.value)}
                    placeholder="Doctor's name"
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500'
                    }`}
                  />
                </div>

                {/* Start Date */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => handleFormChange('start_date', e.target.value)}
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-800'
                    }`}
                  />
                </div>

                {/* End Date */}
                <div>
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    End Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => handleFormChange('end_date', e.target.value)}
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-800'
                    }`}
                  />
                </div>

                {/* Instructions */}
                <div className="md:col-span-2">
                  <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Instructions
                  </label>
                  <textarea
                    value={formData.instructions}
                    onChange={(e) => handleFormChange('instructions', e.target.value)}
                    placeholder="Special instructions (e.g., take with food, avoid alcohol)"
                    rows="3"
                    className={`w-full p-3 rounded-lg border ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400' 
                        : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500'
                    }`}
                  />
                </div>

                {/* Status (only for editing) */}
                {editingMedication && (
                  <div>
                    <label className={`block text-sm font-medium mb-1 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      Status
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => handleFormChange('status', e.target.value)}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-800'
                      }`}
                    >
                      <option value="active">Active</option>
                      <option value="paused">Paused</option>
                      <option value="discontinued">Discontinued</option>
                      <option value="completed">Completed</option>
                    </select>
                  </div>
                )}

                {/* Reminder Enabled */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="reminder_enabled"
                    checked={formData.reminder_enabled}
                    onChange={(e) => handleFormChange('reminder_enabled', e.target.checked)}
                    className="mr-2"
                  />
                  <label htmlFor="reminder_enabled" className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    Enable medication reminders
                  </label>
                </div>

                {/* Submit Button */}
                <div className="md:col-span-2 flex gap-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="bg-gradient-to-r from-green-600 to-green-700 text-white px-6 py-2 rounded-lg hover:from-green-700 hover:to-green-800 disabled:opacity-50 transition-all"
                  >
                    {loading ? 'Saving...' : (editingMedication ? 'Update Medication' : 'Add Medication')}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      resetForm();
                      setShowAddForm(false);
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

        {/* Medications List */}
        <div className="space-y-4">
          <h2 className={`text-xl font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            Your Medications ({medications.length})
          </h2>
          
          {loading && !showAddForm ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className={`mt-2 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Loading medications...</p>
            </div>
          ) : medications.length === 0 ? (
            <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              <p>No medications found.</p>
              <p className="text-sm mt-2">Click "Add Medication" to get started.</p>
            </div>
          ) : (
            <div className="grid gap-4">
              {medications.map((medication, index) => (
                <motion.div
                  key={medication.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`p-4 rounded-lg border ${darkMode ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-200'} shadow-sm`}
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                          {medication.medication?.name || 'Unknown Medication'}
                        </h3>
                        <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(medication.status)}`}>
                          {medication.status}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                        <div>
                          <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Dosage:</span>
                          <span className={`ml-1 ${darkMode ? 'text-white' : 'text-gray-800'}`}>{medication.dosage}</span>
                        </div>
                        <div>
                          <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Frequency:</span>
                          <span className={`ml-1 ${darkMode ? 'text-white' : 'text-gray-800'}`}>{medication.frequency}</span>
                        </div>
                        {medication.prescribed_by && (
                          <div>
                            <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>Prescribed by:</span>
                            <span className={`ml-1 ${darkMode ? 'text-white' : 'text-gray-800'}`}>{medication.prescribed_by}</span>
                          </div>
                        )}
                      </div>
                      
                      {medication.instructions && (
                        <p className={`text-sm mt-2 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                          <span className="font-medium">Instructions:</span> {medication.instructions}
                        </p>
                      )}
                      
                      {/* Adherence Stats */}
                      {medication.total_doses_prescribed > 0 && (
                        <div className="mt-2 flex items-center gap-4 text-sm">
                          <span className={`font-medium ${getAdherenceColor(medication.adherence_percentage)}`}>
                            Adherence: {medication.adherence_percentage.toFixed(1)}%
                          </span>
                          <span className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                            Taken: {medication.doses_taken}/{medication.total_doses_prescribed}
                          </span>
                          {medication.doses_missed > 0 && (
                            <span className={`${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                              Missed: {medication.doses_missed}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex flex-col gap-2 ml-4">
                      {medication.status === 'active' && (
                        <div className="flex gap-1">
                          <button
                            onClick={() => logDose(medication.id, 'taken')}
                            className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                          >
                            ✓ Taken
                          </button>
                          <button
                            onClick={() => logDose(medication.id, 'missed')}
                            className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                          >
                            ✗ Missed
                          </button>
                        </div>
                      )}
                      
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleEdit(medication)}
                          className={`px-2 py-1 text-xs rounded ${darkMode ? 'bg-blue-700 hover:bg-blue-600 text-white' : 'bg-blue-100 hover:bg-blue-200 text-blue-800'} transition-colors`}
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => loadDoseHistory(medication.id)}
                          className={`px-2 py-1 text-xs rounded ${darkMode ? 'bg-purple-700 hover:bg-purple-600 text-white' : 'bg-purple-100 hover:bg-purple-200 text-purple-800'} transition-colors`}
                        >
                          History
                        </button>
                        <button
                          onClick={() => handleDelete(medication.id)}
                          className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Dose History Modal */}
        <AnimatePresence>
          {showDoseHistory && doseHistory[showDoseHistory] && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-60 bg-black bg-opacity-50 flex items-center justify-center p-4"
              onClick={() => setShowDoseHistory(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className={`max-w-2xl w-full max-h-96 overflow-y-auto rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} p-6`}
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex justify-between items-center mb-4">
                  <h3 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                    Dose History - {doseHistory[showDoseHistory].medication?.name}
                  </h3>
                  <button
                    onClick={() => setShowDoseHistory(null)}
                    className={`px-3 py-1 rounded ${darkMode ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'}`}
                  >
                    Close
                  </button>
                </div>
                
                <div className="space-y-2">
                  {doseHistory[showDoseHistory].dose_history?.map((dose, index) => (
                    <div key={index} className={`p-2 rounded border ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
                      <div className="flex justify-between items-center">
                        <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                          {new Date(dose.scheduled_time).toLocaleString()}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded ${
                          dose.status === 'taken' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : dose.status === 'missed'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                        }`}>
                          {dose.status}
                        </span>
                      </div>
                      {dose.notes && (
                        <p className={`text-xs mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                          {dose.notes}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
                
                {/* Statistics */}
                <div className="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div>
                      <div className={`text-lg font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                        {doseHistory[showDoseHistory].statistics?.total_doses || 0}
                      </div>
                      <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Total Doses
                      </div>
                    </div>
                    <div>
                      <div className={`text-lg font-bold text-green-600`}>
                        {doseHistory[showDoseHistory].statistics?.taken_doses || 0}
                      </div>
                      <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Taken
                      </div>
                    </div>
                    <div>
                      <div className={`text-lg font-bold text-red-600`}>
                        {doseHistory[showDoseHistory].statistics?.missed_doses || 0}
                      </div>
                      <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Missed
                      </div>
                    </div>
                    <div>
                      <div className={`text-lg font-bold ${getAdherenceColor(doseHistory[showDoseHistory].statistics?.adherence_percentage || 0)}`}>
                        {(doseHistory[showDoseHistory].statistics?.adherence_percentage || 0).toFixed(1)}%
                      </div>
                      <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                        Adherence
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default MedicationManager;