import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

const PersonalizationSettings = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analytics, setAnalytics] = useState(null);
  const [recentSuggestions, setRecentSuggestions] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Form state
  const [formData, setFormData] = useState({
    ai_personality: 'empathetic',
    communication_style: 'supportive',
    preferred_activities: [],
    response_preferences: {
      emoji_usage: 'moderate',
      response_length: 'medium',
      formality: 'casual'
    }
  });

  useEffect(() => {
    if (user) {
      loadPersonalizationData();
    }
  }, [user]);

  const loadPersonalizationData = async () => {
    try {
      setLoading(true);
      const token = await user.getIdToken();
      
      // Load personalization profile
      const profileResponse = await fetch('/api/personalization/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        setProfile(profileData);
        setFormData({
          ai_personality: profileData.ai_personality,
          communication_style: profileData.communication_style,
          preferred_activities: profileData.preferred_activities,
          response_preferences: profileData.response_preferences
        });
      }

      // Load suggestion analytics
      const analyticsResponse = await fetch('/api/personalization/suggestions/analytics', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setAnalytics(analyticsData);
      }

      // Load recent suggestions
      const suggestionsResponse = await fetch('/api/personalization/suggestions/recent?limit=5', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (suggestionsResponse.ok) {
        const suggestionsData = await suggestionsResponse.json();
        setRecentSuggestions(suggestionsData.suggestions || []);
      }

    } catch (err) {
      setError('Failed to load personalization data');
      console.error('Error loading personalization data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      const token = await user.getIdToken();
      const response = await fetch('/api/personalization/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setSuccess('Personalization settings saved successfully!');
        await loadPersonalizationData(); // Reload data
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (err) {
      setError('Failed to save personalization settings');
      console.error('Error saving settings:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleRefreshProfile = async () => {
    try {
      setLoading(true);
      const token = await user.getIdToken();
      
      const response = await fetch('/api/personalization/profile/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setSuccess('Profile refreshed based on recent activity!');
        await loadPersonalizationData();
      } else {
        throw new Error('Failed to refresh profile');
      }
    } catch (err) {
      setError('Failed to refresh profile');
      console.error('Error refreshing profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionFeedback = async (suggestionId, feedback) => {
    try {
      const token = await user.getIdToken();
      
      const response = await fetch('/api/personalization/suggestions/feedback', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          suggestion_id: suggestionId,
          feedback: feedback,
          effectiveness_score: feedback === 'helpful' ? 0.8 : feedback === 'tried' ? 0.9 : 0.2
        })
      });

      if (response.ok) {
        setSuccess('Feedback submitted successfully!');
        await loadPersonalizationData(); // Reload to update analytics
      } else {
        throw new Error('Failed to submit feedback');
      }
    } catch (err) {
      setError('Failed to submit feedback');
      console.error('Error submitting feedback:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Loading personalization settings...</span>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">🎯 Personalization Settings</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        {/* AI Personality Settings */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">🤖 AI Personality</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { value: 'empathetic', label: 'Empathetic', desc: 'Warm and emotionally supportive' },
              { value: 'professional', label: 'Professional', desc: 'Structured and caring' },
              { value: 'casual', label: 'Casual', desc: 'Friendly and conversational' }
            ].map((option) => (
              <label key={option.value} className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="ai_personality"
                  value={option.value}
                  checked={formData.ai_personality === option.value}
                  onChange={(e) => setFormData({ ...formData, ai_personality: e.target.value })}
                  className="mt-1"
                />
                <div>
                  <div className="font-medium text-gray-800">{option.label}</div>
                  <div className="text-sm text-gray-600">{option.desc}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Communication Style */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">💬 Communication Style</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { value: 'gentle', label: 'Gentle', desc: 'Extra patient and soft' },
              { value: 'supportive', label: 'Supportive', desc: 'Balanced support and advice' },
              { value: 'direct', label: 'Direct', desc: 'Clear and action-oriented' }
            ].map((option) => (
              <label key={option.value} className="flex items-start space-x-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                <input
                  type="radio"
                  name="communication_style"
                  value={option.value}
                  checked={formData.communication_style === option.value}
                  onChange={(e) => setFormData({ ...formData, communication_style: e.target.value })}
                  className="mt-1"
                />
                <div>
                  <div className="font-medium text-gray-800">{option.label}</div>
                  <div className="text-sm text-gray-600">{option.desc}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Response Preferences */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">📝 Response Preferences</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Emoji Usage</label>
              <select
                value={formData.response_preferences.emoji_usage}
                onChange={(e) => setFormData({
                  ...formData,
                  response_preferences: {
                    ...formData.response_preferences,
                    emoji_usage: e.target.value
                  }
                })}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="low">Low</option>
                <option value="moderate">Moderate</option>
                <option value="high">High</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Response Length</label>
              <select
                value={formData.response_preferences.response_length}
                onChange={(e) => setFormData({
                  ...formData,
                  response_preferences: {
                    ...formData.response_preferences,
                    response_length: e.target.value
                  }
                })}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="short">Short</option>
                <option value="medium">Medium</option>
                <option value="long">Long</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Formality</label>
              <select
                value={formData.response_preferences.formality}
                onChange={(e) => setFormData({
                  ...formData,
                  response_preferences: {
                    ...formData.response_preferences,
                    formality: e.target.value
                  }
                })}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="casual">Casual</option>
                <option value="formal">Formal</option>
              </select>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4">
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Saving...' : 'Save Settings'}
          </button>
          
          <button
            onClick={handleRefreshProfile}
            disabled={loading}
            className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Refresh Profile
          </button>
        </div>
      </div>

      {/* Current Profile Summary */}
      {profile && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">📊 Your Personalization Profile</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Conversation Patterns</h4>
              <div className="text-sm text-gray-600 space-y-1">
                <div>Average message length: {profile.conversation_patterns.avg_message_length} characters</div>
                <div>Preferred time: {profile.conversation_patterns.preferred_time}</div>
                <div>Conversation frequency: {profile.conversation_patterns.conversation_frequency}</div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Insights</h4>
              <div className="text-sm text-gray-600 space-y-1">
                <div>Mood triggers: {profile.mood_triggers.slice(0, 3).join(', ') || 'None identified'}</div>
                <div>Preferred topics: {profile.preferred_topics.slice(0, 3).join(', ') || 'General wellbeing'}</div>
                <div>Effective activities: {profile.preferred_activities.slice(0, 3).join(', ') || 'None yet'}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Suggestion Analytics */}
      {analytics && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">📈 Suggestion Analytics</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{analytics.total_suggestions}</div>
              <div className="text-sm text-gray-600">Total Suggestions</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{analytics.helpful_suggestions}</div>
              <div className="text-sm text-gray-600">Helpful</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">{analytics.tried_suggestions}</div>
              <div className="text-sm text-gray-600">Tried</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{(analytics.average_effectiveness * 100).toFixed(0)}%</div>
              <div className="text-sm text-gray-600">Avg Effectiveness</div>
            </div>
          </div>
        </div>
      )}

      {/* Recent Suggestions */}
      {recentSuggestions.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">💡 Recent Suggestions</h3>
          
          <div className="space-y-4">
            {recentSuggestions.map((suggestion, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="font-medium text-gray-800">{suggestion.suggestion_text}</div>
                    <div className="text-sm text-gray-600">
                      Type: {suggestion.suggestion_type} • 
                      {new Date(suggestion.suggested_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="text-sm">
                    {suggestion.user_feedback ? (
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        suggestion.user_feedback === 'helpful' ? 'bg-green-100 text-green-800' :
                        suggestion.user_feedback === 'tried' ? 'bg-blue-100 text-blue-800' :
                        suggestion.user_feedback === 'not_helpful' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {suggestion.user_feedback}
                      </span>
                    ) : (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSuggestionFeedback(suggestion.suggestion_id, 'helpful')}
                          className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded hover:bg-green-200"
                        >
                          Helpful
                        </button>
                        <button
                          onClick={() => handleSuggestionFeedback(suggestion.suggestion_id, 'tried')}
                          className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded hover:bg-blue-200"
                        >
                          Tried
                        </button>
                        <button
                          onClick={() => handleSuggestionFeedback(suggestion.suggestion_id, 'not_helpful')}
                          className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded hover:bg-red-200"
                        >
                          Not Helpful
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PersonalizationSettings;