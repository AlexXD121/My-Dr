import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { FiSettings } from 'react-icons/fi';
import { useChat } from '../hooks/useChat';
import ChatSettings from './ChatSettings';
import VoiceCommandHandler from './VoiceCommandHandler';
import FormattedAIMessage from './FormattedAIMessage';
import SimpleFormattedMessage from './SimpleFormattedMessage';


// Typing animation component
const TypingText = ({ text, speed = 30 }) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, speed]);

  return <span>{displayText}</span>;
};

// Message bubble component
const MessageBubble = ({ message, index, isMobile }) => {
  const isUser = message.sender === 'user';
  const isTyping = message.isTyping;
  const [showReactions, setShowReactions] = useState(false);
  const [selectedReaction, setSelectedReaction] = useState(null);

  const reactions = ['👍', '❤️', '😊', '🤔', '👏', '🙏'];

  const handleReaction = (reaction) => {
    setSelectedReaction(reaction);
    setShowReactions(false);
    // Here you could save the reaction to your backend
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.4,
        delay: index * 0.1,
        type: "spring",
        stiffness: 200,
        damping: 20
      }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 sm:mb-6 group px-2 sm:px-0`}
    >
      <div className={`flex items-end gap-2 sm:gap-3 max-w-[90%] sm:max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <motion.div
          className={`w-8 h-8 sm:w-10 sm:h-10 rounded-2xl flex items-center justify-center text-sm sm:text-lg shadow-lg ${isUser
            ? 'bg-gradient-to-br from-blue-600 to-gray-800'
            : 'bg-transparent animate-float'
            }`}
          whileHover={{ scale: isMobile ? 1 : 1.1, rotate: isMobile ? 0 : 5 }}
          whileTap={{ scale: 0.95 }}
        >
          {isUser ? '👤' : (
            <img
              src="/dr.png"
              alt="Dr. AI"
              className="w-full h-full rounded-2xl object-cover"
            />
          )}
        </motion.div>

        {/* Message content */}
        <div className="relative">
          <motion.div
            className={`
              px-3 py-3 sm:px-6 sm:py-4 rounded-2xl shadow-lg backdrop-blur-sm relative overflow-hidden
              ${isUser
                ? 'bg-blue-600 text-white rounded-br-md'
                : 'bg-white dark:bg-gray-800 text-black dark:text-white rounded-bl-md border border-gray-200 dark:border-gray-700 shadow-md'
              }
            `}
            whileHover={{ scale: isMobile ? 1 : 1.02, y: isMobile ? 0 : -2 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
            onHoverStart={() => !isUser && !isMobile && setShowReactions(true)}
            onHoverEnd={() => setShowReactions(false)}
            onTouchStart={() => !isUser && isMobile && setShowReactions(true)}
            onTouchEnd={() => isMobile && setTimeout(() => setShowReactions(false), 2000)}
          >
            {/* Shimmer effect for AI messages */}
            {!isUser && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
            )}

            <div className="relative z-10">
              {/* Debug message info */}
              <div className="text-xs bg-yellow-100 dark:bg-yellow-900/20 p-2 rounded mb-2">
                🔍 Message Debug: sender="{message.sender}", isUser={isUser.toString()}, isTyping={isTyping.toString()}
              </div>

              {isTyping ? (
                <TypingText text={message.text} speed={20} />
              ) : isUser ? (
                <div>
                  <div className="text-xs text-blue-500 mb-2">👤 USER MESSAGE</div>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown
                      components={{
                        code: ({ node, inline, className, children, ...props }) => {
                          return inline ? (
                            <code className="bg-black/10 dark:bg-white/10 px-1 py-0.5 rounded text-sm" {...props}>
                              {children}
                            </code>
                          ) : (
                            <pre className="bg-black/10 dark:bg-white/10 p-3 rounded-lg overflow-x-auto">
                              <code {...props}>{children}</code>
                            </pre>
                          );
                        }
                      }}
                    >
                      {message.text}
                    </ReactMarkdown>
                  </div>
                </div>
              ) : (
                // AI Message - Enhanced formatting applied directly
                <div className="space-y-4">
                  <div className="text-xs text-green-500 mb-2 bg-green-50 dark:bg-green-900/20 p-2 rounded">
                    🎨 Enhanced AI Response Formatting Active
                  </div>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown
                      components={{
                        h2: ({ children }) => (
                          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100 mb-3 mt-6 flex items-center gap-2 border-l-4 border-blue-500 pl-3">
                            {children}
                          </h2>
                        ),
                        h3: ({ children }) => (
                          <h3 className="text-lg font-medium text-gray-700 dark:text-gray-200 mb-2 mt-4">
                            {children}
                          </h3>
                        ),
                        p: ({ children }) => (
                          <p className="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed">
                            {children}
                          </p>
                        ),
                        ul: ({ children }) => (
                          <ul className="space-y-2 mb-4">{children}</ul>
                        ),
                        li: ({ children }) => (
                          <li className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
                            <span className="text-blue-500 mt-1 flex-shrink-0">•</span>
                            <span>{children}</span>
                          </li>
                        ),
                        strong: ({ children }) => (
                          <strong className="font-semibold text-gray-900 dark:text-white bg-blue-50 dark:bg-blue-900/30 px-1 py-0.5 rounded">
                            {children}
                          </strong>
                        ),
                        blockquote: ({ children }) => (
                          <blockquote className="border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900/20 p-4 my-4 rounded-r-lg">
                            <div className="text-blue-800 dark:text-blue-200">{children}</div>
                          </blockquote>
                        )
                      }}
                    >
                      {(() => {
                        let formatted = message.text || '';

                        // Remove AI assistant references
                        formatted = formatted.replace(/As a friendly AI,?\s*/gi, '');
                        formatted = formatted.replace(/As an AI,?\s*/gi, '');

                        // Add contextual heading
                        if (formatted.toLowerCase().includes('mental') || formatted.toLowerCase().includes('trauma') || formatted.toLowerCase().includes('sad')) {
                          formatted = `## 🧠 **Mental Health Support**\n\n${formatted}`;
                        } else {
                          formatted = `## 🩺 **Medical Information**\n\n${formatted}`;
                        }

                        // Convert numbered lists to bullet points
                        formatted = formatted.replace(/(\d+)\.\s*\*\*([^*]+)\*\*/g, '\n• **$2**');
                        formatted = formatted.replace(/(\d+)\.\s*([^\n]+)/g, '\n• **$2**');

                        // Highlight important terms
                        const terms = ['emotions', 'feelings', 'professional', 'help', 'support', 'mental health', 'sad'];
                        terms.forEach(term => {
                          const regex = new RegExp(`\\b(${term})\\b`, 'gi');
                          formatted = formatted.replace(regex, '**$1**');
                        });

                        // Add medical disclaimer
                        formatted += `\n\n---\n\n> 💡 **Medical Disclaimer:** This information is for educational purposes only. Always consult with a healthcare provider for medical concerns.`;

                        return formatted.trim();
                      })()}
                    </ReactMarkdown>
                  </div>
                </div>
              )}

              {/* DIRECT INLINE FORMATTING TEST */}
              {!isUser && !isTyping && (
                <div className="mt-4 border-t-2 border-purple-500 pt-4">
                  <div className="text-xs text-purple-500 mb-2 bg-purple-50 dark:bg-purple-900/20 p-2 rounded">
                    🎨 DIRECT INLINE FORMATTING (This should work!)
                  </div>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <ReactMarkdown>
                      {(() => {
                        let formatted = message.text;
                        // Remove AI references
                        formatted = formatted.replace(/As a friendly AI,?\s*/gi, '');
                        formatted = formatted.replace(/As an AI,?\s*/gi, '');
                        // Add heading
                        formatted = `## 🩺 **Medical Information**\n\n${formatted}`;
                        // Convert numbered lists
                        formatted = formatted.replace(/(\d+)\.\s*\*\*([^*]+)\*\*/g, '\n• **$2**');
                        formatted = formatted.replace(/(\d+)\.\s*([^\n]+)/g, '\n• **$2**');
                        // Highlight terms
                        formatted = formatted.replace(/\b(emotions|feelings|professional|help)\b/gi, '**$1**');
                        return formatted;
                      })()}
                    </ReactMarkdown>
                  </div>
                </div>
              )}

              <div className="flex items-center justify-between mt-1 sm:mt-2">
                <motion.time
                  className={`text-xs opacity-70 ${isUser ? 'text-white/80' : 'text-gray-600 dark:text-gray-400'
                    }`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 0.7 }}
                  transition={{ delay: 0.5 }}
                >
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </motion.time>

                {selectedReaction && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="text-lg"
                  >
                    {selectedReaction}
                  </motion.span>
                )}
              </div>
            </div>
          </motion.div>

          {/* Reaction picker */}
          <AnimatePresence>
            {showReactions && !isUser && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 10 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.8, y: 10 }}
                className={`absolute ${isMobile ? '-top-14' : '-top-12'} left-0 flex gap-1 bg-white dark:bg-gray-800 
                  rounded-full px-2 py-1 shadow-lg border border-gray-200 dark:border-gray-700 z-10`}
              >
                {reactions.map((reaction, i) => (
                  <motion.button
                    key={reaction}
                    onClick={() => handleReaction(reaction)}
                    className={`${isMobile ? 'w-10 h-10' : 'w-8 h-8'} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 
                      flex items-center justify-center text-sm transition-colors mobile-tap-target`}
                    whileHover={{ scale: isMobile ? 1.1 : 1.2 }}
                    whileTap={{ scale: 0.9 }}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                  >
                    {reaction}
                  </motion.button>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
};

export default function Mainbox() {
  const {
    messages,
    input,
    setInput,
    isTyping,
    isListening,
    setVoiceEnabled,
    chatEndRef,
    inputRef,
    handleSend,
    clearChat,
    // Enhanced voice features
    speechSupported,
    speechError,
    interimTranscript,
    repeatLastMessage,
    lastAiMessage
  } = useChat();

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  // Listen for window resize
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <main className="flex-1 flex flex-col relative overflow-hidden pb-safe-bottom bg-white dark:bg-gray-900">
      {/* Soothing animated background */}
      <div className="absolute inset-0 bg-white dark:bg-gray-900" />
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/30 via-transparent to-blue-50/20 dark:from-blue-900/20 dark:via-transparent dark:to-blue-900/10 animate-pulse" style={{ animationDuration: '8s' }} />

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto relative z-10 swipeable">
        <div className="max-w-4xl mx-auto px-2 sm:px-4 py-4 sm:py-8">
          {/* Welcome section */}
          {messages.length === 1 && (
            <motion.div
              className="text-center py-8 sm:py-16 px-4"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <motion.div
                className="w-16 h-16 sm:w-20 sm:h-20 mx-auto mb-4 sm:mb-6 rounded-3xl bg-transparent
                  flex items-center justify-center text-2xl sm:text-3xl shadow-2xl animate-float"
                whileHover={{ scale: isMobile ? 1.05 : 1.1, rotate: isMobile ? 0 : 5 }}
                whileTap={{ scale: 0.95 }}
              >
                <img
                  src="/dr.png"
                  alt="MyDoc AI"
                  className="w-full h-full rounded-3xl object-cover"
                />
              </motion.div>
              <motion.h2
                className="text-2xl sm:text-4xl font-bold gradient-text mb-3 sm:mb-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
              >
                Welcome to MyDoc AI
              </motion.h2>
              <motion.p
                className="text-black dark:text-white max-w-lg mx-auto text-base sm:text-lg leading-relaxed px-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
              >
                Your intelligent medical assistant powered by advanced AI. Ask me about symptoms, conditions, treatments, or general health questions. I'm here to help! ✨
              </motion.p>

              {/* Floating particles */}
              <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {[...Array(6)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-2 h-2 bg-gradient-to-r from-blue-400 to-gray-400 rounded-full opacity-30"
                    style={{
                      left: `${20 + i * 15}%`,
                      top: `${30 + (i % 2) * 20}%`,
                    }}
                    animate={{
                      y: [-20, 20, -20],
                      x: [-10, 10, -10],
                      scale: [1, 1.2, 1],
                    }}
                    transition={{
                      duration: 4 + i,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                  />
                ))}
              </div>
            </motion.div>
          )}

          {/* Messages */}
          <AnimatePresence>
            {messages.map((msg, idx) => (
              <MessageBubble key={idx} message={msg} index={idx} isMobile={isMobile} />
            ))}
          </AnimatePresence>

          {/* Typing indicator */}
          <AnimatePresence>
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex justify-start mb-6"
              >
                <div className="flex items-end gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-transparent flex items-center justify-center text-lg animate-float">
                    <img
                      src="/dr.png"
                      alt="Dr. AI"
                      className="w-full h-full rounded-2xl object-cover"
                    />
                  </div>
                  <div className="bg-white dark:bg-gray-800 px-6 py-4 rounded-2xl rounded-bl-md border border-gray-200 dark:border-gray-700 shadow-md flex items-center gap-3">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <motion.div
                          key={i}
                          className="w-2 h-2 bg-gradient-to-r from-blue-600 to-gray-600 rounded-full"
                          animate={{
                            scale: [1, 1.5, 1],
                            opacity: [0.5, 1, 0.5],
                          }}
                          transition={{
                            duration: 1,
                            repeat: Infinity,
                            delay: i * 0.2,
                          }}
                        />
                      ))}
                    </div>
                    <span className="text-black dark:text-white text-sm">
                      MyDoc AI is thinking...
                    </span>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Floating Input Area */}
      <motion.div
        className="relative z-20 p-2 sm:p-4"
        initial={{ y: 100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <div className="max-w-4xl mx-auto">
          <motion.div
            className="bg-white dark:bg-gray-800 rounded-2xl sm:rounded-3xl p-3 sm:p-6 shadow-2xl border border-gray-200 dark:border-gray-700"
            whileHover={{ scale: isMobile ? 1 : 1.02 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
          >
            <div className="flex items-end gap-2 sm:gap-4">
              {/* Text Input */}
              <div className="flex-1 relative">
                <motion.textarea
                  ref={inputRef}
                  className="w-full p-3 pr-12 sm:p-4 sm:pr-16 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700
                    focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50
                    resize-none text-black dark:text-white bg-transparent
                    placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-300
                    text-sm sm:text-base"
                  placeholder={
                    isListening
                      ? "Listening... 🎤"
                      : interimTranscript
                        ? "Processing speech..."
                        : isMobile
                          ? "Ask about your health... 💬"
                          : "Ask me anything about your health... 💬"
                  }
                  value={interimTranscript || input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      console.log('🟢 Enter key pressed');
                      e.preventDefault();
                      e.stopPropagation();
                      try {
                        handleSend();
                        console.log('🟢 handleSend called from Enter key');
                      } catch (error) {
                        console.error('🔴 Error calling handleSend from Enter key:', error);
                      }
                    }
                  }}
                  rows={1}
                  style={{
                    minHeight: isMobile ? '48px' : '56px',
                    maxHeight: isMobile ? '96px' : '120px',
                    height: 'auto',
                    fontSize: '16px' // Prevents zoom on iOS
                  }}
                  onInput={(e) => {
                    e.target.style.height = 'auto';
                    e.target.style.height = Math.min(e.target.scrollHeight, isMobile ? 96 : 120) + 'px';
                  }}
                  whileFocus={{ scale: isMobile ? 1 : 1.02 }}
                />

                {/* Character count and voice status */}
                <motion.div
                  className="absolute bottom-2 right-12 sm:right-16 text-xs text-gray-400 flex items-center gap-2"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: input.length > 50 || isListening || interimTranscript ? 1 : 0 }}
                >
                  {isListening && (
                    <span className="text-red-500 animate-pulse">🎤 Listening</span>
                  )}
                  {interimTranscript && !isListening && (
                    <span className="text-blue-500">Processing...</span>
                  )}
                  {input.length > 50 && (
                    <span>{input.length}/500</span>
                  )}
                </motion.div>
              </div>

              {/* Send Button */}
              <motion.button
                type="button"
                onClick={(e) => {
                  console.log('🟢 Send button clicked');
                  e.preventDefault();
                  e.stopPropagation();
                  try {
                    handleSend();
                    console.log('🟢 handleSend called from button click');
                  } catch (error) {
                    console.error('🔴 Error calling handleSend from button:', error);
                  }
                }}
                disabled={input.trim() === '' || isTyping}
                className="bg-blue-600 text-white p-3 sm:p-4 rounded-2xl 
                  hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed 
                  transition-all duration-300 shadow-lg disabled:shadow-none relative overflow-hidden
                  mobile-tap-target"
                whileHover={{ scale: input.trim() && !isMobile ? 1.05 : 1 }}
                whileTap={{ scale: 0.95 }}
                title="Send message"
              >
                <motion.div
                  animate={isTyping ? { rotate: 360 } : { rotate: 0 }}
                  transition={{ duration: 1, repeat: isTyping ? Infinity : 0, ease: "linear" }}
                >
                  {isTyping ? (
                    <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  ) : (
                    <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  )}
                </motion.div>

                {/* Ripple effect */}
                {input.trim() !== '' && (
                  <motion.div
                    className="absolute inset-0 bg-white/20 rounded-2xl"
                    initial={{ scale: 0, opacity: 1 }}
                    animate={{ scale: 2, opacity: 0 }}
                    transition={{ duration: 0.6 }}
                  />
                )}
              </motion.button>
            </div>

            {/* Quick suggestions */}
            <AnimatePresence>
              {input === '' && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="flex flex-wrap gap-2 mt-4"
                >
                  {[
                    { text: "What are the symptoms of flu?", emoji: "🤒", short: "Flu symptoms" },
                    { text: "How to reduce stress?", emoji: "😌", short: "Reduce stress" },
                    { text: "Healthy diet tips", emoji: "🥗", short: "Diet tips" },
                    { text: "Exercise recommendations", emoji: "💪", short: "Exercise" },
                    { text: "Sleep improvement tips", emoji: "😴", short: "Sleep tips" },
                    { text: "Mental health support", emoji: "🧠", short: "Mental health" }
                  ].map((suggestion, index) => (
                    <motion.button
                      key={suggestion.text}
                      onClick={() => setInput(suggestion.text)}
                      className="flex items-center gap-2 px-3 py-2 text-sm 
                        bg-gray-50 dark:bg-gray-700 rounded-xl hover:bg-blue-50 dark:hover:bg-blue-900/30
                        text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 
                        border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-600
                        transition-all duration-200 mobile-tap-target"
                      whileHover={{ scale: isMobile ? 1.02 : 1.05, y: isMobile ? 0 : -2 }}
                      whileTap={{ scale: 0.95 }}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <span className="text-base">{suggestion.emoji}</span>
                      <span className="hidden sm:inline font-medium">{suggestion.text}</span>
                      <span className="sm:hidden font-medium">{suggestion.short}</span>
                    </motion.button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Chat controls */}
            <motion.div
              className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                <span>💡</span>
                <span className="hidden sm:inline">
                  Press Enter to send, Shift+Enter for new line
                  {speechSupported && " • Click 🎤 for voice input"}
                </span>
                <span className="sm:hidden text-xs">
                  Enter to send{speechSupported && " • 🎤 for voice"}
                </span>
                {speechError && (
                  <span className="text-red-500 text-xs ml-2">
                    Voice error: {speechError.message}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                <motion.button
                  onClick={() => setSettingsOpen(true)}
                  className="flex items-center gap-2 px-3 py-2 text-xs 
                    bg-gray-50 dark:bg-gray-700 rounded-xl text-gray-600 dark:text-gray-300 
                    hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30
                    border border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-600
                    transition-all duration-200 mobile-tap-target"
                  whileHover={{ scale: isMobile ? 1.02 : 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <FiSettings size={14} />
                  <span className="hidden sm:inline font-medium">Settings</span>
                </motion.button>

                <motion.button
                  onClick={clearChat}
                  className="flex items-center gap-2 px-3 py-2 text-xs 
                    bg-gray-50 dark:bg-gray-700 rounded-xl text-gray-600 dark:text-gray-300 
                    hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30
                    border border-gray-200 dark:border-gray-600 hover:border-red-300 dark:hover:border-red-600
                    transition-all duration-200 mobile-tap-target"
                  whileHover={{ scale: isMobile ? 1.02 : 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <span>🗑️</span>
                  <span className="hidden sm:inline font-medium">Clear Chat</span>
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>

      {/* Settings Modal */}
      <ChatSettings
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />



      {/* Voice Command Handler */}
      <VoiceCommandHandler
        onClearChat={clearChat}
        onNewConversation={clearChat}
        onRepeatMessage={repeatLastMessage}
        onToggleVoice={setVoiceEnabled}
        onShowHelp={() => console.log('Voice help requested')}
        lastMessage={lastAiMessage}
      />
    </main>
  );
}