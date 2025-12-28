/**
 * Data export utilities for MyDoc Medical Assistant
 */

/**
 * Export user data in various formats
 */
export const performCompleteDataExport = async (format = 'json') => {
  try {
    console.log(`📤 Starting data export in ${format} format...`);
    
    // Get user data from various sources
    const userData = await gatherUserData();
    
    switch (format.toLowerCase()) {
      case 'json':
        return exportAsJSON(userData);
      case 'csv':
        return exportAsCSV(userData);
      case 'pdf':
        return exportAsPDF(userData);
      default:
        throw new Error(`Unsupported export format: ${format}`);
    }
    
  } catch (error) {
    console.error('❌ Data export failed:', error);
    throw error;
  }
};

/**
 * Gather user data from all sources
 */
const gatherUserData = async () => {
  const data = {
    profile: {},
    conversations: [],
    medicalHistory: [],
    preferences: {},
    exportDate: new Date().toISOString()
  };
  
  try {
    // Get profile data from localStorage
    const storedProfile = localStorage.getItem('userProfile');
    if (storedProfile) {
      data.profile = JSON.parse(storedProfile);
    }
    
    // Get conversation history
    const conversationHistory = localStorage.getItem('conversationHistory');
    if (conversationHistory) {
      data.conversations = JSON.parse(conversationHistory);
    }
    
    // Get medical history
    const medicalHistory = localStorage.getItem('medicalHistory');
    if (medicalHistory) {
      data.medicalHistory = JSON.parse(medicalHistory);
    }
    
    // Get user preferences
    const preferences = localStorage.getItem('userPreferences');
    if (preferences) {
      data.preferences = JSON.parse(preferences);
    }
    
    console.log('✅ User data gathered successfully');
    return data;
    
  } catch (error) {
    console.error('❌ Failed to gather user data:', error);
    return data; // Return partial data
  }
};

/**
 * Export data as JSON
 */
const exportAsJSON = (data) => {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  
  downloadFile(blob, `mydoc-data-export-${getDateString()}.json`);
  
  console.log('✅ JSON export completed');
  return { success: true, format: 'json' };
};

/**
 * Export data as CSV
 */
const exportAsCSV = (data) => {
  let csvContent = '';
  
  // Export conversations as CSV
  if (data.conversations && data.conversations.length > 0) {
    csvContent += 'Conversation Data\n';
    csvContent += 'Date,Sender,Message\n';
    
    data.conversations.forEach(conv => {
      if (conv.messages) {
        conv.messages.forEach(msg => {
          const date = new Date(msg.timestamp).toLocaleDateString();
          const sender = msg.sender || 'unknown';
          const message = (msg.text || msg.content || '').replace(/"/g, '""');
          csvContent += `"${date}","${sender}","${message}"\n`;
        });
      }
    });
  }
  
  // Add medical history
  if (data.medicalHistory && data.medicalHistory.length > 0) {
    csvContent += '\nMedical History\n';
    csvContent += 'Date,Type,Description\n';
    
    data.medicalHistory.forEach(record => {
      const date = new Date(record.date || record.timestamp).toLocaleDateString();
      const type = record.type || 'General';
      const description = (record.description || record.notes || '').replace(/"/g, '""');
      csvContent += `"${date}","${type}","${description}"\n`;
    });
  }
  
  const blob = new Blob([csvContent], { type: 'text/csv' });
  downloadFile(blob, `mydoc-data-export-${getDateString()}.csv`);
  
  console.log('✅ CSV export completed');
  return { success: true, format: 'csv' };
};

/**
 * Export data as PDF (simplified version)
 */
const exportAsPDF = (data) => {
  // For a full PDF implementation, you'd use a library like jsPDF
  // For now, we'll create a simple HTML version that can be printed to PDF
  
  let htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>MyDoc Data Export</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        .section { margin-bottom: 30px; }
        .message { margin-bottom: 10px; padding: 10px; border-left: 3px solid #007bff; }
        .user-message { border-left-color: #28a745; }
        .ai-message { border-left-color: #007bff; }
        .timestamp { font-size: 0.8em; color: #666; }
      </style>
    </head>
    <body>
      <h1>MyDoc Medical Assistant - Data Export</h1>
      <p>Export Date: ${new Date().toLocaleDateString()}</p>
  `;
  
  // Add profile information
  if (data.profile && Object.keys(data.profile).length > 0) {
    htmlContent += `
      <div class="section">
        <h2>Profile Information</h2>
        <p><strong>Email:</strong> ${data.profile.email || 'Not provided'}</p>
        <p><strong>Display Name:</strong> ${data.profile.displayName || 'Not provided'}</p>
      </div>
    `;
  }
  
  // Add conversations
  if (data.conversations && data.conversations.length > 0) {
    htmlContent += '<div class="section"><h2>Conversation History</h2>';
    
    data.conversations.forEach((conv, index) => {
      htmlContent += `<h3>Conversation ${index + 1}</h3>`;
      
      if (conv.messages) {
        conv.messages.forEach(msg => {
          const messageClass = msg.sender === 'user' ? 'user-message' : 'ai-message';
          const timestamp = new Date(msg.timestamp).toLocaleString();
          
          htmlContent += `
            <div class="message ${messageClass}">
              <div><strong>${msg.sender === 'user' ? 'You' : 'MyDoc AI'}:</strong> ${msg.text || msg.content || ''}</div>
              <div class="timestamp">${timestamp}</div>
            </div>
          `;
        });
      }
    });
    
    htmlContent += '</div>';
  }
  
  // Add medical history
  if (data.medicalHistory && data.medicalHistory.length > 0) {
    htmlContent += '<div class="section"><h2>Medical History</h2>';
    
    data.medicalHistory.forEach(record => {
      const date = new Date(record.date || record.timestamp).toLocaleDateString();
      htmlContent += `
        <div class="message">
          <div><strong>${record.type || 'Medical Record'}:</strong> ${record.description || record.notes || ''}</div>
          <div class="timestamp">${date}</div>
        </div>
      `;
    });
    
    htmlContent += '</div>';
  }
  
  htmlContent += '</body></html>';
  
  // Create blob and download
  const blob = new Blob([htmlContent], { type: 'text/html' });
  downloadFile(blob, `mydoc-data-export-${getDateString()}.html`);
  
  console.log('✅ PDF/HTML export completed');
  return { success: true, format: 'pdf' };
};

/**
 * Download file helper
 */
const downloadFile = (blob, filename) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Get formatted date string for filenames
 */
const getDateString = () => {
  const now = new Date();
  return now.toISOString().split('T')[0]; // YYYY-MM-DD format
};

/**
 * Clear all user data (for account deletion)
 */
export const clearAllUserData = () => {
  try {
    console.log('🗑️  Clearing all user data...');
    
    const keysToRemove = [
      'userProfile',
      'conversationHistory',
      'medicalHistory',
      'userPreferences',
      'userSettings',
      'journalDraft',
      'lastActivity',
      'sessionData'
    ];
    
    keysToRemove.forEach(key => {
      localStorage.removeItem(key);
    });
    
    // Clear session storage
    sessionStorage.clear();
    
    console.log('✅ All user data cleared');
    return true;
    
  } catch (error) {
    console.error('❌ Failed to clear user data:', error);
    return false;
  }
};

/**
 * Get data export summary
 */
export const getDataExportSummary = async () => {
  try {
    const data = await gatherUserData();
    
    return {
      profile: !!data.profile && Object.keys(data.profile).length > 0,
      conversationCount: data.conversations ? data.conversations.length : 0,
      medicalRecordCount: data.medicalHistory ? data.medicalHistory.length : 0,
      hasPreferences: !!data.preferences && Object.keys(data.preferences).length > 0,
      totalDataSize: JSON.stringify(data).length
    };
    
  } catch (error) {
    console.error('❌ Failed to get data export summary:', error);
    return {
      profile: false,
      conversationCount: 0,
      medicalRecordCount: 0,
      hasPreferences: false,
      totalDataSize: 0
    };
  }
};