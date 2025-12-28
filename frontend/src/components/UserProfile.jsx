import { useState, useEffect } from "react";
import { FaUser, FaCog, FaSignOutAlt, FaTimes, FaEdit, FaSave, FaCamera, FaShieldAlt, FaEye, FaEyeSlash } from "react-icons/fa";
import { useAuth } from "../contexts/AuthContext";

export default function UserProfile({ isOpen, onClose, darkMode, onDarkModeChange }) {
  const { currentUser, logout, updateUserProfile, getUserProfile } = useAuth();
  const isAuthenticated = !!currentUser;
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState({
    displayName: "",
    email: "",
    phone: "",
    dateOfBirth: "",
    gender: "prefer-not-to-say",
    emergencyContact: {
      name: "",
      phone: "",
      relationship: ""
    },
    medicalInfo: {
      bloodType: "",
      allergies: "",
      medications: "",
      conditions: ""
    },
    preferences: {
      theme: "light",
      notifications: true,
      language: "en",
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    },
    privacySettings: {
      shareDataForResearch: false,
      allowAnalytics: true,
      dataRetentionPeriod: "2years"
    }
  });

  const [tempProfile, setTempProfile] = useState(profile);

  // Load user profile data
  useEffect(() => {
    const loadProfile = async () => {
      if (currentUser && isOpen) {
        setLoading(true);
        try {
          const userProfile = await getUserProfile();
          if (userProfile) {
            const loadedProfile = {
              displayName: currentUser.displayName || "",
              email: currentUser.email || "",
              phone: userProfile.phone || "",
              dateOfBirth: userProfile.dateOfBirth || "",
              gender: userProfile.gender || "prefer-not-to-say",
              emergencyContact: userProfile.emergencyContact || {
                name: "",
                phone: "",
                relationship: ""
              },
              medicalInfo: userProfile.medicalInfo || {
                bloodType: "",
                allergies: "",
                medications: "",
                conditions: ""
              },
              preferences: {
                theme: darkMode ? "dark" : "light",
                notifications: userProfile.preferences?.notifications ?? true,
                language: userProfile.preferences?.language || "en",
                timezone: userProfile.preferences?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone
              },
              privacySettings: userProfile.privacySettings || {
                shareDataForResearch: false,
                allowAnalytics: true,
                dataRetentionPeriod: "2years"
              }
            };
            setProfile(loadedProfile);
            setTempProfile(loadedProfile);
          }
        } catch (error) {
          console.error('Error loading profile:', error);
        } finally {
          setLoading(false);
        }
      }
    };

    loadProfile();
  }, [currentUser, isOpen, getUserProfile, darkMode]);

  if (!isOpen) return null;

  // Demo mode fallback
  if (!isAuthenticated) {
    const demoProfile = {
      displayName: "Demo User",
      email: "demo@example.com",
      phone: "+1 (555) 123-4567",
      dateOfBirth: "1990-01-01",
      gender: "prefer-not-to-say",
      emergencyContact: {
        name: "Emergency Contact",
        phone: "+1 (555) 987-6543",
        relationship: "Family"
      },
      medicalInfo: {
        bloodType: "O+",
        allergies: "None",
        medications: "None",
        conditions: "None"
      }
    };
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-gray-800 text-white p-6 relative">
            <button onClick={onClose} className="absolute top-4 right-4 text-white hover:text-gray-200 transition-colors">
              <FaTimes size={20} />
            </button>
            <div className="flex items-center gap-4">
              <div className="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <FaUser size={32} />
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-bold">{demoProfile.displayName}</h2>
                <p className="text-blue-100">{demoProfile.email}</p>
                <p className="text-sm text-blue-200 mt-1">Demo Mode - Sign in to access full profile</p>
              </div>
            </div>
          </div>
          <div className="p-6 text-center">
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Sign in to access your full profile with personalized settings and medical information.
            </p>
            <button
              onClick={onClose}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handleEdit = () => {
    setTempProfile(profile);
    setIsEditing(true);
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await updateUserProfile({
        displayName: tempProfile.displayName,
        phone: tempProfile.phone,
        dateOfBirth: tempProfile.dateOfBirth,
        gender: tempProfile.gender,
        emergencyContact: tempProfile.emergencyContact,
        medicalInfo: tempProfile.medicalInfo,
        preferences: tempProfile.preferences,
        privacySettings: tempProfile.privacySettings
      });
      setProfile(tempProfile);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setTempProfile(profile);
    setIsEditing(false);
  };

  const handleInputChange = (section, field, value) => {
    if (section) {
      setTempProfile(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [field]: value
        }
      }));
    } else {
      setTempProfile(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      onClose();
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-gray-800 text-white p-6 relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-white hover:text-gray-200 transition-colors"
          >
            <FaTimes size={20} />
          </button>
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-20 h-20 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                {currentUser?.photoURL ? (
                  <img 
                    src={currentUser.photoURL} 
                    alt="Profile" 
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  <FaUser size={32} />
                )}
              </div>
              {isEditing && (
                <button className="absolute -bottom-1 -right-1 bg-blue-500 hover:bg-blue-600 text-white rounded-full p-2 transition-colors">
                  <FaCamera size={12} />
                </button>
              )}
            </div>
            
            <div className="flex-1">
              <h2 className="text-2xl font-bold">{profile.displayName || 'User'}</h2>
              <p className="text-blue-100">{profile.email}</p>
              {currentUser?.emailVerified ? (
                <p className="text-sm text-green-200">✓ Email verified</p>
              ) : (
                <p className="text-sm text-yellow-200">⚠ Email not verified</p>
              )}
            </div>
            
            <div className="flex gap-2">
              {!isEditing ? (
                <button
                  onClick={handleEdit}
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
                >
                  <FaEdit size={14} />
                  Edit
                </button>
              ) : (
                <div className="flex gap-2">
                  <button
                    onClick={handleSave}
                    disabled={loading}
                    className="bg-green-500 hover:bg-green-600 disabled:bg-green-400 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
                  >
                    <FaSave size={14} />
                    {loading ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    onClick={handleCancel}
                    disabled={loading}
                    className="bg-red-500 hover:bg-red-600 disabled:bg-red-400 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Display Name
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={tempProfile.displayName}
                      onChange={(e) => handleInputChange(null, 'displayName', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.displayName || 'Not set'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email
                  </label>
                  <p className="text-gray-900 dark:text-white">{profile.email}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Email cannot be changed here</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Phone
                  </label>
                  {isEditing ? (
                    <input
                      type="tel"
                      value={tempProfile.phone}
                      onChange={(e) => handleInputChange(null, 'phone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.phone || 'Not set'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Date of Birth
                  </label>
                  {isEditing ? (
                    <input
                      type="date"
                      value={tempProfile.dateOfBirth}
                      onChange={(e) => handleInputChange(null, 'dateOfBirth', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">
                      {profile.dateOfBirth ? new Date(profile.dateOfBirth).toLocaleDateString() : 'Not set'}
                    </p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Gender
                  </label>
                  {isEditing ? (
                    <select
                      value={tempProfile.gender}
                      onChange={(e) => handleInputChange(null, 'gender', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                      <option value="prefer-not-to-say">Prefer not to say</option>
                    </select>
                  ) : (
                    <p className="text-gray-900 dark:text-white capitalize">{profile.gender.replace('-', ' ')}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Privacy Settings */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FaShieldAlt className="text-blue-600" />
                Privacy & Security
              </h3>
              <div className="space-y-4 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Share Data for Research</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Help improve medical AI by sharing anonymized data</p>
                  </div>
                  <button
                    onClick={() => handleInputChange('privacySettings', 'shareDataForResearch', !tempProfile.privacySettings.shareDataForResearch)}
                    disabled={!isEditing}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      tempProfile.privacySettings.shareDataForResearch ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                    } ${!isEditing ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        tempProfile.privacySettings.shareDataForResearch ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Allow Analytics</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Help us improve the app with usage analytics</p>
                  </div>
                  <button
                    onClick={() => handleInputChange('privacySettings', 'allowAnalytics', !tempProfile.privacySettings.allowAnalytics)}
                    disabled={!isEditing}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      tempProfile.privacySettings.allowAnalytics ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                    } ${!isEditing ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        tempProfile.privacySettings.allowAnalytics ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Data Retention Period
                  </label>
                  {isEditing ? (
                    <select
                      value={tempProfile.privacySettings.dataRetentionPeriod}
                      onChange={(e) => handleInputChange('privacySettings', 'dataRetentionPeriod', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                      <option value="1year">1 Year</option>
                      <option value="2years">2 Years</option>
                      <option value="5years">5 Years</option>
                      <option value="indefinite">Indefinite</option>
                    </select>
                  ) : (
                    <p className="text-gray-900 dark:text-white capitalize">{profile.privacySettings.dataRetentionPeriod.replace('years', ' years').replace('year', ' year')}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Emergency Contact */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Emergency Contact</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Name
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={tempProfile.emergencyContact.name}
                      onChange={(e) => handleInputChange('emergencyContact', 'name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.emergencyContact.name || 'Not set'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Phone
                  </label>
                  {isEditing ? (
                    <input
                      type="tel"
                      value={tempProfile.emergencyContact.phone}
                      onChange={(e) => handleInputChange('emergencyContact', 'phone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.emergencyContact.phone || 'Not set'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Relationship
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={tempProfile.emergencyContact.relationship}
                      onChange={(e) => handleInputChange('emergencyContact', 'relationship', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.emergencyContact.relationship || 'Not set'}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Medical Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Medical Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Blood Type
                  </label>
                  {isEditing ? (
                    <select
                      value={tempProfile.medicalInfo.bloodType}
                      onChange={(e) => handleInputChange('medicalInfo', 'bloodType', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    >
                      <option value="">Unknown</option>
                      <option value="A+">A+</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>
                      <option value="B-">B-</option>
                      <option value="AB+">AB+</option>
                      <option value="AB-">AB-</option>
                      <option value="O+">O+</option>
                      <option value="O-">O-</option>
                    </select>
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.medicalInfo.bloodType || 'Unknown'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Allergies
                  </label>
                  {isEditing ? (
                    <textarea
                      value={tempProfile.medicalInfo.allergies}
                      onChange={(e) => handleInputChange('medicalInfo', 'allergies', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                      placeholder="List any known allergies..."
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.medicalInfo.allergies || 'None listed'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Current Medications
                  </label>
                  {isEditing ? (
                    <textarea
                      value={tempProfile.medicalInfo.medications}
                      onChange={(e) => handleInputChange('medicalInfo', 'medications', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                      placeholder="List current medications..."
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.medicalInfo.medications || 'None listed'}</p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Medical Conditions
                  </label>
                  {isEditing ? (
                    <textarea
                      value={tempProfile.medicalInfo.conditions}
                      onChange={(e) => handleInputChange('medicalInfo', 'conditions', e.target.value)}
                      rows={2}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                      placeholder="List any medical conditions..."
                    />
                  ) : (
                    <p className="text-gray-900 dark:text-white">{profile.medicalInfo.conditions || 'None listed'}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Settings */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">App Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Dark Mode</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Toggle dark mode theme</p>
                  </div>
                  <button
                    onClick={onDarkModeChange}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      darkMode ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        darkMode ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Notifications</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Receive health reminders and updates</p>
                  </div>
                  <button
                    onClick={() => handleInputChange('preferences', 'notifications', !tempProfile.preferences.notifications)}
                    disabled={!isEditing}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      tempProfile.preferences.notifications ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                    } ${!isEditing ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        tempProfile.preferences.notifications ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="border-t border-gray-200 dark:border-gray-700 p-6">
          <button 
            onClick={handleLogout}
            className="w-full bg-red-500 hover:bg-red-600 text-white py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <FaSignOutAlt />
            Sign Out
          </button>
        </div>
      </div>
    </div>
  );
}