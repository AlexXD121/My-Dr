/**
 * Female Voice Service for MyDoc AI
 * Provides sweet, natural female voice using free TTS models
 */

class FemaleVoiceService {
  constructor() {
    this.isInitialized = false;
    this.audioContext = null;
    this.currentAudio = null;
    this.voiceSettings = {
      model: 'jenny', // Sweet female voice
      speed: 0.9,
      pitch: 1.1, // Slightly higher for feminine sound
      emotion: 'caring',
      language: 'en'
    };
    
    // Free TTS endpoints (you can host these locally or use free services)
    this.ttsEndpoints = {
      // Local Coqui TTS server (recommended for production)
      local: 'http://localhost:5002/api/tts',
      
      // Free online services (backup options)
      elevenlabs_free: 'https://api.elevenlabs.io/v1/text-to-speech',
      coqui_free: 'https://coqui.ai/api/v1/tts',
      
      // Browser fallback with enhanced female voice
      browser: 'browser'
    };
    
    this.femaleVoices = {
      jenny: {
        name: 'Jenny - Sweet Medical Assistant',
        description: 'Warm, caring female voice perfect for medical consultations',
        model: 'tts_models/en/ljspeech/tacotron2-DDC',
        vocoder: 'vocoder_models/en/ljspeech/hifigan_v2',
        characteristics: ['warm', 'caring', 'professional', 'clear']
      },
      aria: {
        name: 'Aria - Gentle Healthcare Voice',
        description: 'Soft, reassuring voice for health guidance',
        model: 'tts_models/en/vctk/vits',
        speaker: 'p225', // Female speaker
        characteristics: ['gentle', 'reassuring', 'empathetic']
      },
      maya: {
        name: 'Maya - Smart Medical AI',
        description: 'Intelligent, friendly voice for medical AI',
        model: 'tts_models/en/ljspeech/glow-tts',
        characteristics: ['intelligent', 'friendly', 'trustworthy']
      }
    };
    
    this.init();
  }

  async init() {
    try {
      // Initialize audio context
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      
      // Load voice settings from localStorage
      const savedSettings = localStorage.getItem('mydoc-female-voice-settings');
      if (savedSettings) {
        this.voiceSettings = { ...this.voiceSettings, ...JSON.parse(savedSettings) };
      }
      
      // Test available TTS services
      await this.detectAvailableServices();
      
      this.isInitialized = true;
      console.log('🎤 Female Voice Service initialized successfully');
      
    } catch (error) {
      console.error('Failed to initialize Female Voice Service:', error);
      this.isInitialized = false;
    }
  }

  async detectAvailableServices() {
    const services = [];
    
    // Test local Coqui TTS server
    try {
      const response = await fetch(this.ttsEndpoints.local + '/health', { 
        method: 'GET',
        timeout: 2000 
      });
      if (response.ok) {
        services.push('local');
        console.log('✅ Local Coqui TTS server available');
      }
    } catch (error) {
      console.log('❌ Local TTS server not available');
    }
    
    // Always have browser fallback
    services.push('browser');
    
    this.availableServices = services;
    this.currentService = services[0];
  }

  async speak(text, options = {}) {
    if (!this.isInitialized) {
      await this.init();
    }

    const settings = { ...this.voiceSettings, ...options };
    
    try {
      // Stop any current speech
      this.stop();
      
      // Process text for better female voice delivery
      const processedText = this.processTextForFemaleVoice(text);
      
      // Choose TTS method based on available services
      if (this.currentService === 'local') {
        return await this.speakWithLocalTTS(processedText, settings);
      } else {
        return await this.speakWithBrowserTTS(processedText, settings);
      }
      
    } catch (error) {
      console.error('Speech synthesis failed:', error);
      // Fallback to browser TTS
      return await this.speakWithBrowserTTS(text, settings);
    }
  }

  async speakWithLocalTTS(text, settings) {
    try {
      const voice = this.femaleVoices[settings.model] || this.femaleVoices.jenny;
      
      const requestBody = {
        text: text,
        model_name: voice.model,
        vocoder_name: voice.vocoder,
        speaker_idx: voice.speaker || null,
        style_wav: null, // Can add emotional style later
        language_idx: null,
        speed: settings.speed,
        pitch: settings.pitch
      };

      const response = await fetch(this.ttsEndpoints.local, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`TTS API error: ${response.status}`);
      }

      const audioBlob = await response.blob();
      return await this.playAudioBlob(audioBlob);
      
    } catch (error) {
      console.error('Local TTS failed:', error);
      throw error;
    }
  }

  async speakWithBrowserTTS(text, settings) {
    return new Promise((resolve, reject) => {
      if (!window.speechSynthesis) {
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      
      // Find best female voice
      const voices = window.speechSynthesis.getVoices();
      const femaleVoice = this.selectBestFemaleVoice(voices);
      
      if (femaleVoice) {
        utterance.voice = femaleVoice;
      }
      
      // Apply settings for feminine, caring tone
      utterance.rate = settings.speed;
      utterance.pitch = settings.pitch;
      utterance.volume = 1.0;
      
      // Add emotional inflection for medical context
      if (settings.emotion === 'caring') {
        utterance.rate *= 0.9; // Slightly slower for caring tone
        utterance.pitch *= 1.05; // Slightly higher for warmth
      }

      utterance.onend = () => {
        this.currentAudio = null;
        resolve(true);
      };
      
      utterance.onerror = (error) => {
        this.currentAudio = null;
        reject(error);
      };

      this.currentAudio = utterance;
      window.speechSynthesis.speak(utterance);
    });
  }

  selectBestFemaleVoice(voices) {
    // Priority order for female voices
    const femaleVoiceNames = [
      // High-quality neural voices
      'Microsoft Aria Online (Natural) - English (United States)',
      'Microsoft Jenny Online (Natural) - English (United States)',
      'Google US English Female',
      'Microsoft Zira - English (United States)',
      
      // Standard female voices
      'Female',
      'Woman',
      'Samantha',
      'Victoria',
      'Karen',
      'Susan',
      'Allison',
      'Ava',
      'Serena'
    ];

    // Find exact matches first
    for (const voiceName of femaleVoiceNames) {
      const voice = voices.find(v => v.name === voiceName);
      if (voice) return voice;
    }

    // Find partial matches
    for (const voiceName of femaleVoiceNames) {
      const voice = voices.find(v => 
        v.name.toLowerCase().includes(voiceName.toLowerCase())
      );
      if (voice) return voice;
    }

    // Find any female voice
    const femaleVoice = voices.find(v => 
      v.name.toLowerCase().includes('female') ||
      v.name.toLowerCase().includes('woman') ||
      (!v.name.toLowerCase().includes('male') && 
       !v.name.toLowerCase().includes('man'))
    );

    return femaleVoice || voices[0];
  }

  processTextForFemaleVoice(text) {
    let processedText = text;

    // Add caring expressions for medical context
    const caringPhrases = {
      'Hello': 'Hello there',
      'Hi': 'Hi there',
      'I understand': 'I completely understand',
      'That sounds': 'That sounds concerning',
      'You should': 'I would recommend that you',
      'Take care': 'Please take good care of yourself',
      'Feel better': 'I hope you feel better soon'
    };

    Object.entries(caringPhrases).forEach(([original, caring]) => {
      const regex = new RegExp(`\\b${original}\\b`, 'gi');
      processedText = processedText.replace(regex, caring);
    });

    // Add gentle pauses for a more caring delivery
    processedText = processedText
      .replace(/\. /g, '. ... ')
      .replace(/\? /g, '? ... ')
      .replace(/! /g, '! ... ')
      .replace(/However,/g, '... However,')
      .replace(/Additionally,/g, '... Additionally,')
      .replace(/Important:/g, '... This is important: ...');

    // Soften medical terminology
    const medicalSoftening = {
      'diagnosis': 'medical assessment',
      'symptoms': 'what you\'re experiencing',
      'condition': 'health situation',
      'treatment': 'care plan',
      'medication': 'medicine',
      'side effects': 'possible reactions'
    };

    Object.entries(medicalSoftening).forEach(([medical, gentle]) => {
      const regex = new RegExp(`\\b${medical}\\b`, 'gi');
      processedText = processedText.replace(regex, gentle);
    });

    return processedText;
  }

  async playAudioBlob(audioBlob) {
    return new Promise((resolve, reject) => {
      const audio = new Audio();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      audio.src = audioUrl;
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        this.currentAudio = null;
        resolve(true);
      };
      
      audio.onerror = (error) => {
        URL.revokeObjectURL(audioUrl);
        this.currentAudio = null;
        reject(error);
      };

      this.currentAudio = audio;
      audio.play();
    });
  }

  stop() {
    if (this.currentAudio) {
      if (this.currentAudio instanceof Audio) {
        this.currentAudio.pause();
        this.currentAudio.currentTime = 0;
      } else if (this.currentAudio instanceof SpeechSynthesisUtterance) {
        window.speechSynthesis.cancel();
      }
      this.currentAudio = null;
    }
  }

  pause() {
    if (this.currentAudio instanceof Audio) {
      this.currentAudio.pause();
    } else if (window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
    }
  }

  resume() {
    if (this.currentAudio instanceof Audio) {
      this.currentAudio.play();
    } else if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
    }
  }

  isSpeaking() {
    if (this.currentAudio instanceof Audio) {
      return !this.currentAudio.paused;
    }
    return window.speechSynthesis && window.speechSynthesis.speaking;
  }

  // Voice customization methods
  setVoiceModel(modelName) {
    if (this.femaleVoices[modelName]) {
      this.voiceSettings.model = modelName;
      this.saveSettings();
    }
  }

  setSpeed(speed) {
    this.voiceSettings.speed = Math.max(0.1, Math.min(2.0, speed));
    this.saveSettings();
  }

  setPitch(pitch) {
    this.voiceSettings.pitch = Math.max(0.5, Math.min(2.0, pitch));
    this.saveSettings();
  }

  setEmotion(emotion) {
    const validEmotions = ['caring', 'professional', 'friendly', 'gentle'];
    if (validEmotions.includes(emotion)) {
      this.voiceSettings.emotion = emotion;
      this.saveSettings();
    }
  }

  getAvailableVoices() {
    return Object.entries(this.femaleVoices).map(([key, voice]) => ({
      id: key,
      ...voice
    }));
  }

  getCurrentSettings() {
    return { ...this.voiceSettings };
  }

  saveSettings() {
    localStorage.setItem('mydoc-female-voice-settings', JSON.stringify(this.voiceSettings));
  }

  // Test voice with sample medical text
  async testVoice(voiceModel = null) {
    const testText = "Hello! I'm your AI medical assistant. I'm here to help you with your health questions in a caring and professional manner. How are you feeling today?";
    
    const testSettings = voiceModel ? { ...this.voiceSettings, model: voiceModel } : this.voiceSettings;
    
    try {
      await this.speak(testText, testSettings);
      return { success: true, message: 'Voice test completed successfully' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  }
}

// Create singleton instance
const femaleVoiceService = new FemaleVoiceService();

export default femaleVoiceService;