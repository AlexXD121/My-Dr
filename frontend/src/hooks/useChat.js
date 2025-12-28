import { useState, useRef, useEffect, useCallback } from 'react';
import apiService from '../services/api';
import useSpeechRecognition from './useSpeechRecognition';
import useTextToSpeech from './useTextToSpeech';

export const useChat = () => {
  const [messages, setMessages] = useState([
    {
      text: "Hi, I'm MyDoc AI. How can I help you with your medical questions today? 🩺",
      sender: 'ai',
      timestamp: Date.now(),
      isTyping: true,
    },
  ]);
  
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [lastAiMessage, setLastAiMessage] = useState(null);
  
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  // Enhanced speech recognition with medical terminology
  const {
    isListening,
    transcript,
    interimTranscript,
    startListening: startSpeechRecognition,
    stopListening: stopSpeechRecognition,
    error: speechError
  } = useSpeechRecognition({
    continuous: false,
    interimResults: true,
    medicalTermsEnabled: true,
    commandsEnabled: true,
    onResult: (text) => {
      setInput(text);
      inputRef.current?.focus();
    },
    onError: (error, message) => {
      console.error('Speech recognition error:', error, message);
    },
    onCommand: (command, originalText) => {
      console.log('Voice command executed:', command);
    }
  });

  // Enhanced text-to-speech with natural voice
  const {
    speak,
    isSpeaking,
    stopSpeaking,
    isSupported: speechSupported
  } = useTextToSpeech({
    autoSpeak: voiceEnabled,
    rate: 0.9,
    pitch: 1.0,
    volume: 1.0,
    medicalPronunciation: true,
    emphasizeImportant: true
  });

  // Smooth scroll to bottom
  const scrollToBottom = useCallback(() => {
    chatEndRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'end'
    });
  }, []);

  useEffect(() => {
    const timer = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timer);
  }, [messages, scrollToBottom]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Update input when speech recognition provides transcript
  useEffect(() => {
    if (transcript && transcript !== input) {
      setInput(transcript);
    }
  }, [transcript]);

  // Enhanced text-to-speech function
  const speakText = useCallback((text) => {
    if (!voiceEnabled || !speechSupported) return;
    
    // Stop any current speech before starting new one
    stopSpeaking();
    
    // Speak with enhanced processing
    speak(text);
  }, [voiceEnabled, speechSupported, speak, stopSpeaking]);

  // Send message
  const handleSend = useCallback(async () => {
    console.log('🚀 handleSend called with input:', input);
    console.log('🚀 Current isTyping state:', isTyping);
    
    if (input.trim() === '' || isTyping) {
      console.log('❌ Returning early - empty input or typing');
      return;
    }

    const userMessage = {
      text: input.trim(),
      sender: 'user',
      timestamp: Date.now(),
      isTyping: false,
    };

    console.log('✅ Adding user message:', userMessage);
    setMessages(prev => [...prev, userMessage]);
    const currentInput = input.trim();
    setInput('');
    setIsTyping(true);
    console.log('✅ Set isTyping to true, cleared input');

    try {
      console.log('📡 Sending message to API:', currentInput);
      console.log('📡 API Base URL:', import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000');
      
      const data = await apiService.sendMessage(currentInput);
      console.log('✅ Received API response:', data);
      
      const aiResponse = {
        text: data.reply,
        sender: 'ai',
        timestamp: Date.now(),
        isTyping: true,
      };

      console.log('✅ Adding AI response:', aiResponse);
      setMessages(prev => [...prev, aiResponse]);
      setLastAiMessage(aiResponse);
      
      // Speak AI response with enhanced voice
      speakText(data.reply);
    } catch (error) {
      console.error('❌ DETAILED ERROR in handleSend:', {
        message: error.message,
        stack: error.stack,
        name: error.name,
        cause: error.cause,
        fullError: error
      });
      
      let errorMessage = `I apologize, but I'm having trouble processing your request. Error: ${error.message} 😔`;
      
      if (error.message.includes('Rate limit exceeded')) {
        errorMessage = "You're sending messages too quickly. Please wait a moment and try again. ⏰";
      } else if (error.message.includes('Network') || error.message.includes('fetch')) {
        errorMessage = `I'm having trouble connecting to the server. Error: ${error.message} 🌐`;
      } else if (error.message.includes('Failed to fetch')) {
        errorMessage = "Cannot connect to the backend server. Make sure it's running on port 8000. 🔌";
      }

      console.log('📝 Adding error message:', errorMessage);
      setMessages(prev => [
        ...prev,
        {
          text: errorMessage,
          sender: 'ai',
          timestamp: Date.now(),
          isTyping: true,
        },
      ]);
    } finally {
      console.log('🏁 Setting isTyping to false');
      setIsTyping(false);
    }
  }, [input, isTyping, speakText]);

  // Enhanced voice recognition functions
  const startListening = useCallback(() => {
    if (!startSpeechRecognition()) {
      alert('Speech recognition is not supported in this browser or microphone access was denied. Please try Chrome or Edge and ensure microphone permissions are granted.');
    }
  }, [startSpeechRecognition]);

  // Stop listening
  const stopListening = useCallback(() => {
    stopSpeechRecognition();
  }, [stopSpeechRecognition]);

  // Repeat last AI message
  const repeatLastMessage = useCallback(() => {
    if (lastAiMessage) {
      speakText(lastAiMessage.text);
    }
  }, [lastAiMessage, speakText]);

  // Toggle voice responses
  const toggleVoiceEnabled = useCallback((enabled) => {
    if (typeof enabled === 'boolean') {
      setVoiceEnabled(enabled);
    } else {
      setVoiceEnabled(prev => !prev);
    }
    
    // Stop current speech if disabling
    if (enabled === false || (!enabled && voiceEnabled)) {
      stopSpeaking();
    }
  }, [voiceEnabled, stopSpeaking]);

  // Clear chat
  const clearChat = useCallback(() => {
    setMessages([
      {
        text: "Hi, I'm MyDoc AI. How can I help you with your medical questions today? 🩺",
        sender: 'ai',
        timestamp: Date.now(),
        isTyping: true,
      },
    ]);
  }, []);

  return {
    messages,
    input,
    setInput,
    isTyping,
    isListening,
    voiceEnabled,
    setVoiceEnabled: toggleVoiceEnabled,
    chatEndRef,
    inputRef,
    handleSend,
    startListening,
    stopListening,
    clearChat,
    // Enhanced voice features
    isSpeaking,
    speechSupported,
    speechError,
    interimTranscript,
    repeatLastMessage,
    lastAiMessage,
    stopSpeaking
  };
};