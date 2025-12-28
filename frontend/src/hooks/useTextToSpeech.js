import { useState, useEffect, useCallback, useRef } from 'react';
import speechService from '../services/speechService';
import femaleVoiceService from '../services/femaleVoiceService';

/**
 * Enhanced Text-to-Speech Hook with Natural Voice Synthesis
 * Provides advanced speech synthesis with emotion and accessibility features
 */
export const useTextToSpeech = (options = {}) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [currentVoice, setCurrentVoice] = useState(null);
  const [error, setError] = useState(null);
  const [queue, setQueue] = useState([]);
  const [settings, setSettings] = useState({});

  const {
    autoSpeak = false,
    rate = 0.9,
    pitch = 1.0,
    volume = 1.0,
    voice = null,
    language = 'en-US',
    onStart,
    onEnd,
    onError,
    pauseBetweenSentences = 300,
    emphasizeImportant = true,
    medicalPronunciation = true
  } = options;

  const currentUtteranceRef = useRef(null);
  const queueTimeoutRef = useRef(null);

  // Initialize text-to-speech
  useEffect(() => {
    const support = speechService.getSupport();
    setIsSupported(support.synthesis);

    if (support.synthesis) {
      // Load available voices
      const voices = speechService.getAvailableVoices();
      setAvailableVoices(voices);

      // Set initial settings
      const initialSettings = {
        voiceSpeed: rate,
        voicePitch: pitch,
        voiceVolume: volume,
        language,
        preferredVoice: voice,
        autoSpeak
      };
      
      speechService.updateSettings(initialSettings);
      setSettings(speechService.getSettings());

      // Set current voice
      if (voice) {
        const selectedVoice = voices.find(v => v.name === voice);
        setCurrentVoice(selectedVoice);
      } else if (voices.length > 0) {
        // Auto-select best voice for medical context
        const bestVoice = selectBestVoice(voices, language);
        setCurrentVoice(bestVoice);
        speechService.updateSettings({ preferredVoice: bestVoice?.name });
      }
    }

    return () => {
      stopSpeaking();
      if (queueTimeoutRef.current) {
        clearTimeout(queueTimeoutRef.current);
      }
    };
  }, [rate, pitch, volume, voice, language, autoSpeak]);

  // Select best voice for medical context
  const selectBestVoice = useCallback((voices, lang) => {
    // Filter by language
    const langVoices = voices.filter(v => v.lang.startsWith(lang.split('-')[0]));
    
    if (langVoices.length === 0) return voices[0];

    // Prefer neural/premium voices
    const neuralVoices = langVoices.filter(v => 
      v.name.toLowerCase().includes('neural') ||
      v.name.toLowerCase().includes('premium') ||
      v.name.toLowerCase().includes('enhanced')
    );

    if (neuralVoices.length > 0) {
      // Prefer female voices for medical context (often perceived as more caring)
      const femaleNeural = neuralVoices.filter(v =>
        v.name.toLowerCase().includes('female') ||
        v.name.toLowerCase().includes('woman') ||
        v.name.toLowerCase().includes('aria') ||
        v.name.toLowerCase().includes('jenny') ||
        v.name.toLowerCase().includes('samantha')
      );
      
      if (femaleNeural.length > 0) return femaleNeural[0];
      return neuralVoices[0];
    }

    // Fallback to any female voice
    const femaleVoices = langVoices.filter(v =>
      v.name.toLowerCase().includes('female') ||
      v.name.toLowerCase().includes('woman') ||
      !v.name.toLowerCase().includes('male')
    );

    return femaleVoices[0] || langVoices[0];
  }, []);

  // Speak text with enhanced processing
  const speak = useCallback(async (text, speakOptions = {}) => {
    if (!isSupported || !text) {
      return false;
    }

    const processedText = processTextForSpeech(text, {
      emphasizeImportant,
      medicalPronunciation
    });

    const speechOptions = {
      rate: speakOptions.rate || rate,
      pitch: speakOptions.pitch || pitch,
      volume: speakOptions.volume || volume,
      language: speakOptions.language || language,
      voice: speakOptions.voice || currentVoice?.name
    };

    try {
      setError(null);
      setIsSpeaking(true);
      onStart?.();

      // Try female voice service first for better quality
      const femaleVoiceEnabled = localStorage.getItem('mydoc-use-female-voice') !== 'false';
      
      if (femaleVoiceEnabled) {
        try {
          const femaleSuccess = await femaleVoiceService.speak(processedText, {
            speed: speechOptions.rate,
            pitch: speechOptions.pitch,
            emotion: 'caring'
          });
          
          if (femaleSuccess) {
            // Monitor female voice service
            const checkFemaleVoiceEnd = () => {
              if (!femaleVoiceService.isSpeaking()) {
                setIsSpeaking(false);
                onEnd?.();
                processQueue();
              } else {
                setTimeout(checkFemaleVoiceEnd, 100);
              }
            };
            
            setTimeout(checkFemaleVoiceEnd, 100);
            return true;
          }
        } catch (femaleError) {
          console.warn('Female voice service failed, falling back to browser TTS:', femaleError);
        }
      }

      // Fallback to browser TTS
      const success = speechService.speak(processedText, speechOptions);
      
      if (!success) {
        throw new Error('Failed to start speech synthesis');
      }

      // Monitor speech end with error handling
      const checkSpeechEnd = () => {
        try {
          if (!speechService.isSpeaking) {
            setIsSpeaking(false);
            onEnd?.();
            processQueue();
          } else {
            setTimeout(checkSpeechEnd, 100);
          }
        } catch (error) {
          console.warn('Speech monitoring error:', error);
          setIsSpeaking(false);
          onEnd?.();
        }
      };
      
      setTimeout(checkSpeechEnd, 100);
      
      return true;
    } catch (error) {
      setError(error.message);
      setIsSpeaking(false);
      onError?.(error.message);
      return false;
    }
  }, [isSupported, rate, pitch, volume, language, currentVoice, emphasizeImportant, medicalPronunciation, onStart, onEnd, onError]);

  // Process text for better speech synthesis
  const processTextForSpeech = useCallback((text, options = {}) => {
    let processedText = text;

    // Clean markdown and formatting
    processedText = processedText
      .replace(/[*_`]/g, '')
      .replace(/#{1,6}\s/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/:[^:\s]+:/g, '');

    // Handle medical pronunciations
    if (options.medicalPronunciation) {
      const medicalTerms = {
        'acetaminophen': 'uh-see-tuh-MIN-uh-fen',
        'ibuprofen': 'eye-BYOO-proh-fen',
        'hypertension': 'high-per-TEN-shun',
        'pneumonia': 'new-MOH-nee-uh',
        'bronchitis': 'bron-KYE-tis',
        'pharyngitis': 'fair-in-JYE-tis',
        'gastroenteritis': 'gas-troh-en-ter-EYE-tis',
        'mg': 'milligrams',
        'ml': 'milliliters',
        'mcg': 'micrograms',
        'bid': 'twice daily',
        'tid': 'three times daily',
        'qid': 'four times daily',
        'prn': 'as needed'
      };

      Object.entries(medicalTerms).forEach(([term, pronunciation]) => {
        const regex = new RegExp(`\\b${term}\\b`, 'gi');
        processedText = processedText.replace(regex, pronunciation);
      });
    }

    // Add emphasis for important medical information
    if (options.emphasizeImportant) {
      // Add pauses before important warnings
      processedText = processedText
        .replace(/\b(warning|caution|important|emergency|urgent|critical)\b/gi, '... $1')
        .replace(/\b(seek immediate medical attention|call 911|go to emergency room)\b/gi, '... $1 ...')
        .replace(/\b(side effects|allergic reaction|overdose)\b/gi, '... $1');
    }

    // Add natural pauses
    processedText = processedText
      .replace(/\. /g, '. ... ')
      .replace(/\? /g, '? ... ')
      .replace(/! /g, '! ... ')
      .replace(/: /g, ': ... ')
      .replace(/; /g, '; ... ');

    // Clean up extra spaces
    processedText = processedText.replace(/\s+/g, ' ').trim();

    return processedText;
  }, []);

  // Add text to speech queue
  const addToQueue = useCallback((text, options = {}) => {
    const queueItem = {
      id: Date.now() + Math.random(),
      text,
      options,
      timestamp: Date.now()
    };

    setQueue(prev => [...prev, queueItem]);

    // Process queue if not currently speaking
    if (!isSpeaking) {
      processQueue();
    }
  }, [isSpeaking]);

  // Process speech queue
  const processQueue = useCallback(() => {
    if (queueTimeoutRef.current) {
      clearTimeout(queueTimeoutRef.current);
    }

    queueTimeoutRef.current = setTimeout(() => {
      setQueue(prev => {
        if (prev.length === 0 || isSpeaking) return prev;

        const [nextItem, ...remaining] = prev;
        speak(nextItem.text, nextItem.options);
        
        return remaining;
      });
    }, pauseBetweenSentences);
  }, [isSpeaking, speak, pauseBetweenSentences]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    // Stop both services
    speechService.stopSpeaking();
    femaleVoiceService.stop();
    
    setIsSpeaking(false);
    setQueue([]);
    
    if (queueTimeoutRef.current) {
      clearTimeout(queueTimeoutRef.current);
    }
  }, []);

  // Pause speaking
  const pauseSpeaking = useCallback(() => {
    if (speechService.synthesis && speechService.synthesis.speaking) {
      speechService.synthesis.pause();
    }
  }, []);

  // Resume speaking
  const resumeSpeaking = useCallback(() => {
    if (speechService.synthesis && speechService.synthesis.paused) {
      speechService.synthesis.resume();
    }
  }, []);

  // Change voice
  const changeVoice = useCallback((voiceName) => {
    const voice = availableVoices.find(v => v.name === voiceName);
    if (voice) {
      setCurrentVoice(voice);
      speechService.updateSettings({ preferredVoice: voiceName });
    }
  }, [availableVoices]);

  // Update speech settings
  const updateSettings = useCallback((newSettings) => {
    speechService.updateSettings(newSettings);
    setSettings(speechService.getSettings());
  }, []);

  // Test speech synthesis
  const testSpeech = useCallback(async (testText = 'Hello, this is a test of the speech synthesis system.') => {
    try {
      await speechService.testSynthesis(testText);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }, []);

  // Get voice information
  const getVoiceInfo = useCallback((voiceName) => {
    const voice = availableVoices.find(v => v.name === voiceName);
    if (!voice) return null;

    return {
      name: voice.name,
      language: voice.lang,
      gender: detectVoiceGender(voice.name),
      quality: detectVoiceQuality(voice.name),
      isDefault: voice.default,
      isLocal: voice.localService
    };
  }, [availableVoices]);

  // Detect voice gender from name
  const detectVoiceGender = useCallback((voiceName) => {
    const name = voiceName.toLowerCase();
    const femaleIndicators = ['female', 'woman', 'aria', 'jenny', 'samantha', 'karen', 'susan', 'victoria'];
    const maleIndicators = ['male', 'man', 'david', 'mark', 'daniel', 'ryan', 'alex'];
    
    if (femaleIndicators.some(indicator => name.includes(indicator))) return 'female';
    if (maleIndicators.some(indicator => name.includes(indicator))) return 'male';
    return 'unknown';
  }, []);

  // Detect voice quality from name
  const detectVoiceQuality = useCallback((voiceName) => {
    const name = voiceName.toLowerCase();
    if (name.includes('neural') || name.includes('premium') || name.includes('enhanced')) {
      return 'premium';
    }
    if (name.includes('standard') || name.includes('basic')) {
      return 'standard';
    }
    return 'unknown';
  }, []);

  // Speak medical disclaimer
  const speakDisclaimer = useCallback(() => {
    const disclaimer = "Please note: This information is for educational purposes only and should not replace professional medical advice. Always consult with a healthcare provider for medical concerns.";
    speak(disclaimer, { rate: 0.8, pitch: 0.9 });
  }, [speak]);

  // Female voice controls
  const enableFemaleVoice = useCallback((enabled = true) => {
    localStorage.setItem('mydoc-use-female-voice', enabled.toString());
  }, []);

  const isFemaleVoiceEnabled = useCallback(() => {
    return localStorage.getItem('mydoc-use-female-voice') !== 'false';
  }, []);

  return {
    // State
    isSpeaking,
    isSupported,
    availableVoices,
    currentVoice,
    error,
    queue: queue.length,
    settings,

    // Actions
    speak,
    addToQueue,
    stopSpeaking,
    pauseSpeaking,
    resumeSpeaking,
    
    // Voice management
    changeVoice,
    getVoiceInfo,
    
    // Settings
    updateSettings,
    
    // Female voice controls
    enableFemaleVoice,
    isFemaleVoiceEnabled,
    femaleVoiceService,
    
    // Utilities
    testSpeech,
    speakDisclaimer,
    processTextForSpeech
  };
};

export default useTextToSpeech;