/**
 * Enhanced Speech Service for Medical AI Assistant
 * Provides advanced speech recognition and synthesis with medical terminology support
 */

class SpeechService {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.isSupported = this.checkSupport();
    this.settings = {
      language: 'en-US',
      continuous: false,
      interimResults: true,
      maxAlternatives: 3,
      voiceSpeed: 0.9,
      voicePitch: 1.0,
      voiceVolume: 1.0,
      preferredVoice: null,
      medicalTermsEnabled: true,
      commandsEnabled: true,
      autoSpeak: true
    };
    
    // Medical terminology dictionary for better recognition
    this.medicalTerms = [
      'acetaminophen', 'ibuprofen', 'aspirin', 'antibiotic', 'prescription',
      'symptoms', 'diagnosis', 'treatment', 'medication', 'dosage',
      'headache', 'fever', 'nausea', 'dizziness', 'fatigue',
      'chest pain', 'shortness of breath', 'abdominal pain',
      'hypertension', 'diabetes', 'asthma', 'allergies',
      'blood pressure', 'heart rate', 'temperature',
      'doctor', 'physician', 'specialist', 'emergency', 'urgent care',
      'pharmacy', 'hospital', 'clinic', 'appointment'
    ];

    // Voice commands for navigation
    this.voiceCommands = {
      'go to medical history': () => this.executeCommand('navigate', '/medical-history'),
      'open symptom checker': () => this.executeCommand('navigate', '/symptom-checker'),
      'show health analytics': () => this.executeCommand('navigate', '/health-analytics'),
      'check drug interactions': () => this.executeCommand('navigate', '/drug-interactions'),
      'clear chat': () => this.executeCommand('action', 'clear-chat'),
      'start new conversation': () => this.executeCommand('action', 'new-conversation'),
      'repeat last message': () => this.executeCommand('action', 'repeat-message'),
      'stop speaking': () => this.executeCommand('action', 'stop-speech'),
      'enable voice': () => this.executeCommand('action', 'enable-voice'),
      'disable voice': () => this.executeCommand('action', 'disable-voice'),
      'help': () => this.executeCommand('action', 'show-help')
    };

    this.callbacks = {
      onResult: null,
      onError: null,
      onStart: null,
      onEnd: null,
      onCommand: null,
      onInterimResult: null
    };

    this.init();
  }

  /**
   * Initialize the speech service
   */
  init() {
    this.loadSettings();
    this.initializeSpeechRecognition();
    this.loadVoices();
    
    // Listen for voice changes
    if (this.synthesis) {
      this.synthesis.addEventListener('voiceschanged', () => {
        this.loadVoices();
      });
    }
  }

  /**
   * Check if speech recognition and synthesis are supported
   */
  checkSupport() {
    const recognition = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    const synthesis = 'speechSynthesis' in window;
    
    return {
      recognition,
      synthesis,
      full: recognition && synthesis
    };
  }

  /**
   * Load saved settings from localStorage
   */
  loadSettings() {
    const saved = localStorage.getItem('mydoc-speech-settings');
    if (saved) {
      this.settings = { ...this.settings, ...JSON.parse(saved) };
    }
  }

  /**
   * Save settings to localStorage
   */
  saveSettings() {
    localStorage.setItem('mydoc-speech-settings', JSON.stringify(this.settings));
  }

  /**
   * Initialize speech recognition with enhanced settings
   */
  initializeSpeechRecognition() {
    if (!this.isSupported.recognition) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    
    // Configure recognition settings
    this.recognition.lang = this.settings.language;
    this.recognition.continuous = this.settings.continuous;
    this.recognition.interimResults = this.settings.interimResults;
    this.recognition.maxAlternatives = this.settings.maxAlternatives;

    // Set up event handlers
    this.recognition.onstart = () => {
      this.isListening = true;
      this.callbacks.onStart?.();
    };

    this.recognition.onend = () => {
      this.isListening = false;
      this.callbacks.onEnd?.();
    };

    this.recognition.onerror = (event) => {
      this.isListening = false;
      this.handleRecognitionError(event.error);
    };

    this.recognition.onresult = (event) => {
      this.handleRecognitionResult(event);
    };
  }

  /**
   * Handle speech recognition results
   */
  handleRecognitionResult(event) {
    let finalTranscript = '';
    let interimTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const result = event.results[i];
      const transcript = result[0].transcript;

      if (result.isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }

    // Process interim results
    if (interimTranscript && this.callbacks.onInterimResult) {
      this.callbacks.onInterimResult(interimTranscript);
    }

    // Process final results
    if (finalTranscript) {
      const processedText = this.processMedicalTerms(finalTranscript);
      
      // Check for voice commands first
      if (this.settings.commandsEnabled && this.isVoiceCommand(processedText)) {
        this.handleVoiceCommand(processedText);
      } else {
        this.callbacks.onResult?.(processedText);
      }
    }
  }

  /**
   * Process medical terms for better accuracy
   */
  processMedicalTerms(text) {
    if (!this.settings.medicalTermsEnabled) return text;

    let processedText = text.toLowerCase();
    
    // Replace common misrecognitions with correct medical terms
    const corrections = {
      'acetaminophen': ['acetaminophen', 'paracetamol', 'tylenol'],
      'ibuprofen': ['ibuprofen', 'advil', 'motrin'],
      'prescription': ['prescription', 'script', 'rx'],
      'symptoms': ['symptoms', 'symptom'],
      'diagnosis': ['diagnosis', 'diagnose'],
      'medication': ['medication', 'medicine', 'meds'],
      'emergency': ['emergency', 'urgent', 'critical']
    };

    Object.entries(corrections).forEach(([correct, variants]) => {
      variants.forEach(variant => {
        const regex = new RegExp(`\\b${variant}\\b`, 'gi');
        processedText = processedText.replace(regex, correct);
      });
    });

    return processedText;
  }

  /**
   * Check if text contains a voice command
   */
  isVoiceCommand(text) {
    const lowerText = text.toLowerCase().trim();
    return Object.keys(this.voiceCommands).some(command => 
      lowerText.includes(command.toLowerCase())
    );
  }

  /**
   * Handle voice command execution
   */
  handleVoiceCommand(text) {
    const lowerText = text.toLowerCase().trim();
    
    for (const [command, action] of Object.entries(this.voiceCommands)) {
      if (lowerText.includes(command.toLowerCase())) {
        action();
        this.callbacks.onCommand?.(command, text);
        break;
      }
    }
  }

  /**
   * Execute voice command
   */
  executeCommand(type, payload) {
    const event = new CustomEvent('voice-command', {
      detail: { type, payload }
    });
    window.dispatchEvent(event);
  }

  /**
   * Handle speech recognition errors
   */
  handleRecognitionError(error) {
    let errorMessage = 'Speech recognition error occurred';
    
    switch (error) {
      case 'no-speech':
        errorMessage = 'No speech detected. Please try again.';
        break;
      case 'audio-capture':
        errorMessage = 'Microphone access denied or not available.';
        break;
      case 'not-allowed':
        errorMessage = 'Microphone permission denied. Please enable microphone access.';
        break;
      case 'network':
        errorMessage = 'Network error occurred during speech recognition.';
        break;
      case 'service-not-allowed':
        errorMessage = 'Speech recognition service not allowed.';
        break;
      case 'bad-grammar':
        errorMessage = 'Speech recognition grammar error.';
        break;
      case 'language-not-supported':
        errorMessage = 'Language not supported for speech recognition.';
        break;
      default:
        // Don't show error for common browser issues
        console.warn('Speech recognition error:', error);
        return; // Don't call error callback for unknown errors
    }

    this.callbacks.onError?.(error, errorMessage);
  }

  /**
   * Load available voices for text-to-speech
   */
  loadVoices() {
    if (!this.isSupported.synthesis) return;

    const voices = this.synthesis.getVoices();
    this.availableVoices = voices;

    // Find preferred voice or select best default
    if (!this.settings.preferredVoice && voices.length > 0) {
      // Prefer English voices, then female voices for medical context
      const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
      const femaleVoices = englishVoices.filter(voice => 
        voice.name.toLowerCase().includes('female') || 
        voice.name.toLowerCase().includes('woman') ||
        voice.name.toLowerCase().includes('samantha') ||
        voice.name.toLowerCase().includes('karen')
      );
      
      this.settings.preferredVoice = femaleVoices[0]?.name || englishVoices[0]?.name || voices[0]?.name;
      this.saveSettings();
    }
  }

  /**
   * Start speech recognition
   */
  startListening() {
    if (!this.isSupported.recognition) {
      this.callbacks.onError?.('not-supported', 'Speech recognition is not supported in this browser');
      return false;
    }

    if (this.isListening) {
      return false;
    }

    try {
      this.recognition.start();
      return true;
    } catch (error) {
      this.callbacks.onError?.('start-error', 'Failed to start speech recognition');
      return false;
    }
  }

  /**
   * Stop speech recognition
   */
  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }

  /**
   * Speak text with enhanced voice synthesis
   */
  speak(text, options = {}) {
    if (!this.isSupported.synthesis || !text) return false;

    // Stop any current speech
    this.stopSpeaking();

    // Clean text for better speech
    const cleanText = this.cleanTextForSpeech(text);
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    
    // Apply settings
    utterance.rate = options.rate || this.settings.voiceSpeed;
    utterance.pitch = options.pitch || this.settings.voicePitch;
    utterance.volume = options.volume || this.settings.voiceVolume;
    utterance.lang = options.language || this.settings.language;

    // Set voice
    if (this.settings.preferredVoice) {
      const voice = this.availableVoices?.find(v => v.name === this.settings.preferredVoice);
      if (voice) {
        utterance.voice = voice;
      }
    }

    // Add event listeners
    utterance.onstart = () => {
      this.isSpeaking = true;
    };

    utterance.onend = () => {
      this.isSpeaking = false;
    };

    utterance.onerror = (event) => {
      this.isSpeaking = false;
      console.warn('Text-to-speech error:', event.error);
      // Don't show error to user for common TTS issues
      if (event.error !== 'interrupted' && event.error !== 'canceled') {
        this.callbacks.onError?.('speech-error', 'Text-to-speech error occurred');
      }
    };

    // Speak the text
    this.synthesis.speak(utterance);
    return true;
  }

  /**
   * Clean text for better speech synthesis
   */
  cleanTextForSpeech(text) {
    return text
      // Remove markdown formatting
      .replace(/[*_`#]/g, '')
      // Remove emoji shortcodes
      .replace(/:[^:\s]+:/g, '')
      // Replace common abbreviations
      .replace(/\bDr\./g, 'Doctor')
      .replace(/\bMr\./g, 'Mister')
      .replace(/\bMrs\./g, 'Missus')
      .replace(/\bMs\./g, 'Miss')
      // Add pauses for better flow
      .replace(/\. /g, '. ')
      .replace(/\? /g, '? ')
      .replace(/! /g, '! ')
      // Clean up extra whitespace
      .replace(/\s+/g, ' ')
      .trim();
  }

  /**
   * Stop current speech synthesis
   */
  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel();
      this.isSpeaking = false;
    }
  }

  /**
   * Set callback functions
   */
  setCallbacks(callbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * Update settings
   */
  updateSettings(newSettings) {
    this.settings = { ...this.settings, ...newSettings };
    this.saveSettings();
    
    // Reinitialize recognition if language changed
    if (newSettings.language && this.recognition) {
      this.recognition.lang = newSettings.language;
    }
  }

  /**
   * Get current settings
   */
  getSettings() {
    return { ...this.settings };
  }

  /**
   * Get available voices
   */
  getAvailableVoices() {
    return this.availableVoices || [];
  }

  /**
   * Get support status
   */
  getSupport() {
    return this.isSupported;
  }

  /**
   * Test speech recognition
   */
  testRecognition() {
    return new Promise((resolve, reject) => {
      if (!this.isSupported.recognition) {
        reject(new Error('Speech recognition not supported'));
        return;
      }

      const originalCallbacks = { ...this.callbacks };
      
      this.setCallbacks({
        onResult: (text) => {
          this.setCallbacks(originalCallbacks);
          resolve(text);
        },
        onError: (error, message) => {
          this.setCallbacks(originalCallbacks);
          reject(new Error(message));
        }
      });

      if (!this.startListening()) {
        this.setCallbacks(originalCallbacks);
        reject(new Error('Failed to start listening'));
      }
    });
  }

  /**
   * Test speech synthesis
   */
  testSynthesis(text = 'Hello, this is a test of the speech synthesis system.') {
    return new Promise((resolve, reject) => {
      if (!this.isSupported.synthesis) {
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      
      utterance.onend = () => resolve(true);
      utterance.onerror = () => reject(new Error('Speech synthesis failed'));

      this.synthesis.speak(utterance);
    });
  }

  /**
   * Get voice command help
   */
  getVoiceCommandHelp() {
    return Object.keys(this.voiceCommands).map(command => ({
      command,
      description: this.getCommandDescription(command)
    }));
  }

  /**
   * Get command description
   */
  getCommandDescription(command) {
    const descriptions = {
      'go to medical history': 'Navigate to your medical history page',
      'open symptom checker': 'Open the symptom checker tool',
      'show health analytics': 'Display your health analytics dashboard',
      'check drug interactions': 'Open drug interaction checker',
      'clear chat': 'Clear the current chat conversation',
      'start new conversation': 'Start a new chat conversation',
      'repeat last message': 'Repeat the last AI response',
      'stop speaking': 'Stop current speech output',
      'enable voice': 'Enable voice responses',
      'disable voice': 'Disable voice responses',
      'help': 'Show voice command help'
    };
    
    return descriptions[command] || 'Voice command';
  }
}

// Create singleton instance
const speechService = new SpeechService();

export default speechService;