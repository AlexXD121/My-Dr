import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence, PanInfo } from 'framer-motion';
import { useSwipeGestures } from '../hooks/useSwipeGestures';

const MobileChatInterface = ({ messages, onSendMessage, isTyping }) => {
  const [input, setInput] = useState('');
  const [showQuickActions, setShowQuickActions] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const quickActions = [
    { text: 'I have a headache', emoji: '🤕' },
    { text: 'Feeling tired', emoji: '😴' },
    { text: 'Stomach pain', emoji: '🤢' },
    { text: 'Need medication info', emoji: '💊' }
  ];

  const swipeGestures = useSwipeGestures(
    () => setShowQuickActions(false), // swipe left to hide
    () => setShowQuickActions(true),  // swipe right to show
    50
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (input.trim()) {
      onSendMessage(input.trim());
      setInput('');
      inputRef.current?.focus();
    }
  };

  const handleQuickAction = (text) => {
    setInput(text);
    setShowQuickActions(false);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-full bg-gray-50 dark:bg-gray-900">
      {/* Messages Area */}
      <div 
        className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
        {...swipeGestures}
      >
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -20, scale: 0.95 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] p-3 rounded-2xl shadow-sm ${
                  message.sender === 'user'
                    ? 'bg-blue-600 text-white rounded-br-md'
                    : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-bl-md'
                }`}
              >
                <p className="text-sm leading-relaxed">{message.text}</p>
                <p className="text-xs opacity-70 mt-1">
                  {new Date(message.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing Indicator */}
        <AnimatePresence>
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex justify-start"
            >
              <div className="bg-white dark:bg-gray-800 p-3 rounded-2xl rounded-bl-md shadow-sm">
                <div className="flex space-x-1">
                  {[0, 1, 2].map((i) => (
                    <motion.div
                      key={i}
                      className="w-2 h-2 bg-gray-400 rounded-full"
                      animate={{
                        scale: [1, 1.2, 1],
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
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions Panel */}
      <AnimatePresence>
        {showQuickActions && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            className="px-4 py-2 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
          >
            <div className="flex space-x-2 overflow-x-auto pb-2">
              {quickActions.map((action, index) => (
                <motion.button
                  key={index}
                  onClick={() => handleQuickAction(action.text)}
                  className="flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 
                    rounded-full whitespace-nowrap text-sm hover:bg-gray-200 dark:hover:bg-gray-600
                    transition-colors duration-200"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <span>{action.emoji}</span>
                  <span>{action.text}</span>
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Area */}
      <div className="p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-end space-x-2">
          {/* Quick Actions Toggle */}
          <motion.button
            onClick={() => setShowQuickActions(!showQuickActions)}
            className="p-2 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300
              hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
            </svg>
          </motion.button>

          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Type your message..."
              className="w-full p-3 pr-12 rounded-2xl bg-gray-100 dark:bg-gray-700 
                border-none resize-none focus:outline-none focus:ring-2 focus:ring-blue-500
                text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400
                text-base" // 16px to prevent zoom on iOS
              rows={1}
              style={{
                minHeight: '48px',
                maxHeight: '120px',
                fontSize: '16px'
              }}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
              }}
            />
            
            {/* Character count */}
            {input.length > 100 && (
              <div className="absolute bottom-2 right-12 text-xs text-gray-400">
                {input.length}/500
              </div>
            )}
          </div>

          {/* Send Button */}
          <motion.button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className="p-3 rounded-full bg-blue-600 text-white disabled:opacity-50 
              disabled:cursor-not-allowed shadow-lg"
            whileHover={{ scale: input.trim() ? 1.1 : 1 }}
            whileTap={{ scale: 0.9 }}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </motion.button>
        </div>

        {/* Input hints */}
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
          <span>💡 Swipe right for quick actions</span>
          <span>Enter to send</span>
        </div>
      </div>
    </div>
  );
};

export default MobileChatInterface;