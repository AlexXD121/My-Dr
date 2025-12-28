// API service for backend communication
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = null;
    this.tokenRefreshCallback = null;
    this.requestQueue = [];
    this.isRefreshing = false;
  }

  // Set authentication token
  setToken(token) {
    this.token = token;
  }

  // Clear authentication token
  clearToken() {
    this.token = null;
  }

  // Set token refresh callback
  setTokenRefreshCallback(callback) {
    this.tokenRefreshCallback = callback;
  }

  // Initialize with Firebase auth context
  initializeAuth(authContext) {
    this.authContext = authContext;
    
    // Set up automatic token management
    if (authContext.currentUser) {
      this.refreshAndSetToken();
    }
    
    // Listen for auth state changes
    window.addEventListener('auth:token-updated', (event) => {
      this.setToken(event.detail.token);
    });
    
    window.addEventListener('auth:logout', () => {
      this.clearToken();
    });
  }

  // Refresh and set token from Firebase
  async refreshAndSetToken() {
    if (this.authContext && this.authContext.currentUser) {
      try {
        const token = await this.authContext.getIdToken(true);
        this.setToken(token);
        return token;
      } catch (error) {
        console.error('Failed to refresh Firebase token:', error);
        this.clearToken();
        throw error;
      }
    }
    return null;
  }

  // Refresh token and retry failed requests
  async refreshTokenAndRetry() {
    if (this.isRefreshing) {
      // If already refreshing, wait for it to complete
      return new Promise((resolve) => {
        this.requestQueue.push(resolve);
      });
    }

    this.isRefreshing = true;

    try {
      if (this.tokenRefreshCallback) {
        const newToken = await this.tokenRefreshCallback(true);
        this.setToken(newToken);
        
        // Resolve all queued requests
        this.requestQueue.forEach(resolve => resolve(newToken));
        this.requestQueue = [];
        
        return newToken;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearToken();
      throw error;
    } finally {
      this.isRefreshing = false;
    }
  }

  // Get headers with authentication
  getHeaders(contentType = 'application/json') {
    const headers = {
      'Content-Type': contentType,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Generic request method with automatic token refresh
  async request(endpoint, options = {}, retryCount = 0) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: this.getHeaders(),
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      // Handle rate limiting
      if (response.status === 429) {
        const retryAfter = response.headers.get('Retry-After') || '60';
        throw new Error(`Rate limit exceeded. Please try again in ${retryAfter} seconds.`);
      }

      // Handle authentication errors with token refresh
      if (response.status === 401 && retryCount === 0) {
        try {
          await this.refreshTokenAndRetry();
          // Retry the request with the new token
          return this.request(endpoint, options, retryCount + 1);
        } catch (refreshError) {
          throw new Error('Authentication required. Please log in again.');
        }
      }

      // Handle other HTTP errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      // Return JSON response
      return await response.json();
    } catch (error) {
      // Don't log authentication errors as they're expected
      if (!error.message.includes('Authentication required')) {
        console.error(`API request failed: ${endpoint}`, error);
      }
      throw error;
    }
  }

  // Request with offline support
  async requestWithOfflineSupport(endpoint, options = {}) {
    try {
      return await this.request(endpoint, options);
    } catch (error) {
      // If offline, try to get cached data
      if (!navigator.onLine) {
        const cachedData = this.getCachedData(endpoint);
        if (cachedData) {
          return cachedData;
        }
        throw new Error('You are offline and no cached data is available.');
      }
      throw error;
    }
  }

  // Cache management for offline support
  getCachedData(endpoint) {
    try {
      const cached = localStorage.getItem(`api_cache_${endpoint}`);
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        // Return cached data if it's less than 5 minutes old
        if (Date.now() - timestamp < 5 * 60 * 1000) {
          return data;
        }
      }
    } catch (error) {
      console.error('Error reading cached data:', error);
    }
    return null;
  }

  setCachedData(endpoint, data) {
    try {
      localStorage.setItem(`api_cache_${endpoint}`, JSON.stringify({
        data,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.error('Error caching data:', error);
    }
  }

  // GET request
  async get(endpoint) {
    return this.request(endpoint, {
      method: 'GET',
    });
  }

  // POST request
  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // PUT request
  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }

  // Health check
  async healthCheck() {
    return this.get('/health');
  }

  // Authentication with Firebase token
  async authenticateWithFirebase(idToken) {
    return this.post('/auth/firebase', { idToken });
  }

  // Send chat message - no auth required for demo
  async sendMessage(message) {
    console.log('🔵 API Service: Sending message to backend:', message);
    console.log('🔵 API Service: Base URL:', this.baseURL);
    
    const url = `${this.baseURL}/chat`;
    console.log('🔵 API Service: Full URL:', url);
    
    try {
      console.log('🔵 API Service: Starting fetch request...');
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      console.log('🔵 API Service: Response received');
      console.log('🔵 API Service: Response status:', response.status);
      console.log('🔵 API Service: Response ok:', response.ok);
      console.log('🔵 API Service: Response statusText:', response.statusText);

      if (!response.ok) {
        let errorText;
        try {
          errorText = await response.text();
          console.error('🔴 API Service: Error response text:', errorText);
        } catch (textError) {
          console.error('🔴 API Service: Could not read error response:', textError);
          errorText = 'Unknown error';
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText} - ${errorText}`);
      }

      console.log('🔵 API Service: Parsing JSON response...');
      const data = await response.json();
      console.log('✅ API Service: Response data:', data);
      return data;
    } catch (error) {
      console.error('🔴 API Service: DETAILED FETCH ERROR:', {
        message: error.message,
        stack: error.stack,
        name: error.name,
        cause: error.cause,
        type: typeof error,
        fullError: error
      });
      
      // Add more specific error messages
      if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        throw new Error('Failed to connect to backend server. Is it running on port 8000?');
      } else if (error.message.includes('NetworkError')) {
        throw new Error('Network error - check your internet connection');
      } else if (error.message.includes('ECONNREFUSED')) {
        throw new Error('Connection refused - backend server is not running');
      }
      
      throw error;
    }
  }

  // Get user profile
  async getUserProfile() {
    return this.get('/user/profile');
  }

  // Validate connection to backend
  async validateConnection() {
    try {
      const response = await this.get('/');
      return response.message ? true : false;
    } catch (error) {
      console.error('Backend connection failed:', error);
      return false;
    }
  }

  // Symptom analysis methods
  async analyzeSymptoms(symptomData) {
    console.log('🔵 API Service: Analyzing symptoms:', symptomData);
    return this.post('/symptoms/analyze', symptomData);
  }

  async getSymptomHistory(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/symptoms/history?${queryString}` : '/symptoms/history';
    return this.get(endpoint);
  }

  async getSymptomInsights(daysBack = 30) {
    return this.get(`/symptoms/insights?days_back=${daysBack}`);
  }

  async exportSymptomData(format = 'json', dateFrom = null, dateTo = null) {
    const params = new URLSearchParams({ format });
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    
    return this.get(`/symptoms/export?${params.toString()}`);
  }

  async deleteSymptomRecord(recordId) {
    return this.delete(`/symptoms/history/${recordId}`);
  }

  async getSymptomCheckerHealth() {
    return this.get('/symptoms/health');
  }

  // Medical History API methods
  async getMedicalRecords(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/medical-history/records?${queryString}` : '/medical-history/records';
    return this.get(endpoint);
  }

  async getMedicalRecord(recordId) {
    return this.get(`/medical-history/records/${recordId}`);
  }

  async createMedicalRecord(recordData) {
    console.log('🔵 API Service: Creating medical record:', recordData);
    return this.post('/medical-history/records', recordData);
  }

  async updateMedicalRecord(recordId, recordData) {
    console.log('🔵 API Service: Updating medical record:', recordId, recordData);
    return this.put(`/medical-history/records/${recordId}`, recordData);
  }

  async deleteMedicalRecord(recordId) {
    console.log('🔵 API Service: Deleting medical record:', recordId);
    return this.delete(`/medical-history/records/${recordId}`);
  }

  async getMedicalHistoryStats() {
    return this.get('/medical-history/stats');
  }

  async uploadMedicalAttachment(recordId, file, description = null) {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    return this.request(`/medical-history/records/${recordId}/attachments`, {
      method: 'POST',
      body: formData,
      headers: {
        // Don't set Content-Type for FormData, let browser set it with boundary
        'Authorization': this.token ? `Bearer ${this.token}` : undefined
      }
    });
  }

  async getMedicalRecordCategories() {
    return this.get('/medical-history/categories');
  }

  // Medical Data Export and Sharing methods
  async exportMedicalHistory(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/medical-history/export?${queryString}` : '/medical-history/export';
    return this.get(endpoint);
  }

  async createMedicalShare(shareData) {
    console.log('🔵 API Service: Creating medical share:', shareData);
    return this.post('/medical-history/share', shareData);
  }

  async createMedicalBackup(includeAttachments = false) {
    return this.get(`/medical-history/backup?include_attachments=${includeAttachments}`);
  }

  async restoreMedicalBackup(backupData, overwriteExisting = false) {
    console.log('🔵 API Service: Restoring medical backup');
    return this.post(`/medical-history/restore?overwrite_existing=${overwriteExisting}`, backupData);
  }

  // Medication Management API methods
  async searchMedications(query, limit = 10) {
    const params = new URLSearchParams({ query, limit: limit.toString() });
    return this.get(`/medications/search?${params.toString()}`);
  }

  async validateMedication(medicationName) {
    return this.post('/medications/validate', { medication_name: medicationName });
  }

  async getUserMedications(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/medications/user-medications?${queryString}` : '/medications/user-medications';
    return this.get(endpoint);
  }

  async addUserMedication(medicationData) {
    console.log('🔵 API Service: Adding user medication:', medicationData);
    return this.post('/medications/user-medications', medicationData);
  }

  async updateUserMedication(userMedicationId, medicationData) {
    console.log('🔵 API Service: Updating user medication:', userMedicationId, medicationData);
    return this.put(`/medications/user-medications/${userMedicationId}`, medicationData);
  }

  async deleteUserMedication(userMedicationId) {
    console.log('🔵 API Service: Deleting user medication:', userMedicationId);
    return this.delete(`/medications/user-medications/${userMedicationId}`);
  }

  async checkDrugInteractions(medications) {
    console.log('🔵 API Service: Checking drug interactions:', medications);
    return this.post('/medications/check-interactions', { medications });
  }

  async getUserDrugInteractions(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/medications/user-interactions?${queryString}` : '/medications/user-interactions';
    return this.get(endpoint);
  }

  async logMedicationDose(doseData) {
    console.log('🔵 API Service: Logging medication dose:', doseData);
    return this.post('/medications/dose-log', doseData);
  }

  async getMedicationDoseHistory(userMedicationId, days = 30) {
    return this.get(`/medications/dose-history/${userMedicationId}?days=${days}`);
  }

  async createMedicationReminder(reminderData) {
    console.log('🔵 API Service: Creating medication reminder:', reminderData);
    return this.post('/medications/reminders', reminderData);
  }

  async getMedicationReminders(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/medications/reminders?${queryString}` : '/medications/reminders';
    return this.get(endpoint);
  }

  async seedMedicationDatabase() {
    console.log('🔵 API Service: Seeding medication database');
    return this.post('/medications/seed-database');
  }

  // Health Analytics API methods
  async getHealthAnalytics(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/health-analytics?${queryString}` : '/health-analytics';
    console.log('🔵 API Service: Getting health analytics:', endpoint);
    return this.get(endpoint);
  }

  async getHealthInsights(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/health-analytics/insights?${queryString}` : '/health-analytics/insights';
    console.log('🔵 API Service: Getting health insights:', endpoint);
    return this.get(endpoint);
  }

  async getHealthTrends(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/health-analytics/trends?${queryString}` : '/health-analytics/trends';
    console.log('🔵 API Service: Getting health trends:', endpoint);
    return this.get(endpoint);
  }

  async generateHealthReport(reportData) {
    console.log('🔵 API Service: Generating health report:', reportData);
    return this.post('/health-analytics/report', reportData);
  }

  async getHistoricalAnalytics(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/health-analytics/historical?${queryString}` : '/health-analytics/historical';
    console.log('🔵 API Service: Getting historical analytics:', endpoint);
    return this.get(endpoint);
  }

  async deleteAnalyticsData(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/health-analytics?${queryString}` : '/health-analytics';
    console.log('🔵 API Service: Deleting analytics data:', endpoint);
    return this.delete(endpoint);
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService;

// Export the class for testing purposes
export { ApiService };