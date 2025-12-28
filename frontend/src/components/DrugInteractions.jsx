import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import apiService from '../services/api';

const DrugInteractions = ({ isOpen, onClose, darkMode }) => {
  const [medications, setMedications] = useState(['']);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [userMedications, setUserMedications] = useState([]);
  const [loadingUserMeds, setLoadingUserMeds] = useState(false);
  const [searchSuggestions, setSearchSuggestions] = useState({});
  const [activeTab, setActiveTab] = useState('manual'); // 'manual' or 'saved'
  const [error, setError] = useState(null);

  // Load user's saved medications when component opens
  useEffect(() => {
    if (isOpen) {
      loadUserMedications();
      // Seed database if needed
      seedDatabaseIfNeeded();
    }
  }, [isOpen]);

  const seedDatabaseIfNeeded = async () => {
    try {
      await apiService.post('/medications/seed-database');
    } catch (error) {
      // Ignore errors - database might already be seeded
      console.log('Database seeding skipped (likely already seeded)');
    }
  };

  const loadUserMedications = async () => {
    setLoadingUserMeds(true);
    try {
      const response = await apiService.get('/medications/user-medications');
      setUserMedications(response.medications || []);
    } catch (error) {
      console.error('Failed to load user medications:', error);
    } finally {
      setLoadingUserMeds(false);
    }
  };

  const searchMedications = async (query, index) => {
    if (query.length < 2) {
      setSearchSuggestions(prev => ({ ...prev, [index]: [] }));
      return;
    }

    try {
      const response = await apiService.get(`/medications/search?query=${encodeURIComponent(query)}&limit=5`);
      setSearchSuggestions(prev => ({ 
        ...prev, 
        [index]: response.medications || [] 
      }));
    } catch (error) {
      console.error('Failed to search medications:', error);
      setSearchSuggestions(prev => ({ ...prev, [index]: [] }));
    }
  };

  const addMedication = () => {
    setMedications([...medications, '']);
  };

  const updateMedication = (index, value) => {
    const updated = [...medications];
    updated[index] = value;
    setMedications(updated);
    
    // Search for suggestions
    if (value.length >= 2) {
      searchMedications(value, index);
    } else {
      setSearchSuggestions(prev => ({ ...prev, [index]: [] }));
    }
  };

  const selectSuggestion = (index, medication) => {
    const updated = [...medications];
    updated[index] = medication.name;
    setMedications(updated);
    setSearchSuggestions(prev => ({ ...prev, [index]: [] }));
  };

  const removeMedication = (index) => {
    if (medications.length > 1) {
      const updated = medications.filter((_, i) => i !== index);
      setMedications(updated);
      // Clean up suggestions for removed index
      setSearchSuggestions(prev => {
        const newSuggestions = { ...prev };
        delete newSuggestions[index];
        return newSuggestions;
      });
    }
  };

  const checkInteractions = async () => {
    const validMeds = medications.filter(med => med.trim());
    if (validMeds.length < 2) {
      setError('Please enter at least 2 medications to check for interactions.');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.post('/medications/check-interactions', {
        medications: validMeds
      });
      
      setResults(response);
    } catch (error) {
      console.error('Failed to check interactions:', error);
      setError('Failed to check drug interactions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const checkUserMedicationInteractions = async () => {
    if (userMedications.length < 2) {
      setError('You need at least 2 saved medications to check for interactions.');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.get('/medications/user-interactions');
      setResults({
        interactions: response.interactions || [],
        summary: {
          total_interactions: response.interactions?.length || 0,
          high_severity: response.interactions?.filter(i => i.severity === 'high').length || 0,
          moderate_severity: response.interactions?.filter(i => i.severity === 'moderate').length || 0,
          low_severity: response.interactions?.filter(i => i.severity === 'low').length || 0,
          contraindicated: response.interactions?.filter(i => i.contraindicated).length || 0,
          requires_monitoring: response.interactions?.filter(i => i.monitoring_required).length || 0
        },
        medications_checked: userMedications.map(um => um.medication?.name).filter(Boolean),
        checked_at: new Date().toISOString()
      });
    } catch (error) {
      console.error('Failed to check user medication interactions:', error);
      setError('Failed to check your medication interactions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      low: darkMode ? 'bg-yellow-900 text-yellow-200 border-yellow-700' : 'bg-yellow-100 text-yellow-800 border-yellow-300',
      moderate: darkMode ? 'bg-orange-900 text-orange-200 border-orange-700' : 'bg-orange-100 text-orange-800 border-orange-300',
      high: darkMode ? 'bg-red-900 text-red-200 border-red-700' : 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[severity] || colors.low;
  };

  const getSeverityIcon = (severity) => {
    const icons = {
      low: '⚠️',
      moderate: '🔶',
      high: '🚨'
    };
    return icons[severity] || '⚠️';
  };

  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className={`flex-1 ${darkMode ? 'bg-gray-900' : 'bg-white'} overflow-y-auto`}
    >
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="flex justify-between items-center mb-6">
          <h1 className={`text-3xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
            💊 Drug Interactions Checker
          </h1>

        </div>

        {/* Tab Navigation */}
        <div className="flex mb-6 border-b border-gray-300 dark:border-gray-600">
          <button
            onClick={() => setActiveTab('manual')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'manual'
                ? `border-b-2 border-blue-500 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`
                : `${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-600 hover:text-gray-800'}`
            }`}
          >
            Manual Entry
          </button>
          <button
            onClick={() => setActiveTab('saved')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'saved'
                ? `border-b-2 border-blue-500 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`
                : `${darkMode ? 'text-gray-400 hover:text-gray-200' : 'text-gray-600 hover:text-gray-800'}`
            }`}
          >
            My Medications ({userMedications.length})
          </button>
        </div>

        {error && (
          <div className={`mb-4 p-3 rounded-lg border ${darkMode ? 'bg-red-900 border-red-700 text-red-200' : 'bg-red-100 border-red-300 text-red-800'}`}>
            <p className="font-medium">⚠️ {error}</p>
          </div>
        )}

        {/* Manual Entry Tab */}
        {activeTab === 'manual' && (
          <div className="mb-6">
            <h2 className={`text-lg font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
              Enter medications to check for interactions:
            </h2>
            
            {medications.map((med, index) => (
              <div key={index} className="relative mb-3">
                <div className="flex gap-2">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={med}
                      onChange={(e) => updateMedication(index, e.target.value)}
                      placeholder={`Medication ${index + 1} (e.g., aspirin, ibuprofen)`}
                      className={`w-full p-3 rounded-lg border ${
                        darkMode 
                          ? 'bg-gray-800 border-gray-600 text-white placeholder-gray-400' 
                          : 'bg-white border-gray-300 text-gray-800 placeholder-gray-500'
                      }`}
                    />
                    
                    {/* Search Suggestions */}
                    <AnimatePresence>
                      {searchSuggestions[index] && searchSuggestions[index].length > 0 && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -10 }}
                          className={`absolute z-10 w-full mt-1 rounded-lg border shadow-lg ${
                            darkMode ? 'bg-gray-800 border-gray-600' : 'bg-white border-gray-300'
                          }`}
                        >
                          {searchSuggestions[index].map((suggestion, suggestionIndex) => (
                            <button
                              key={suggestionIndex}
                              onClick={() => selectSuggestion(index, suggestion)}
                              className={`w-full text-left px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 ${
                                suggestionIndex === 0 ? 'rounded-t-lg' : ''
                              } ${
                                suggestionIndex === searchSuggestions[index].length - 1 ? 'rounded-b-lg' : ''
                              }`}
                            >
                              <div className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                                {suggestion.name}
                              </div>
                              {suggestion.brand_names && suggestion.brand_names.length > 0 && (
                                <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                  Brand names: {suggestion.brand_names.join(', ')}
                                </div>
                              )}
                              {suggestion.drug_class && (
                                <div className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                                  {suggestion.drug_class}
                                </div>
                              )}
                            </button>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                  
                  {medications.length > 1 && (
                    <button
                      onClick={() => removeMedication(index)}
                      className="px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>
            ))}

            <div className="flex gap-2 mb-6">
              <button
                onClick={addMedication}
                className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all"
              >
                Add Medication
              </button>
              <button
                onClick={checkInteractions}
                disabled={loading || medications.filter(m => m.trim()).length < 2}
                className="bg-gradient-to-r from-green-600 to-green-700 text-white px-4 py-2 rounded-lg hover:from-green-700 hover:to-green-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Checking...
                  </span>
                ) : 'Check Interactions'}
              </button>
            </div>
          </div>
        )}

        {/* Saved Medications Tab */}
        {activeTab === 'saved' && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                Your Saved Medications:
              </h2>
              <button
                onClick={loadUserMedications}
                disabled={loadingUserMeds}
                className={`px-3 py-1 text-sm rounded ${darkMode ? 'bg-gray-700 hover:bg-gray-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'} transition-colors`}
              >
                {loadingUserMeds ? 'Loading...' : 'Refresh'}
              </button>
            </div>
            
            {loadingUserMeds ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className={`mt-2 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Loading your medications...</p>
              </div>
            ) : userMedications.length === 0 ? (
              <div className={`text-center py-8 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                <p>No saved medications found.</p>
                <p className="text-sm mt-2">Add medications to your profile to check for interactions automatically.</p>
              </div>
            ) : (
              <>
                <div className="grid gap-3 mb-4">
                  {userMedications.map((userMed, index) => (
                    <div key={index} className={`p-3 rounded-lg border ${darkMode ? 'bg-gray-800 border-gray-600' : 'bg-gray-50 border-gray-200'}`}>
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className={`font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                            {userMed.medication?.name || 'Unknown Medication'}
                          </h3>
                          <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                            {userMed.dosage} - {userMed.frequency}
                          </p>
                          {userMed.instructions && (
                            <p className={`text-xs mt-1 ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                              {userMed.instructions}
                            </p>
                          )}
                        </div>
                        <span className={`px-2 py-1 text-xs rounded ${
                          userMed.status === 'active' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                        }`}>
                          {userMed.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
                
                <button
                  onClick={checkUserMedicationInteractions}
                  disabled={loading || userMedications.length < 2}
                  className="bg-gradient-to-r from-purple-600 to-purple-700 text-white px-4 py-2 rounded-lg hover:from-purple-700 hover:to-purple-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Checking...
                    </span>
                  ) : 'Check My Medication Interactions'}
                </button>
              </>
            )}
          </div>
        )}

        {/* Results Section */}
        <AnimatePresence>
          {results && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`p-6 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}
            >
              <h3 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                Interaction Results
              </h3>
              
              {/* Summary Statistics */}
              {results.summary && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                  <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-gray-700' : 'bg-white'}`}>
                    <div className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                      {results.summary.total_interactions}
                    </div>
                    <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                      Total Interactions
                    </div>
                  </div>
                  <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-red-900' : 'bg-red-100'}`}>
                    <div className={`text-2xl font-bold ${darkMode ? 'text-red-200' : 'text-red-800'}`}>
                      {results.summary.high_severity}
                    </div>
                    <div className={`text-sm ${darkMode ? 'text-red-400' : 'text-red-600'}`}>
                      High Severity
                    </div>
                  </div>
                  <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-orange-900' : 'bg-orange-100'}`}>
                    <div className={`text-2xl font-bold ${darkMode ? 'text-orange-200' : 'text-orange-800'}`}>
                      {results.summary.moderate_severity}
                    </div>
                    <div className={`text-sm ${darkMode ? 'text-orange-400' : 'text-orange-600'}`}>
                      Moderate
                    </div>
                  </div>
                  <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-yellow-900' : 'bg-yellow-100'}`}>
                    <div className={`text-2xl font-bold ${darkMode ? 'text-yellow-200' : 'text-yellow-800'}`}>
                      {results.summary.low_severity}
                    </div>
                    <div className={`text-sm ${darkMode ? 'text-yellow-400' : 'text-yellow-600'}`}>
                      Low Severity
                    </div>
                  </div>
                  <div className={`p-3 rounded-lg text-center ${darkMode ? 'bg-purple-900' : 'bg-purple-100'}`}>
                    <div className={`text-2xl font-bold ${darkMode ? 'text-purple-200' : 'text-purple-800'}`}>
                      {results.summary.contraindicated}
                    </div>
                    <div className={`text-sm ${darkMode ? 'text-purple-400' : 'text-purple-600'}`}>
                      Contraindicated
                    </div>
                  </div>
                </div>
              )}
              
              {/* Interaction Details */}
              {results.interactions && results.interactions.length > 0 ? (
                <div className="space-y-4">
                  <h4 className={`text-lg font-semibold ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                    Detailed Interactions:
                  </h4>
                  
                  {results.interactions.map((interaction, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className={`p-4 rounded-lg border-l-4 ${getSeverityColor(interaction.severity)}`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center">
                          <span className="text-lg mr-2">{getSeverityIcon(interaction.severity)}</span>
                          <h5 className="font-semibold">
                            {interaction.medication_a} + {interaction.medication_b}
                          </h5>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 text-xs rounded-full font-medium ${getSeverityColor(interaction.severity)}`}>
                            {interaction.severity.toUpperCase()}
                          </span>
                          {interaction.contraindicated && (
                            <span className="px-2 py-1 text-xs rounded-full font-medium bg-red-600 text-white">
                              CONTRAINDICATED
                            </span>
                          )}
                        </div>
                      </div>
                      
                      <p className="mb-3 text-sm">
                        <strong>Mechanism:</strong> {interaction.mechanism}
                      </p>
                      
                      {interaction.clinical_effects && interaction.clinical_effects.length > 0 && (
                        <div className="mb-3">
                          <strong className="text-sm">Clinical Effects:</strong>
                          <ul className="list-disc list-inside text-sm mt-1 ml-4">
                            {interaction.clinical_effects.map((effect, effectIndex) => (
                              <li key={effectIndex}>{effect}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {interaction.management_recommendations && interaction.management_recommendations.length > 0 && (
                        <div className="mb-3">
                          <strong className="text-sm">Management Recommendations:</strong>
                          <ul className="list-disc list-inside text-sm mt-1 ml-4">
                            {interaction.management_recommendations.map((rec, recIndex) => (
                              <li key={recIndex}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-xs">
                        <span>Evidence Level: {interaction.evidence_level}</span>
                        {interaction.monitoring_required && (
                          <span className="bg-blue-600 text-white px-2 py-1 rounded">
                            Monitoring Required
                          </span>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </div>
              ) : (
                <div className={`p-4 rounded-lg text-center ${darkMode ? 'bg-green-900' : 'bg-green-100'}`}>
                  <p className={`text-lg font-medium ${darkMode ? 'text-green-200' : 'text-green-800'}`}>
                    ✅ No known interactions found
                  </p>
                  <p className={`text-sm mt-2 ${darkMode ? 'text-green-300' : 'text-green-700'}`}>
                    The medications checked do not have any known interactions in our database.
                  </p>
                </div>
              )}

              {/* General Recommendations */}
              <div className={`mt-6 p-4 rounded-lg ${darkMode ? 'bg-blue-900' : 'bg-blue-100'}`}>
                <h4 className={`font-semibold mb-2 ${darkMode ? 'text-blue-200' : 'text-blue-800'}`}>
                  💡 Important Reminders:
                </h4>
                <ul className={`list-disc list-inside space-y-1 text-sm ${darkMode ? 'text-blue-300' : 'text-blue-700'}`}>
                  <li>Always inform your healthcare provider about all medications you're taking</li>
                  <li>Include over-the-counter drugs, supplements, and herbal products</li>
                  <li>This tool provides general information - consult your pharmacist or doctor for personalized advice</li>
                  <li>Never stop or change medications without consulting your healthcare provider</li>
                  <li>Keep an updated medication list with you at all times</li>
                </ul>
              </div>
              
              {results.checked_at && (
                <div className={`mt-4 text-xs text-center ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                  Checked on {new Date(results.checked_at).toLocaleString()}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default DrugInteractions;