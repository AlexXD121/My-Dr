/**
 * Voice Notification Service
 * Provides voice output for system notifications and alerts
 */

import speechService from './speechService';

class VoiceNotificationService {
  constructor() {
    this.isEnabled = true;
    this.notificationQueue = [];
    this.isProcessing = false;
    this.settings = {
      enabled: true,
      priority: {
        emergency: 1,
        warning: 2,
        info: 3,
        success: 4
      },
      voiceSettings: {
        rate: 1.0,
        pitch: 1.1,
        volume: 1.0
      }
    };
    
    this.init();
  }

  /**
   * Initialize the voice notification service
   */
  init() {
    this.loadSettings();
    this.setupEventListeners();
  }

  /**
   * Load settings from localStorage
   */
  loadSettings() {
    const saved = localStorage.getItem('mydoc-voice-notifications');
    if (saved) {
      this.settings = { ...this.settings, ...JSON.parse(saved) };
    }
    this.isEnabled = this.settings.enabled;
  }

  /**
   * Save settings to localStorage
   */
  saveSettings() {
    localStorage.setItem('mydoc-voice-notifications', JSON.stringify(this.settings));
  }

  /**
   * Setup event listeners for various notification types
   */
  setupEventListeners() {
    // Listen for toast notifications
    window.addEventListener('toast-notification', (event) => {
      this.handleToastNotification(event.detail);
    });

    // Listen for system alerts
    window.addEventListener('system-alert', (event) => {
      this.handleSystemAlert(event.detail);
    });

    // Listen for medical alerts
    window.addEventListener('medical-alert', (event) => {
      this.handleMedicalAlert(event.detail);
    });

    // Listen for connection status changes
    window.addEventListener('connection-status', (event) => {
      this.handleConnectionStatus(event.detail);
    });

    // Listen for voice command feedback
    window.addEventListener('voice-command-feedback', (event) => {
      this.handleVoiceCommandFeedback(event.detail);
    });
  }

  /**
   * Handle toast notification
   */
  handleToastNotification(notification) {
    if (!this.isEnabled) return;

    const { type, message, title } = notification;
    const priority = this.getPriorityByType(type);
    
    const voiceMessage = title ? `${title}. ${message}` : message;
    
    this.queueNotification({
      message: voiceMessage,
      priority,
      type,
      settings: this.getVoiceSettingsByType(type)
    });
  }

  /**
   * Handle system alert
   */
  handleSystemAlert(alert) {
    if (!this.isEnabled) return;

    const { level, message, action } = alert;
    const priority = this.getPriorityByLevel(level);
    
    let voiceMessage = message;
    if (action) {
      voiceMessage += ` ${action}`;
    }
    
    this.queueNotification({
      message: voiceMessage,
      priority,
      type: 'system',
      settings: this.getVoiceSettingsByLevel(level),
      urgent: level === 'emergency' || level === 'critical'
    });
  }

  /**
   * Handle medical alert
   */
  handleMedicalAlert(alert) {
    if (!this.isEnabled) return;

    const { severity, message, recommendation } = alert;
    const priority = 1; // Medical alerts are always high priority
    
    let voiceMessage = `Medical Alert. ${message}`;
    if (recommendation) {
      voiceMessage += ` Recommendation: ${recommendation}`;
    }
    
    this.queueNotification({
      message: voiceMessage,
      priority,
      type: 'medical',
      settings: {
        rate: 0.9,
        pitch: 1.1,
        volume: 1.0
      },
      urgent: severity === 'high' || severity === 'emergency'
    });
  }

  /**
   * Handle connection status changes
   */
  handleConnectionStatus(status) {
    if (!this.isEnabled) return;

    const messages = {
      connected: 'Connection restored',
      disconnected: 'Connection lost. Working offline',
      reconnecting: 'Attempting to reconnect',
      error: 'Connection error occurred'
    };

    const message = messages[status.type] || 'Connection status changed';
    
    this.queueNotification({
      message,
      priority: status.type === 'error' ? 2 : 3,
      type: 'connection',
      settings: this.settings.voiceSettings
    });
  }

  /**
   * Handle voice command feedback
   */
  handleVoiceCommandFeedback(feedback) {
    if (!this.isEnabled) return;

    const { command, success, message } = feedback;
    
    let voiceMessage;
    if (success) {
      voiceMessage = message || `Command executed: ${command}`;
    } else {
      voiceMessage = message || `Command failed: ${command}`;
    }
    
    this.queueNotification({
      message: voiceMessage,
      priority: 4,
      type: 'command',
      settings: this.settings.voiceSettings
    });
  }

  /**
   * Queue a notification for voice output
   */
  queueNotification(notification) {
    // If urgent, add to front of queue
    if (notification.urgent) {
      this.notificationQueue.unshift(notification);
    } else {
      this.notificationQueue.push(notification);
    }

    // Sort queue by priority
    this.notificationQueue.sort((a, b) => a.priority - b.priority);

    // Process queue if not already processing
    if (!this.isProcessing) {
      this.processQueue();
    }
  }

  /**
   * Process the notification queue
   */
  async processQueue() {
    if (this.notificationQueue.length === 0 || this.isProcessing) {
      return;
    }

    this.isProcessing = true;

    while (this.notificationQueue.length > 0) {
      const notification = this.notificationQueue.shift();
      
      try {
        await this.speakNotification(notification);
        
        // Small delay between notifications
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (error) {
        console.error('Error speaking notification:', error);
      }
    }

    this.isProcessing = false;
  }

  /**
   * Speak a notification
   */
  async speakNotification(notification) {
    return new Promise((resolve, reject) => {
      const { message, settings } = notification;
      
      // Clean message for speech
      const cleanMessage = this.cleanMessageForSpeech(message);
      
      // Use speech service to speak
      const success = speechService.speak(cleanMessage, settings);
      
      if (success) {
        // Wait for speech to complete
        const checkComplete = () => {
          if (!speechService.isSpeaking) {
            resolve();
          } else {
            setTimeout(checkComplete, 100);
          }
        };
        setTimeout(checkComplete, 100);
      } else {
        reject(new Error('Failed to start speech synthesis'));
      }
    });
  }

  /**
   * Clean message for better speech output
   */
  cleanMessageForSpeech(message) {
    return message
      // Remove HTML tags
      .replace(/<[^>]*>/g, '')
      // Remove excessive punctuation
      .replace(/[!]{2,}/g, '!')
      .replace(/[?]{2,}/g, '?')
      // Replace common abbreviations
      .replace(/\bAPI\b/g, 'A P I')
      .replace(/\bURL\b/g, 'U R L')
      .replace(/\bHTTP\b/g, 'H T T P')
      // Add pauses for better flow
      .replace(/\. /g, '. ... ')
      .replace(/! /g, '! ... ')
      .replace(/\? /g, '? ... ')
      // Clean up whitespace
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * Get priority by notification type
   */
  getPriorityByType(type) {
    const priorities = {
      error: 1,
      warning: 2,
      info: 3,
      success: 4
    };
    return priorities[type] || 3;
  }

  /**
   * Get priority by alert level
   */
  getPriorityByLevel(level) {
    const priorities = {
      emergency: 1,
      critical: 1,
      warning: 2,
      info: 3,
      success: 4
    };
    return priorities[level] || 3;
  }

  /**
   * Get voice settings by notification type
   */
  getVoiceSettingsByType(type) {
    const settings = {
      error: { rate: 0.9, pitch: 1.1, volume: 1.0 },
      warning: { rate: 0.9, pitch: 1.0, volume: 1.0 },
      info: { rate: 1.0, pitch: 1.0, volume: 0.9 },
      success: { rate: 1.1, pitch: 1.0, volume: 0.9 }
    };
    return settings[type] || this.settings.voiceSettings;
  }

  /**
   * Get voice settings by alert level
   */
  getVoiceSettingsByLevel(level) {
    const settings = {
      emergency: { rate: 0.8, pitch: 1.2, volume: 1.0 },
      critical: { rate: 0.8, pitch: 1.1, volume: 1.0 },
      warning: { rate: 0.9, pitch: 1.0, volume: 1.0 },
      info: { rate: 1.0, pitch: 1.0, volume: 0.9 },
      success: { rate: 1.1, pitch: 1.0, volume: 0.9 }
    };
    return settings[level] || this.settings.voiceSettings;
  }

  /**
   * Announce emergency information
   */
  announceEmergency(message, options = {}) {
    const emergencyMessage = `Emergency Alert! ${message}`;
    
    this.queueNotification({
      message: emergencyMessage,
      priority: 1,
      type: 'emergency',
      settings: {
        rate: 0.8,
        pitch: 1.2,
        volume: 1.0
      },
      urgent: true
    });

    // Also trigger system alert event
    window.dispatchEvent(new CustomEvent('system-alert', {
      detail: {
        level: 'emergency',
        message,
        ...options
      }
    }));
  }

  /**
   * Announce medication reminder
   */
  announceMedicationReminder(medication, time) {
    const message = `Medication reminder: Time to take ${medication}`;
    
    this.queueNotification({
      message,
      priority: 2,
      type: 'medication',
      settings: {
        rate: 0.9,
        pitch: 1.0,
        volume: 1.0
      }
    });
  }

  /**
   * Announce health insight
   */
  announceHealthInsight(insight) {
    const message = `Health insight: ${insight}`;
    
    this.queueNotification({
      message,
      priority: 3,
      type: 'health',
      settings: this.settings.voiceSettings
    });
  }

  /**
   * Enable/disable voice notifications
   */
  setEnabled(enabled) {
    this.isEnabled = enabled;
    this.settings.enabled = enabled;
    this.saveSettings();

    if (!enabled) {
      // Clear queue and stop current speech
      this.notificationQueue = [];
      speechService.stopSpeaking();
    }
  }

  /**
   * Update voice settings
   */
  updateVoiceSettings(newSettings) {
    this.settings.voiceSettings = { ...this.settings.voiceSettings, ...newSettings };
    this.saveSettings();
  }

  /**
   * Clear notification queue
   */
  clearQueue() {
    this.notificationQueue = [];
    speechService.stopSpeaking();
  }

  /**
   * Get current settings
   */
  getSettings() {
    return { ...this.settings };
  }

  /**
   * Test voice notifications
   */
  testNotification(type = 'info') {
    const testMessages = {
      info: 'This is a test information notification',
      success: 'This is a test success notification',
      warning: 'This is a test warning notification',
      error: 'This is a test error notification',
      emergency: 'This is a test emergency notification'
    };

    this.queueNotification({
      message: testMessages[type] || testMessages.info,
      priority: this.getPriorityByType(type),
      type,
      settings: this.getVoiceSettingsByType(type)
    });
  }
}

// Create singleton instance
const voiceNotificationService = new VoiceNotificationService();

export default voiceNotificationService;