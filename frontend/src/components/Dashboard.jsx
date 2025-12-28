import { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { FiSend, FiMic, FiMicOff, FiPaperclip, FiSmile } from "react-icons/fi";
import { useChat } from "../hooks/useChat";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useTextToSpeech } from "../hooks/useTextToSpeech";
import LoadingSpinner from "./LoadingSpinner";

const Dashboard = () => {
  const [message, setMessage] = useState("");
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef(null);
  
  const { 
    messages, 
    isLoading, 
    sendMessage, 
    isConnected 
  } = useChat();
  
  const { 
    isSupported: speechSupported, 
    startListening, 
    stopListening, 
    transcript 
  } = useSpeechRecognition();
  
  const { speak, stop: stopSpeaking } = useTextToSpeech();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Update message with speech transcript
  useEffect(() => {
    if (transcript) {
      setMessage(transcript);
    }
  }, [transcript]);

  const handleSendMessage = async () => {
    if (!message.trim() || isLoading) return;
    
    const messageToSend = message;
    setMessage("");
    await sendMessage(messageToSend);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
      setIsListening(false);
    } else {
      startListening();
      setIsListening(true);
    }
  };

  const handleSpeakMessage = (text) => {
    speak(text);
  };

  return (
    <div className="h-full flex flex-col bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              AI Health Assistant
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {isConnected ? "Connected" : "Connecting..."} • Ask me anything about your health
            </p>
          </div>
          <div className={`w-3 h-3 rounded-full ${isConnected ? "bg-green-500" : "bg-yellow-500"}`} />
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4">
              <FiSmile className="w-8 h-8 text-white" />
            </div>
            <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Welcome to MyDoc AI
            </h4>
            <p className="text-gray-500 dark:text-gray-400 max-w-md">
              I'm here to help with your health questions, symptom analysis, medication information, and more. 
              How can I assist you today?
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-6 w-full max-w-2xl">
              {[
                "Check my symptoms",
                "Medication interactions",
                "Health tips for today",
                "Analyze my mood"
              ].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setMessage(suggestion)}
                  className="p-3 text-left bg-gray-50 dark:bg-gray-800 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors border border-gray-200 dark:border-gray-600"
                >
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {suggestion}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] ${msg.sender === 'user' ? 'order-2' : 'order-1'}`}>
                  <div
                    className={`px-4 py-3 rounded-2xl ${
                      msg.sender === 'user'
                        ? 'bg-blue-500 text-white ml-auto'
                        : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
                    }`}
                  >
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className={`text-xs ${
                        msg.sender === 'user' 
                          ? 'text-blue-100' 
                          : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        {new Date(msg.timestamp).toLocaleTimeString()}
                      </span>
                      {msg.sender === 'assistant' && (
                        <button
                          onClick={() => handleSpeakMessage(msg.content)}
                          className="ml-2 p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          title="Read aloud"
                        >
                          <FiMic className="w-3 h-3 text-gray-500 dark:text-gray-400" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-2xl px-4 py-3">
                  <LoadingSpinner size="sm" />
                </div>
              </motion.div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your health question here..."
              className="w-full px-4 py-3 pr-12 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
              rows={1}
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
            <button
              type="button"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <FiPaperclip className="w-4 h-4" />
            </button>
          </div>
          
          {speechSupported && (
            <button
              onClick={toggleListening}
              className={`p-3 rounded-xl transition-colors ${
                isListening
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
              title={isListening ? "Stop listening" : "Start voice input"}
            >
              {isListening ? <FiMicOff className="w-5 h-5" /> : <FiMic className="w-5 h-5" />}
            </button>
          )}
          
          <button
            onClick={handleSendMessage}
            disabled={!message.trim() || isLoading}
            className="p-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Send message"
          >
            <FiSend className="w-5 h-5" />
          </button>
        </div>
        
        {isListening && (
          <div className="mt-2 text-sm text-blue-600 dark:text-blue-400 flex items-center">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse mr-2" />
            Listening... Speak now
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;